#!/bin/bash
# Saaransh Local LLM Production Deployment Script
# Usage: ./deploy-production.sh [domain-name]

set -e

DOMAIN=${1:-"your-domain.com"}
APP_DIR="/opt/saaransh"
BACKUP_DIR="/opt/backups"

echo "🚀 Starting Saaransh Local LLM Production Deployment..."
echo "📍 Domain: $DOMAIN"

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ]; then
    echo "❌ Please run as ubuntu user"
    exit 1
fi

# 1. System Update
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Install Dependencies
echo "🔧 Installing dependencies..."
sudo apt install -y curl wget git python3 python3-pip python3-venv \
    nginx certbot python3-certbot-nginx htop iotop jq awscli

# 3. Install uv (Python package manager)
echo "🐍 Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# 4. Install Ollama
echo "🤖 Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# 5. Configure Ollama Security
echo "🔒 Configuring Ollama security..."
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_ORIGINS=http://localhost,http://127.0.0.1"
Environment="OLLAMA_NUM_PARALLEL=2"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
User=ubuntu
Group=ubuntu
EOF

sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

# Wait for Ollama to start
sleep 5

# 6. Download Model
echo "📥 Downloading Llama model..."
if ! ollama list | grep -q "llama3.1:8b"; then
    ollama pull llama3.1:8b
fi

# 7. Setup Application Directory
echo "🏗️ Setting up application directory..."
sudo mkdir -p $APP_DIR $BACKUP_DIR
sudo chown ubuntu:ubuntu $APP_DIR $BACKUP_DIR

# 8. Configure Firewall
echo "🛡️ Configuring firewall..."
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw deny 11434

# 9. Setup Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/saaransh << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL configuration will be added by certbot
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Block debug endpoints in production
        location /debug {
            deny all;
            return 404;
        }
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/saaransh /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

# 10. Create Saaransh service
echo "⚙️ Creating Saaransh systemd service..."
sudo tee /etc/systemd/system/saaransh.service << EOF
[Unit]
Description=Saaransh Backend Service
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$APP_DIR/saaransh_backend
Environment=PATH=$APP_DIR/saaransh_backend/.venv/bin
ExecStart=$APP_DIR/saaransh_backend/.venv/bin/python serve.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# 11. Create monitoring script
echo "📊 Setting up monitoring..."
tee $APP_DIR/monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/saaransh-monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check services
for service in ollama saaransh nginx; do
    if ! systemctl is-active --quiet $service; then
        echo "$DATE ALERT: $service is down" >> $LOG_FILE
        sudo systemctl restart $service
    fi
done

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$DATE ALERT: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check Ollama model
if ! curl -s http://localhost:11434/api/tags | grep -q "llama3.1:8b"; then
    echo "$DATE ALERT: Llama model not available" >> $LOG_FILE
fi
EOF

chmod +x $APP_DIR/monitor.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/monitor.sh") | crontab -

# 12. Create backup script
echo "💾 Setting up backup system..."
tee $APP_DIR/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup application
tar -czf $BACKUP_DIR/saaransh-$DATE.tar.gz /opt/saaransh/saaransh_backend

# Clean old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x $APP_DIR/backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh >> /var/log/saaransh-backup.log 2>&1") | crontab -

echo ""
echo "✅ Deployment infrastructure completed!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your Saaransh application to: $APP_DIR/saaransh_backend"
echo "2. Configure environment: $APP_DIR/saaransh_backend/.env.production"
echo "3. Install Python dependencies: cd $APP_DIR/saaransh_backend && uv sync"
echo "4. Start Saaransh service: sudo systemctl enable saaransh && sudo systemctl start saaransh"
echo "5. Get SSL certificate: sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "🔍 Verify deployment:"
echo "- Check services: sudo systemctl status ollama saaransh nginx"
echo "- Test Ollama: curl -s http://localhost:11434/api/tags"
echo "- Check firewall: sudo ufw status"
echo ""
echo "🔒 Security verification:"
echo "- Ollama localhost only: sudo netstat -tlnp | grep 11434"
echo "- External access blocked: nmap -p 11434 \$(curl -s ifconfig.me)"
echo ""
echo "🚀 Your Saaransh Local LLM deployment is ready!"