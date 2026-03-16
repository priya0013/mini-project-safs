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

  ingress {
    from_port   = 80
    to_port     = 80
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
  key_name_prefix = "${var.key_name}-"
  public_key      = tls_private_key.attendance.public_key_openssh
}

resource "local_file" "attendance_private_key" {
  content  = tls_private_key.attendance.private_key_pem
  filename = "${path.root}/${aws_key_pair.attendance.key_name}.pem"
}

resource "aws_instance" "attendance" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.attendance.key_name
  vpc_security_group_ids      = [aws_security_group.attendance_sg.id]
  associate_public_ip_address = true
  user_data_replace_on_change = true

  user_data = trimspace(<<-EOF
              #!/bin/bash
              set -euxo pipefail

              exec > >(tee /var/log/attendance-bootstrap.log | logger -t attendance-bootstrap -s 2>/dev/console) 2>&1
              export DEBIAN_FRONTEND=noninteractive

              if ! swapon --show | grep -q '/swapfile'; then
                fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
                chmod 600 /swapfile
                mkswap /swapfile
                swapon /swapfile
                grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
              fi

              apt-get update -y
              apt-get install -y python3-pip python3-venv git curl ca-certificates gnupg nginx docker.io build-essential
              systemctl enable --now docker

              curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
              apt-get install -y nodejs

              cd /home/ubuntu
              rm -rf mini-project-safs
              git clone ${var.repo_url} mini-project-safs
              chown -R ubuntu:ubuntu /home/ubuntu/mini-project-safs

              REPO_ROOT="/home/ubuntu/mini-project-safs/attsyscopy/Attendance-Management-system-using-face-recognition-master"
              BACKEND_DIR="$REPO_ROOT/backend"
              FRONTEND_DIR="$REPO_ROOT/frontend"

                find "$FRONTEND_DIR/app" -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \) -exec sed -i 's#http://127.0.0.1:5000##g; s#http://localhost:5000##g' {} +

          python3 - "$FRONTEND_DIR" "$BACKEND_DIR" <<'PY'
          from pathlib import Path
          import sys

          frontend_dir = Path(sys.argv[1])
          backend_dir = Path(sys.argv[2])

          frontend_dir.joinpath("next.config.ts").write_text('''import type { NextConfig } from "next";

          const nextConfig: NextConfig = {
            eslint: {
            ignoreDuringBuilds: true,
            },
            typescript: {
            ignoreBuildErrors: true,
            },
          };

          export default nextConfig;
          ''', encoding="utf-8")

          backend_dir.joinpath("app.py").write_text('''import logging
          import os
          import threading
          import time

          import numpy as np
          from dotenv import load_dotenv
          from flask import Flask
          from flask_bcrypt import Bcrypt
          from flask_cors import CORS
          from pymongo import MongoClient

          from auth.routes import auth_bp, bcrypt as auth_bcrypt

          try:
            from student.registration import student_registration_bp
          except ImportError:
            student_registration_bp = None

          try:
            from student.updatedetails import student_update_bp
          except ImportError:
            student_update_bp = None

          try:
            from student.demo_session import demo_session_bp
          except ImportError:
            demo_session_bp = None

          try:
            from student.view_attendance import attendance_bp
          except ImportError:
            attendance_bp = None

          try:
            from teacher.attendance_records import attendance_session_bp
          except ImportError:
            attendance_session_bp = None

          logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
          logger = logging.getLogger(__name__)

          load_dotenv()

          ENABLE_FACE_MODELS = os.getenv("ENABLE_FACE_MODELS", "false").lower() == "true"
          MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
          DB_NAME = os.getenv("DATABASE_NAME", "facerecognition")
          COLLECTION_NAME = os.getenv("COLLECTION_NAME", "students")
          THRESHOLD = float(os.getenv("THRESHOLD", "0.6"))

          client = MongoClient(MONGODB_URI)
          db = client[DB_NAME]
          students_collection = db[COLLECTION_NAME]
          attendance_db = client["facerecognition_db"]
          attendance_collection = attendance_db["attendance_records"]


          class ModelManager:
            _instance = None
            _lock = threading.Lock()

            def __new__(cls):
              if cls._instance is None:
                with cls._lock:
                  if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize_models()
              return cls._instance

            def _initialize_models(self):
              logger.info("Starting model initialization")
              start_time = time.time()

              self.models_ready = False
              self.detector = None
              self.deepface_ready = False

              from mtcnn import MTCNN
              from deepface import DeepFace

              self.detector = MTCNN()
              dummy_img = np.zeros((160, 160, 3), dtype=np.uint8)
              DeepFace.represent(dummy_img, model_name="Facenet512", detector_backend="skip", enforce_detection=False)

              dummy_img_2 = np.ones((224, 224, 3), dtype=np.uint8) * 128
              DeepFace.represent(dummy_img_2, model_name="Facenet512", detector_backend="skip", enforce_detection=False)

              self.deepface_ready = True
              self.models_ready = True
              logger.info("Models initialized in %.2f seconds", time.time() - start_time)

            def get_detector(self):
              if not self.models_ready:
                raise RuntimeError("Models not properly initialized")
              return self.detector

            def is_ready(self):
              return self.models_ready and self.deepface_ready

            def health_check(self):
              try:
                if not self.models_ready:
                  return False

                test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
                self.detector.detect_faces(test_img)

                from deepface import DeepFace

                test_face = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
                DeepFace.represent(test_face, model_name="Facenet512", detector_backend="skip", enforce_detection=False)
                return True
              except Exception as error:
                logger.error("Model health check failed: %s", error)
                return False


          model_manager = None
          if ENABLE_FACE_MODELS:
            logger.info("Initializing model manager")
            try:
              model_manager = ModelManager()
            except Exception as error:
              logger.error("Model manager initialization failed: %s", error)
              model_manager = None
          else:
            logger.info("Face-recognition model initialization is disabled")

          app = Flask(__name__)
          CORS(app)

          app.config["DB"] = db
          app.config["COLLECTION_NAME"] = COLLECTION_NAME
          app.config["THRESHOLD"] = THRESHOLD
          app.config["ATTENDANCE_COLLECTION"] = attendance_collection
          app.config["MODEL_MANAGER"] = model_manager
          app.config["MTCNN_DETECTOR"] = model_manager.get_detector() if model_manager else None

          bcrypt = Bcrypt(app)
          auth_bcrypt.init_app(app)


          @app.route("/health", methods=["GET"])
          @app.route("/api/health", methods=["GET"])
          def health_check():
            model_status = model_manager.is_ready() if model_manager else False
            model_health = model_manager.health_check() if model_manager else False
            return {
              "status": "healthy" if (not ENABLE_FACE_MODELS or (model_status and model_health)) else "unhealthy",
              "face_models_enabled": ENABLE_FACE_MODELS,
              "models_ready": model_status,
              "models_healthy": model_health,
              "timestamp": time.time(),
            }


          app.register_blueprint(auth_bp)

          if student_registration_bp:
            app.register_blueprint(student_registration_bp)
          if student_update_bp:
            app.register_blueprint(student_update_bp)
          if demo_session_bp:
            app.register_blueprint(demo_session_bp)
          if attendance_bp:
            app.register_blueprint(attendance_bp)
          if attendance_session_bp:
            app.register_blueprint(attendance_session_bp)

          if __name__ == "__main__":
            if ENABLE_FACE_MODELS and (not model_manager or not model_manager.is_ready()):
              raise SystemExit("Cannot start server because the models are not ready")

            logger.info("Starting Flask server on http://0.0.0.0:5000")
            app.run(host="0.0.0.0", port=5000, debug=False)
          ''', encoding="utf-8")
          PY

              docker rm -f attendance-mongo || true
              docker pull mongo:7
              docker run -d --name attendance-mongo --restart unless-stopped -p 27017:27017 mongo:7

              python3 -m venv /opt/attendance-api-venv
              /opt/attendance-api-venv/bin/pip install --upgrade pip
              /opt/attendance-api-venv/bin/pip install flask flask-cors pymongo python-dotenv flask-bcrypt numpy

          python3 - <<'PY'
          from pathlib import Path

          Path("/etc/systemd/system/attendance-api.service").write_text("""[Unit]
          Description=Attendance Backend API
          After=network.target docker.service
          Requires=docker.service

          [Service]
          Type=simple
          User=ubuntu
          WorkingDirectory=/home/ubuntu/mini-project-safs/attsyscopy/Attendance-Management-system-using-face-recognition-master/backend
          Environment=PYTHONUNBUFFERED=1
          Environment=ENABLE_FACE_MODELS=false
          Environment=MONGODB_URI=mongodb://127.0.0.1:27017/
          ExecStart=/opt/attendance-api-venv/bin/python /home/ubuntu/mini-project-safs/attsyscopy/Attendance-Management-system-using-face-recognition-master/backend/app.py
          Restart=always
          RestartSec=5

          [Install]
          WantedBy=multi-user.target
          """, encoding="utf-8")

          Path("/etc/systemd/system/attendance-frontend.service").write_text("""[Unit]
          Description=Attendance Next.js Frontend
          After=network.target attendance-api.service

          [Service]
          Type=simple
          User=ubuntu
          WorkingDirectory=/home/ubuntu/mini-project-safs/attsyscopy/Attendance-Management-system-using-face-recognition-master/frontend
          Environment=NODE_ENV=production
          Environment=PYTHONUNBUFFERED=1
          ExecStart=/usr/bin/npm run start -- --hostname 127.0.0.1 --port 3000
          Restart=always
          RestartSec=5

          [Install]
          WantedBy=multi-user.target
          """, encoding="utf-8")

          Path("/etc/nginx/sites-available/attendance").write_text("""server {
            listen 80 default_server;
            listen [::]:80 default_server;
            server_name _;

            location /api/ {
              proxy_pass http://127.0.0.1:5000/api/;
              proxy_http_version 1.1;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
            }

            location / {
              proxy_pass http://127.0.0.1:3000;
              proxy_http_version 1.1;
              proxy_set_header Upgrade $http_upgrade;
              proxy_set_header Connection \"upgrade\";
              proxy_set_header Host $host;
              proxy_cache_bypass $http_upgrade;
            }
          }
          """, encoding="utf-8")
          PY

              rm -f /etc/nginx/sites-enabled/default
              ln -sf /etc/nginx/sites-available/attendance /etc/nginx/sites-enabled/attendance

              sudo -u ubuntu -H bash -lc "cd '$FRONTEND_DIR' && npm ci && NODE_OPTIONS=--max-old-space-size=512 npm run build"

              systemctl daemon-reload
              systemctl enable attendance-api
              systemctl restart attendance-api
              systemctl enable attendance-frontend
              systemctl restart attendance-frontend
              systemctl enable nginx
              systemctl restart nginx
              EOF
  )

  tags = {
    Name = var.instance_name
  }
}
