output "public_ip" {
  value = aws_instance.attendance.public_ip
}

output "app_url" {
  value = "http://${aws_instance.attendance.public_ip}:${var.app_port}"
}

output "private_key_path" {
  value = local_file.attendance_private_key.filename
}
