resource "yandex_dns_recordset" "external_ip_dns" {
  count   = var.dns != null ? 1 : 0

  zone_id = var.dns.zone_id
  name    = var.dns.name
  ttl     = var.dns.ttl
  type    = var.dns.type
  data    = [module.yc-ec2.external_ip[0]]
}