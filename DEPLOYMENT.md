# Auto-Deployment Setup Guide

This guide explains how to set up automatic deployment when merging to the main branch.

## Prerequisites

1. **Server with SSH access**
2. **Git repository** (GitHub, GitLab, or Bitbucket)
3. **Systemd services** for API and Dashboard

## Option 1: GitHub Actions (Recommended)

### Step 1: Install System Dependencies

WeasyPrint (for PDF generation) requires system libraries. Install them first:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

# CentOS/RHEL
sudo yum install -y \
    pango \
    pango-devel \
    gdk-pixbuf2 \
    libffi-devel
```

### Step 2: Create Systemd Services

#### API Service (`/etc/systemd/system/atqan-api.service`)

```ini
[Unit]
Description=Atqan WATHQ API Service
After=network.target postgresql.service

[Service]
Type=simple
User=mahmoud
WorkingDirectory=/home/mahmoud/atqan-wathq-services/api
Environment="PATH=/home/mahmoud/atqan-wathq-services/api/.venv/bin"
ExecStart=/home/mahmoud/atqan-wathq-services/api/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 5551
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Dashboard Service (`/etc/systemd/system/atqan-dashboard.service`)

**Important:** First find where `pnpm` is installed:
```bash
which pnpm
# Example output: /home/mahmoud/.nvm/versions/node/v22.17.1/bin/pnpm
```

Then use that path in the service file:

```ini
[Unit]
Description=Atqan WATHQ Dashboard Service
After=network.target

[Service]
Type=simple
User=mahmoud
WorkingDirectory=/home/mahmoud/atqan-wathq-services/dashboard
# Update this path based on 'which pnpm' output
ExecStart=/home/mahmoud/.nvm/versions/node/v22.17.1/bin/pnpm start
Environment="NODE_ENV=production"
Environment="PORT=3000"
Environment="PATH=/home/mahmoud/.nvm/versions/node/v22.17.1/bin:/usr/local/bin:/usr/bin:/bin"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Alternative:** Use Node.js directly with the built output:
```ini
[Unit]
Description=Atqan WATHQ Dashboard Service
After=network.target

[Service]
Type=simple
User=mahmoud
WorkingDirectory=/home/mahmoud/atqan-wathq-services/dashboard
ExecStart=/usr/bin/node .output/server/index.mjs
Environment="NODE_ENV=production"
Environment="PORT=3000"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable atqan-api
sudo systemctl enable atqan-dashboard
sudo systemctl start atqan-api
sudo systemctl start atqan-dashboard
```

### Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:
- `SERVER_HOST`: Your server IP or domain (e.g., `192.168.1.100`)
- `SERVER_USER`: SSH username (e.g., `ubuntu`)
- `SSH_PRIVATE_KEY`: Your SSH private key (copy from `~/.ssh/id_rsa`)
- `SERVER_PORT`: SSH port (default: `22`)

### Step 3: Update Deployment Script

Edit `.github/workflows/deploy.yml` and update:
- `/path/to/your/app` → actual path on server
- Service names if different
- Add environment variables if needed

### Step 4: Test Deployment

1. Make a change and commit to a feature branch
2. Create a pull request to `main`
3. Merge the PR
4. Check Actions tab in GitHub to see deployment progress

## Option 2: GitLab CI/CD

Create `.gitlab-ci.yml`:

```yaml
stages:
  - deploy

deploy_production:
  stage: deploy
  only:
    - main
  before_script:
    - 'command -v ssh-agent >/dev/null || ( apt-get update -y && apt-get install openssh-client -y )'
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan $SERVER_HOST >> ~/.ssh/known_hosts
    - chmod 644 ~/.ssh/known_hosts
  script:
    - ssh $SERVER_USER@$SERVER_HOST "
        cd /home/mahmoud/atqan-wathq-services &&
        git pull origin main &&
        cd api &&
        source .venv/bin/activate &&
        pip install -r requirements.txt &&
        alembic upgrade head &&
        sudo systemctl restart atqan-api &&
        cd ../dashboard &&
        pnpm install &&
        pnpm build &&
        sudo systemctl restart atqan-dashboard
      "
