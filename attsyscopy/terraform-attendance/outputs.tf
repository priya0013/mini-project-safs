output "server_public_ip" {
  value = module.attendance_server.public_ip
}

output "app_url" {
  value = module.attendance_server.app_url
}

output "backend_api_url" {
  value       = module.attendance_server.backend_api_url
  description = "Public backend API base URL"
}

output "private_key_path" {
  value       = module.attendance_server.private_key_path
  description = "Path to generated private key PEM file"
}

output "key_pair_name" {
  value       = module.attendance_server.key_pair_name
  description = "Generated AWS key pair name"
}
