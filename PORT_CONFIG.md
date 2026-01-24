# Port Configuration

## Application Ports

- **Backend API**: `5551`
- **Frontend Dashboard**: `4551`

## Configuration Files

### Backend (API)
- **Service file**: `/etc/systemd/system/atqan-api.service`
  ```ini
  ExecStart=/home/mahmoud/atqan-wathq-services/api/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 5551
  ```

### Frontend (Dashboard)
- **Service file**: `/etc/systemd/system/atqan-dashboard.service`
  ```ini
  Environment="PORT=4551"
  ```

- **Nuxt config**: `dashboard/nuxt.config.ts`
  ```typescript
  devServer: {
    host: "localhost",
    port: 4551,
  }
  ```

## URLs

### Development
- Frontend: `http://localhost:4551`
- Backend API: `http://localhost:5551`
- API Docs: `http://localhost:5551/docs`

### Production
- Frontend: `http://your-server:4551`
- Backend API: `http://your-server:5551`
- API Docs: `http://your-server:5551/docs`

## Firewall Configuration

If using UFW (Ubuntu Firewall):
```bash
sudo ufw allow 4551/tcp comment 'Atqan Dashboard'
sudo ufw allow 5551/tcp comment 'Atqan API'
sudo ufw reload
```

If using firewalld (CentOS/RHEL):
```bash
sudo firewall-cmd --permanent --add-port=4551/tcp
sudo firewall-cmd --permanent --add-port=5551/tcp
sudo firewall-cmd --reload
```

## Nginx Reverse Proxy (Optional)

If you want to use standard ports (80/443) with domain names:

```nginx
# Frontend
server {
    listen 80;
    server_name dashboard.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:4551;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5551;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Environment Variables

### Backend (.env)
```bash
# No port configuration needed - set in systemd service
```

### Frontend (.env)
```bash
NUXT_PUBLIC_API_BASE=http://localhost:5551/api/v1
NUXT_PRIVATE_API_BASE_URL=http://localhost:5551
# PORT is set in systemd service
```

## Troubleshooting

### Check if ports are in use:
```bash
sudo netstat -tlnp | grep 4551
sudo netstat -tlnp | grep 5551
```

### Check if services are listening:
```bash
curl http://localhost:4551
curl http://localhost:5551/docs
```

### View service logs:
```bash
sudo journalctl -u atqan-dashboard -f
sudo journalctl -u atqan-api -f
```