```

## Option 3: Simple Git Hook (Server-side)

On your server, create a post-receive hook:

```bash
# On server
cd /home/mahmoud/atqan-wathq-services
git init --bare ~/atqan-repo.git
cd ~/atqan-repo.git/hooks
nano post-receive
```

Add this script:

```bash
#!/bin/bash

WORK_TREE=/home/mahmoud/atqan-wathq-services
GIT_DIR=$HOME/atqan-repo.git

echo "Deploying to production..."

# Update working directory
git --work-tree=$WORK_TREE --git-dir=$GIT_DIR checkout -f main

# Deploy API
cd $WORK_TREE/api
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart atqan-api

# Deploy Dashboard
cd $WORK_TREE/dashboard
pnpm install
pnpm build
sudo systemctl restart atqan-dashboard

echo "Deployment completed!"
```

Make it executable:
```bash
chmod +x post-receive
```

On your local machine:
```bash
git remote add production mahmoud@your-server:~/atqan-repo.git
git push production main
```

## Option 4: PM2 with Ecosystem File

Install PM2 on server:
```bash
npm install -g pm2
```

Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [
    {
      name: 'atqan-api',
      cwd: '/home/mahmoud/atqan-wathq-services/api',
      script: '.venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 5551',
      env: {
        PYTHONPATH: '/home/mahmoud/atqan-wathq-services/api'
      }
    },
    {
      name: 'atqan-dashboard',
      cwd: '/home/mahmoud/atqan-wathq-services/dashboard',
      script: 'pnpm',
      args: 'start',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    }
  ],
  
  deploy: {
    production: {
      user: 'mahmoud',
      host: 'your-server',
      ref: 'origin/main',
      repo: 'git@github.com:your-org/atqan-wathq-services-fixing.git',
      path: '/home/mahmoud/atqan-wathq-services',
      'post-deploy': 'cd api && source .venv/bin/activate && pip install -r requirements.txt && alembic upgrade head && cd ../dashboard && pnpm install && pnpm build && pm2 reload ecosystem.config.js'
    }
  }
}
```

Deploy with:
```bash
pm2 deploy production setup
pm2 deploy production
```

## Monitoring & Logs

### Check service status:
```bash
sudo systemctl status atqan-api
sudo systemctl status atqan-dashboard
```

### View logs:
```bash
# API logs
sudo journalctl -u atqan-api -f

# Dashboard logs
sudo journalctl -u atqan-dashboard -f

# Or if using PM2
pm2 logs atqan-api
pm2 logs atqan-dashboard
```

## Rollback Strategy

### Using systemd:
```bash
cd /home/mahmoud/atqan-wathq-services
git log --oneline -10  # Find commit to rollback to
git reset --hard <commit-hash>
sudo systemctl restart atqan-api
sudo systemctl restart atqan-dashboard
```

### Using PM2:
```bash
pm2 deploy production revert 1
```

## Security Best Practices

1. **Use SSH keys** instead of passwords
2. **Restrict sudo access** - create specific sudoers rules:
   ```bash
   mahmoud ALL=(ALL) NOPASSWD: /bin/systemctl restart atqan-api, /bin/systemctl restart atqan-dashboard
   ```
3. **Use environment variables** for secrets
4. **Enable firewall** and only allow necessary ports
5. **Regular backups** of database before deployment

## Troubleshooting

### Deployment fails:
- Check GitHub Actions logs
- Verify SSH connection: `ssh user@server`
- Check file permissions on server
- Verify systemd service configuration

### Services won't start:
- Check logs: `sudo journalctl -u atqan-api -n 50`
- Verify Python virtual environment
- Check database connection
- Verify port availability: `sudo netstat -tlnp | grep 5551`

### Database migration issues:
- Backup database first
- Run migrations manually: `alembic upgrade head`
- Check migration files in `api/alembic/versions/`

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [PM2 Documentation](https://pm2.keymetrics.io/)
- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
