# bot_scripts/db.py

import aiosqlite
import os
from datetime import datetime, timedelta
DB_NAME = os.getenv("DB_NAME", "bookings.db")

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT,
                date TEXT,
                time TEXT,
                duration INTEGER DEFAULT 2,
                table_number INTEGER,
                guest_count INTEGER,
                guest_name TEXT,
                comment TEXT,
                review_notification_sent INTEGER DEFAULT 0,
                by_admin INTEGER DEFAULT 0,
                chat_id INTEGER
            )
        """)
        await db.commit()

async def save_booking(date, time, guest_count, table_number, phone_number, guest_name, comment, duration, by_admin=0):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO bookings (date, time, guest_count, table_number, phone_number, guest_name, comment, duration, by_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (date, time, guest_count, table_number, phone_number, guest_name, comment, duration, by_admin))
        await db.commit()

_cached_tables = {}
_cached_at = {}

async def get_booked_tables(date: str, time: str):
    now = datetime.now()
    key = (date, time)

    # Очистка кэша старше 60 секунд
    for k in list(_cached_at):
        if (now - _cached_at[k]).total_seconds() > 60:
            _cached_tables.pop(k, None)
            _cached_at.pop(k, None)

    # Возвращаем из кэша, если есть
    if key in _cached_tables:
        return _cached_tables[key]

    # Иначе читаем из базы
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT table_number, time, duration FROM bookings WHERE date=?
        """, (date,))
        rows = await cursor.fetchall()

    requested_start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    requested_end = requested_start + timedelta(hours=2)

    occupied = set()
    for table_num, booked_time, duration in rows:
        booked_start = datetime.strptime(f"{date} {booked_time}", "%Y-%m-%d %H:%M")
        booked_end = booked_start + timedelta(hours=duration)

        if booked_start < requested_end and requested_start < booked_end:
            occupied.add(table_num)

    _cached_tables[key] = occupied
    _cached_at[key] = now
    return occupied

async def db_fetchall(query: str, params: tuple = ()):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query, params)
        return await cursor.fetchall()

async def db_execute(query: str, params: tuple = ()):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(query, params)
        await db.commit()