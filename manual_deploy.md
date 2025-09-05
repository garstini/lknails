# Manual VPS Deployment Guide

## Step 1: Create deployment package locally
```bash
# Create a tar archive of the project
cd /Users/copv/Data/code/nails_salon
tar -czf nails_salon.tar.gz \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='env' \
    --exclude='db.sqlite3' \
    --exclude='deploy_package' \
    .
```

## Step 2: Copy to VPS manually
```bash
# You need to manually upload nails_salon.tar.gz to your VPS
# Use SCP or SFTP client to upload the file
```

## Step 3: Run these commands on VPS (SSH into root@142.171.70.173)

### Install system dependencies
```bash
apt update
apt install -y python3 python3-pip python3-venv nginx supervisor
```

### Setup project directory
```bash
mkdir -p /var/www/nails_salon
cd /var/www/nails_salon

# Extract your uploaded tar file here
tar -xzf /path/to/uploaded/nails_salon.tar.gz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Configure Django settings
```bash
# Copy production settings
cp production_settings.py /var/www/nails_salon/
export DJANGO_SETTINGS_MODULE=production_settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser --email admin@lknails.de --username admin

# Collect static files
python manage.py collectstatic --noinput

# Compile messages
python manage.py compilemessages
```

### Setup Nginx
```bash
# Create Nginx config
cat > /etc/nginx/sites-available/nails_salon << 'EOF'
server {
    listen 80;
    server_name 142.171.70.173 lknailslashes.de www.lknailslashes.de;

    location /static/ {
        alias /var/www/nails_salon/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /var/www/nails_salon/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/nails_salon /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t
```

### Setup Supervisor for Gunicorn
```bash
# Create supervisor config
cat > /etc/supervisor/conf.d/nails_salon.conf << 'EOF'
[program:nails_salon]
command=/var/www/nails_salon/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 nails_salon_project.wsgi:application
directory=/var/www/nails_salon
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/nails_salon/logs/gunicorn.log
environment=DJANGO_SETTINGS_MODULE=production_settings
EOF

# Create logs directory
mkdir -p /var/www/nails_salon/logs

# Set permissions
chown -R www-data:www-data /var/www/nails_salon
chmod -R 755 /var/www/nails_salon
```

### Start services
```bash
# Start supervisor and nginx
supervisorctl reread
supervisorctl update
supervisorctl start nails_salon
systemctl restart nginx

# Check status
supervisorctl status nails_salon
systemctl status nginx
```

## Step 4: Access your site
- Main site: http://142.171.70.173
- Admin panel: http://142.171.70.173/admin
- Use the admin credentials you created in step 3

## Troubleshooting
```bash
# Check gunicorn logs
tail -f /var/www/nails_salon/logs/gunicorn.log

# Check nginx logs  
tail -f /var/log/nginx/error.log

# Restart services if needed
supervisorctl restart nails_salon
systemctl restart nginx
```