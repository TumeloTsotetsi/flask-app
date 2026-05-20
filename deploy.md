# CyberDiary — VPS Deployment Guide

## 1. Upload your files to the VPS
```bash
scp -r cyberblog/ user@your-vps-ip:/var/www/cyberdiary
```

## 2. SSH into your VPS and install dependencies
```bash
ssh user@your-vps-ip
cd /var/www/cyberdiary
pip install -r requirements.txt
```

## 3. Set a strong secret key
```bash
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```
To make it permanent, add it to `/etc/environment` or your systemd service file.

## 4. Run once to create the database
```bash
python app.py
# Ctrl+C after the DB is created
```
This creates `cyberdiary.db` with all seed data and prints your admin credentials.

## 5. Run with Gunicorn (production)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 6. Nginx reverse proxy (recommended)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 7. Run as a systemd service (so it restarts automatically)
Create `/etc/systemd/system/cyberdiary.service`:
```ini
[Unit]
Description=CyberDiary Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/cyberdiary
Environment="SECRET_KEY=your-secret-key-here"
Environment="FLASK_ENV=production"
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable cyberdiary
sudo systemctl start cyberdiary
sudo systemctl status cyberdiary
```

## Admin panel
Visit: `http://yourdomain.com/admin`
Default login: `admin` / `cyberdiary2026`
**Change the password immediately at `/admin/settings`!**
