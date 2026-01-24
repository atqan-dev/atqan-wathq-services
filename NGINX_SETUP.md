# Nginx Production Setup Guide

## Step 1: Install Nginx

```bash
sudo apt update
sudo apt install nginx -y
```

## Step 2: Update Service Configuration

Since Nginx will handle external traffic, change your services to listen on localhost only for better security:

### API Service
```bash
sudo nano /etc/systemd/system/atqan-api.service
```

Change:
```ini
ExecStart=/home/mahmoud/atqan-wathq-services/api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 5551
```

### Dashboard Service
No changes needed - it already uses environment variable for host.

Reload services:
```bash
sudo systemctl daemon-reload
sudo systemctl restart atqan-api
sudo systemctl restart atqan-dashboard
```

## Step 3: Configure Nginx

### Copy the configuration file:
```bash
sudo cp /home/mahmoud/atqan-wathq-services/nginx.conf /etc/nginx/sites-available/atqan
```

### Edit the configuration:
```bash
sudo nano /etc/nginx/sites-available/atqan
```

**Update these values:**
- Domain is set to: `verify.tawthiq.com.sa`
- Update SSL certificate paths (or remove SSL section for now)
- Verify paths match your setup

### For IP-only access (no domain):
If you don't have a domain yet, use this simpler HTTP-only version:

```bash
sudo nano /etc/nginx/sites-available/atqan
```

Replace the content with:
```nginx
# Upstream definitions
upstream atqan_api {
    server 127.0.0.1:5551;
    keepalive 32;
}

upstream atqan_dashboard {
    server 127.0.0.1:4551;
    keepalive 32;
}

# Main HTTP Server
server {
    listen 80;
    listen [::]:80;
    server_name 162.241.87.35 _;
    
    # Logging
    access_log /var/log/nginx/atqan_access.log;
    error_log /var/log/nginx/atqan_error.log warn;
    
    client_max_body_size 50M;
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
    
    # Frontend Dashboard
    location / {
        proxy_pass http://atqan_dashboard;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://atqan_api/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Authorization $http_authorization;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    # API Documentation
    location /docs {
        proxy_pass http://atqan_api/docs;
        proxy_set_header Host $host;
    }
    
    location /redoc {
        proxy_pass http://atqan_api/redoc;
        proxy_set_header Host $host;
    }
    
    location /openapi.json {
        proxy_pass http://atqan_api/openapi.json;
        proxy_set_header Host $host;
    }
}
```

## Step 4: Enable the Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/atqan /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

## Step 5: Configure Firewall

```bash
# Allow Nginx HTTP/HTTPS
sudo ufw allow 'Nginx Full'

# Or manually:
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Remove direct access to app ports (optional, for extra security)
# sudo ufw delete allow 4551/tcp
# sudo ufw delete allow 5551/tcp

# Reload firewall
sudo ufw reload
sudo ufw status
```

## Step 6: Test the Setup

```bash
# Check Nginx status
sudo systemctl status nginx

# Check if Nginx is listening
sudo netstat -tlnp | grep nginx

# Test from server
curl http://localhost
curl http://localhost/api/health
curl http://localhost/docs

# Test from outside (replace with your IP)
curl http://162.241.87.35
curl http://162.241.87.35/docs
```

## Step 7: Add SSL/TLS (Optional but Recommended)

### Using Let's Encrypt (Free SSL):

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate for your domain
sudo certbot --nginx -d verify.tawthiq.com.sa -d www.verify.tawthiq.com.sa

# Certbot will automatically update your Nginx config
# Test auto-renewal
sudo certbot renew --dry-run
```

### Manual SSL Setup:
If you have your own certificates:

```bash
# Copy certificates
sudo mkdir -p /etc/nginx/ssl
sudo cp your-cert.crt /etc/nginx/ssl/
sudo cp your-key.key /etc/nginx/ssl/

# Update nginx.conf SSL paths:
ssl_certificate /etc/nginx/ssl/your-cert.crt;
ssl_certificate_key /etc/nginx/ssl/your-key.key;
```

## Step 8: Monitoring and Logs

### View logs:
```bash
# Access logs
sudo tail -f /var/log/nginx/atqan_access.log

# Error logs
sudo tail -f /var/log/nginx/atqan_error.log

# Nginx error log
sudo tail -f /var/log/nginx/error.log
```

### Log rotation (automatic):
Nginx logs are automatically rotated by logrotate. Config at:
```bash
/etc/logrotate.d/nginx
```

## Troubleshooting

### Nginx won't start:
```bash
# Check configuration
sudo nginx -t

# Check detailed errors
sudo journalctl -u nginx -n 50

# Check if port 80 is in use
sudo netstat -tlnp | grep :80
```

### 502 Bad Gateway:
```bash
# Check if backend services are running
sudo systemctl status atqan-api
sudo systemctl status atqan-dashboard

# Check if they're listening
sudo netstat -tlnp | grep 4551
sudo netstat -tlnp | grep 5551

# Check SELinux (if enabled)
sudo setsebool -P httpd_can_network_connect 1
```

### 504 Gateway Timeout:
- Increase timeout values in nginx config
- Check backend service logs for slow responses

### Permission denied errors:
```bash
# Check Nginx user has access
sudo chown -R www-data:www-data /var/cache/nginx
sudo chmod -R 755 /var/cache/nginx
```

## Performance Tuning

### For high traffic:
```bash
sudo nano /etc/nginx/nginx.conf
```

Update:
```nginx
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
client_body_buffer_size 128k;
client_max_body_size 50m;
```

## Security Enhancements

### 1. Hide Nginx version:
```nginx
# In /etc/nginx/nginx.conf
http {
    server_tokens off;
}
```

### 2. Add fail2ban for brute force protection:
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Rate limiting (already in full config):
- API: 100 requests/second
- General: 200 requests/second

## Maintenance

### Reload after config changes:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

### Restart Nginx:
```bash
sudo systemctl restart nginx
```

### Update Nginx:
```bash
sudo apt update
sudo apt upgrade nginx
```

## URLs After Setup

- **Frontend**: `https://verify.tawthiq.com.sa`
- **API**: `https://verify.tawthiq.com.sa/api/`
- **API Docs**: `https://verify.tawthiq.com.sa/docs`
- **ReDoc**: `https://verify.tawthiq.com.sa/redoc`

**Without SSL (HTTP only):**
- **Frontend**: `http://verify.tawthiq.com.sa` or `http://162.241.87.35`
- **API**: `http://verify.tawthiq.com.sa/api/` or `http://162.241.87.35/api/`
- **API Docs**: `http://verify.tawthiq.com.sa/docs` or `http://162.241.87.35/docs`

## Benefits of This Setup

✅ **Security**: Apps only accessible through Nginx
✅ **SSL/TLS**: Easy to add HTTPS
✅ **Caching**: Static assets cached for performance
✅ **Compression**: Gzip enabled for faster loading
✅ **Rate Limiting**: Protection against abuse
✅ **Load Balancing**: Ready for multiple backend instances
✅ **Logging**: Centralized access and error logs
✅ **Standard Ports**: Use port 80/443 instead of custom ports
