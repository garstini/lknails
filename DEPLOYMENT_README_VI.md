# Hướng dẫn triển khai Django cho lknailslashes.de

## Thông tin server
- **Domain**: lknailslashes.de
- **IP**: 142.171.70.173
- **Project**: Bella Nails & Lashes (Django)

## 🚀 Triển khai nhanh

### 1. Chuẩn bị gói deployment
```bash
# Trên máy local
./package_for_deployment.sh
```

### 2. Upload lên server
```bash
# Sử dụng SCP hoặc SFTP
scp nails_salon_deployment_*.tar.gz root@142.171.70.173:/tmp/

# Hoặc sử dụng rsync
rsync -avz nails_salon_deployment_*.tar.gz root@142.171.70.173:/tmp/
```

### 3. Triển khai trên server
```bash
# SSH vào server
ssh root@142.171.70.173

# Extract package
cd /tmp
tar -xzf nails_salon_deployment_*.tar.gz
cd nails_salon_deployment_*

# Chạy script triển khai hoàn chỉnh
chmod +x complete_deploy.sh
./complete_deploy.sh
```

### 4. Thiết lập HTTPS (Let's Encrypt miễn phí)
```bash
# Sau khi triển khai cơ bản thành công
chmod +x setup_https.sh
./setup_https.sh
```

## 📋 Cấu hình systemd service

File service đã được tạo tự động tại `/etc/systemd/system/nails_salon.service`:

```ini
[Unit]
Description=LK Nails & Lashes Django Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
RuntimeDirectory=nails_salon
WorkingDirectory=/var/www/nails_salon
Environment=DJANGO_SETTINGS_MODULE=production_settings
ExecStart=/var/www/nails_salon/venv/bin/gunicorn --workers 3 --bind unix:/run/nails_salon/nails_salon.sock nails_salon_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### Quản lý service
```bash
# Khởi động service
sudo systemctl start nails_salon

# Dừng service
sudo systemctl stop nails_salon

# Restart service
sudo systemctl restart nails_salon

# Kiểm tra trạng thái
sudo systemctl status nails_salon

# Xem logs
sudo journalctl -u nails_salon -f

# Enable tự động khởi động
sudo systemctl enable nails_salon
```

## 🔒 Cấu hình HTTPS

Script `setup_https.sh` sẽ tự động:

1. **Cài đặt Certbot** từ snapd
2. **Tạo SSL certificate** cho lknailslashes.de và www.lknailslashes.de
3. **Cấu hình Nginx** với HTTPS redirect
4. **Thiết lập auto-renewal** cho certificate
5. **Cập nhật Django settings** cho HTTPS

### Cấu hình Nginx với HTTPS

File `/etc/nginx/sites-available/nails_salon` sẽ có:
- HTTP redirect to HTTPS
- SSL configuration với TLS 1.2/1.3
- Security headers
- Gzip compression
- Static file serving

## 🛠️ Các lệnh hữu ích

### Django management
```bash
cd /var/www/nails_salon
source venv/bin/activate

# Tạo superuser
python manage.py createsuperuser

# Chạy migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Django shell
python manage.py shell
```

### Kiểm tra logs
```bash
# Django application logs
sudo journalctl -u nails_salon -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Django logs (nếu có cấu hình file logging)
sudo tail -f /var/www/nails_salon/logs/django.log
```

### Backup và restore
```bash
# Backup database
cd /var/www/nails_salon
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Backup media files
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

## 🔧 Troubleshooting

### Nếu Django service không khởi động
```bash
# Kiểm tra logs
sudo journalctl -u nails_salon -n 50

# Kiểm tra permissions
sudo chown -R www-data:www-data /var/www/nails_salon
sudo chown -R www-data:www-data /run/nails_salon

# Test Django
cd /var/www/nails_salon
source venv/bin/activate
python manage.py check
```

### Nếu Nginx có lỗi
```bash
# Test cấu hình
sudo nginx -t

# Kiểm tra syntax
sudo nginx -T

# Restart Nginx
sudo systemctl restart nginx
```

### Nếu SSL không hoạt động
```bash
# Kiểm tra certificate
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run

# Kiểm tra DNS
dig lknailslashes.de
nslookup lknailslashes.de
```

## 📱 Các URL quan trọng

Sau khi triển khai thành công:

- **Website**: https://lknailslashes.de
- **Admin panel**: https://lknailslashes.de/admin/
- **Static files**: https://lknailslashes.de/static/
- **Media files**: https://lknailslashes.de/media/

## 🎯 Tính năng chính

- ✅ Responsive design
- ✅ Booking system với calendar
- ✅ User authentication
- ✅ Admin dashboard
- ✅ Email notifications
- ✅ Image gallery
- ✅ Blog system
- ✅ SEO optimized
- ✅ HTTPS enabled
- ✅ Systemd service
- ✅ Auto-renewal SSL

## 📞 Hỗ trợ

Nếu gặp vấn đề trong quá trình triển khai, hãy kiểm tra logs và đảm bảo:

1. DNS đã trỏ đúng về IP 142.171.70.173
2. Port 80 và 443 đã được mở
3. Tất cả dependencies đã được cài đặt
4. Permissions đã được set đúng cho www-data user
