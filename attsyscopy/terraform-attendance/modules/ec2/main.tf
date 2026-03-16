data "aws_vpc" "default" {
  default = true
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "attendance_sg" {
  name        = "attendance-sg"
  description = "Security group for automated attendance deployment"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_cidr_blocks
  }

  ingress {
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.instance_name}-sg"
  }
}

resource "tls_private_key" "attendance" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "attendance" {
  key_name   = var.key_name
  public_key = tls_private_key.attendance.public_key_openssh
}

resource "local_file" "attendance_private_key" {
  content         = tls_private_key.attendance.private_key_pem
  filename        = "${path.root}/${var.key_name}.pem"
  file_permission = "0400"
}

resource "aws_instance" "attendance" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.attendance.key_name
  vpc_security_group_ids      = [aws_security_group.attendance_sg.id]
  associate_public_ip_address = true

  user_data = <<-EOF
              #!/bin/bash
              set -euxo pipefail

              apt-get update -y
              apt-get install -y python3-pip git

              cd /home/ubuntu
              rm -rf mini-project-safs
              git clone ${var.repo_url} mini-project-safs
              chown -R ubuntu:ubuntu /home/ubuntu/mini-project-safs

              cd /home/ubuntu/mini-project-safs
              pip3 install --upgrade pip
              pip3 install flask flask-cors pymongo

              cat >/etc/systemd/system/attendance.service <<'SERVICE'
              [Unit]
              Description=Attendance Flask API
              After=network.target

              [Service]
              Type=simple
              User=ubuntu
              WorkingDirectory=/home/ubuntu/mini-project-safs
              ExecStart=/usr/bin/python3 /home/ubuntu/mini-project-safs/app.py
              Restart=always
              RestartSec=5
              Environment=PYTHONUNBUFFERED=1

              [Install]
              WantedBy=multi-user.target
              SERVICE

              systemctl daemon-reload
              systemctl enable attendance
              systemctl restart attendance
              EOF

  tags = {
    Name = var.instance_name
  }
}
