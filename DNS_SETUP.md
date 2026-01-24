# DNS Configuration for verify.notarizationjustice.sa

## Required DNS Records

You need to configure these DNS records with your domain registrar (notarizationjustice.sa):

### A Records (Point domain to your server)

```
Type: A
Name: verify
Value: 162.241.87.35
TTL: 3600 (or Auto)

Type: A
Name: www.verify
Value: 162.241.87.35
TTL: 3600 (or Auto)
```

### Optional: API Subdomain

If you want to use `api.verify.notarizationjustice.sa`:

```
Type: A
Name: api.verify
Value: 162.241.87.35
TTL: 3600 (or Auto)
```

## Verify DNS Configuration

After adding DNS records, wait 5-30 minutes for propagation, then test:

```bash
# Check if domain resolves to your server
dig verify.notarizationjustice.sa
nslookup verify.notarizationjustice.sa

# Should show: 162.241.87.35
```

Online tools:
- https://dnschecker.org
- https://mxtoolbox.com/SuperTool.aspx

## Setup Steps

### 1. Configure DNS (Do this first!)
Add the A records above in your domain control panel.

### 2. Wait for DNS Propagation
Usually takes 5-30 minutes, can take up to 48 hours.

### 3. Install and Configure Nginx
```bash
# Install Nginx
sudo apt update
sudo apt install nginx -y

# Copy configuration
sudo cp /home/mahmoud/atqan-wathq-services/nginx.conf /etc/nginx/sites-available/atqan

# For HTTP-only (no SSL yet), edit the config:
sudo nano /etc/nginx/sites-available/atqan
```

**Remove or comment out the HTTPS sections** (lines with `listen 443 ssl`), and update the HTTP section:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name verify.notarizationjustice.sa www.verify.notarizationjustice.sa;
    
    # Remove the redirect to HTTPS
    # Comment out: return 301 https://$host$request_uri;
    
    # Add your location blocks here (proxy_pass to backend)
    # ... (see NGINX_SETUP.md for full config)
}
```

### 4. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/atqan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Test HTTP Access
```bash
curl http://verify.notarizationjustice.sa
curl http://verify.notarizationjustice.sa/docs
```

### 6. Add SSL Certificate (After HTTP works)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get free SSL certificate from Let's Encrypt
sudo certbot --nginx -d verify.notarizationjustice.sa -d www.verify.notarizationjustice.sa

# Certbot will automatically:
# - Get the certificate
# - Update your Nginx config
# - Set up auto-renewal
```

### 7. Test HTTPS Access
```bash
curl https://verify.notarizationjustice.sa
curl https://verify.notarizationjustice.sa/docs
```

## Final URLs

After complete setup:

- **Frontend**: https://verify.notarizationjustice.sa
- **API**: https://verify.notarizationjustice.sa/api/
- **API Docs**: https://verify.notarizationjustice.sa/docs
- **ReDoc**: https://verify.notarizationjustice.sa/redoc

## Troubleshooting

### Domain doesn't resolve
- Check DNS records are correct
- Wait longer for propagation (up to 48 hours)
- Clear your DNS cache: `sudo systemd-resolve --flush-caches`

### SSL certificate fails
- Make sure HTTP works first
- Ensure port 80 is open: `sudo ufw allow 80`
- Check domain resolves: `dig verify.notarizationjustice.sa`
- Let's Encrypt needs to verify domain ownership via HTTP

### 502 Bad Gateway
- Check backend services are running:
  ```bash
  sudo systemctl status atqan-api
  sudo systemctl status atqan-dashboard
  ```

## Contact Domain Administrator

If you don't have access to DNS settings, contact your domain administrator with this information:

**Request:**
"Please add the following DNS A records for verify.notarizationjustice.sa:

- Host: verify.notarizationjustice.sa → IP: 162.241.87.35
- Host: www.verify.notarizationjustice.sa → IP: 162.241.87.35

These records will point the subdomain to our application server."
