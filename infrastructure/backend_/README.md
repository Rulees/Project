# ☁️ Terraform Backend Setup

Этот модуль создаёт **backend** для хранения состояния Terraform в Object Storage Yandex.Cloud.

> **ВАЖНО:** Backend должен быть создан **вручную один раз до запуска любого `terragrunt apply`**, иначе `terragrunt` не сможет инициализироваться.

---

## ⚠️ Правила

- CI/CD не создаёт backend!
- После создания — он **больше не трогается**
- Все окружения (`dev`, `prod`, и т.д.) используют этот backend для хранения `tfstate`

---