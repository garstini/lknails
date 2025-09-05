# Cấu hình HTTPS với SSL Certificate

## Phương pháp 1: Sử dụng Certbot (Let's Encrypt - Miễn phí)

### Bước 1: Cài đặt Certbot trên VPS

```bash
# Update system
apt update

# Install snapd
apt install snapd -y

# Install certbot via snap
snap install core; snap refresh core
snap install --classic certbot

# Create symlink
ln -s /snap/bin/certbot /usr/bin/certbot
```

### Bước 2: Tạo SSL Certificate

```bash
# Tạo certificate cho domain
certbot --nginx -d lknailslashes.de -d www.lknailslashes.de

# Hoặc nếu chỉ có IP
certbot --nginx -d 142.171.70.173

# Certbot sẽ tự động:
# - Tạo SSL certificate
# - Cập nhật nginx config
# - Setup auto-renewal
```

### Bước 3: Verify SSL đã hoạt động

```bash
# Check certificate
certbot certificates

# Test renewal
certbot renew --dry-run
```

## Phương pháp 2: Manual Nginx SSL Config

Nếu bạn có SSL certificate từ nhà cung cấp khác:

### Bước 1: Update Nginx Config với SSL

```bash
# Tạo file config mới
cat > /etc/nginx/sites-available/nails_salon << 'EOF'
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name 142.171.70.173 lknailslashes.de www.lknailslashes.de;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name 142.171.70.173 lknailslashes.de www.lknailslashes.de;

    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Static files
    location /static/ {
        alias /var/www/nails_salon/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Media files  
    location /media/ {
        alias /var/www/nails_salon/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Django app
    location / {
        proxy_pass http://unix:/run/nails_salon/nails_salon.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $server_name;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
}
EOF

# Test nginx config
nginx -t

# Restart nginx
systemctl restart nginx
```

## Bước 2: Update Django Settings cho HTTPS

```bash
# Edit production settings
cat >> /var/www/nails_salon/production_settings.py << 'EOF'

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Trusted origins for HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://142.171.70.173',
    'https://lknailslashes.de',
    'https://www.lknailslashes.de',
]
EOF

# Restart Django service
systemctl restart nails_salon.service
```

## Phương pháp 3: Sử dụng Cloudflare (Đơn giản nhất)

### Bước 1: Setup Cloudflare
1. Tạo tài khoản Cloudflare
2. Thêm domain `lknailslashes.de` 
3. Thay đổi nameserver theo hướng dẫn Cloudflare
4. Trong Cloudflare Dashboard:
   - SSL/TLS → Overview → Set to "Full (strict)"
   - SSL/TLS → Edge Certificates → Enable "Always Use HTTPS"

### Bước 2: Nginx Config cho Cloudflare

```bash
cat > /etc/nginx/sites-available/nails_salon << 'EOF'
server {
    listen 80;
    server_name 142.171.70.173 lknailslashes.de www.lknailslashes.de;

    # Real IP from Cloudflare
    real_ip_header CF-Connecting-IP;
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    set_real_ip_from 141.101.64.0/18;
    set_real_ip_from 108.162.192.0/18;
    set_real_ip_from 190.93.240.0/20;
    set_real_ip_from 188.114.96.0/20;
    set_real_ip_from 197.234.240.0/22;
    set_real_ip_from 198.41.128.0/17;
    set_real_ip_from 162.158.0.0/15;
    set_real_ip_from 104.16.0.0/13;
    set_real_ip_from 104.24.0.0/14;
    set_real_ip_from 172.64.0.0/13;
    set_real_ip_from 131.0.72.0/22;

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
        proxy_pass http://unix:/run/nails_salon/nails_salon.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
    }
}
EOF

nginx -t
systemctl restart nginx
```

## Kiểm tra HTTPS

### Test SSL Certificate
```bash
# Check với openssl
openssl s_client -connect lknailslashes.de:443 -servername lknailslashes.de

# Check với curl
curl -I https://lknailslashes.de

# Online test
# https://www.ssllabs.com/ssltest/
```

### Check Django HTTPS Settings
```bash
# Test redirect
curl -I http://lknailslashes.de
# Should return 301 redirect to https

# Test HTTPS
curl -I https://lknailslashes.de
# Should return 200 OK
```

## Auto-renewal Certificate (Let's Encrypt)

Certbot tự động setup renewal, nhưng bạn có thể check:

```bash
# Check auto-renewal setup
systemctl status snap.certbot.renew.service
systemctl status snap.certbot.renew.timer

# Manual renewal test
certbot renew --dry-run

# Force renewal (if needed)
certbot renew --force-renewal
```

## Troubleshooting HTTPS

### Common Issues:

1. **Mixed Content Errors**:
   - Check Django SECURE_SSL_REDIRECT = True
   - Ensure all internal links use HTTPS

2. **Certificate Errors**:
   - Check certificate path in nginx
   - Verify certificate validity

3. **Redirect Loops**:
   - Check X-Forwarded-Proto headers
   - Verify CSRF_TRUSTED_ORIGINS

### Debug Commands:
```bash
# Check nginx error logs
tail -f /var/log/nginx/error.log

# Check Django logs  
journalctl -u nails_salon.service -f

# Test nginx config
nginx -t

# Check certificates
certbot certificates
```

Sau khi setup HTTPS xong, website sẽ có:
- ✅ SSL Certificate
- ✅ HTTPS redirect
- ✅ Security headers
- ✅ A+ SSL rating (if configured properly)