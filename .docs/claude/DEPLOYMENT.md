# Open WebUI Deployment Guide for Coolify/VPS

This guide will help you deploy Open WebUI on Coolify or any VPS using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (or other LLM provider)
- Coolify instance or VPS with Docker support

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd open-webui-cloned-from-fork
```

### 2. Configure Environment Variables

Copy the production environment template:

```bash
cp .env.production .env
```

Edit `.env` and set your configuration:

```bash
# Required: Set your OpenAI API key
OPENAI_API_KEY=sk-your-key-here

# Required: Generate a secure secret key
WEBUI_SECRET_KEY=$(openssl rand -hex 32)

# Optional: Change the port (default: 3000)
OPEN_WEBUI_PORT=3000

# Optional: Configure CORS for your domain
CORS_ALLOW_ORIGIN=https://yourdomain.com
```

### 3. Deploy with Docker Compose

```bash
# Build and start the services
docker compose -f docker-compose.coolify.yaml up -d

# View logs
docker compose -f docker-compose.coolify.yaml logs -f

# Stop the services
docker compose -f docker-compose.coolify.yaml down
```

### 4. Access the Application

Open your browser and navigate to:
- Local: `http://localhost:3000`
- Production: `http://your-server-ip:3000`

## Coolify Deployment

### Method 1: Using Coolify's Git Integration

1. **Create a new service in Coolify**
   - Go to your Coolify dashboard
   - Click "Add New Service" → "Docker Compose"

2. **Configure the service**
   - Repository: Point to your Git repository
   - Branch: `main` (or your branch)
   - Docker Compose Location: `docker-compose.coolify.yaml`

3. **Set environment variables in Coolify**
   - Go to Service → Environment Variables
   - Add all required variables from `.env.production`

4. **Deploy**
   - Click "Deploy" and Coolify will handle the rest
   - Coolify will automatically set up SSL with Let's Encrypt

### Method 2: Manual Docker Compose

If deploying manually on a VPS:

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Clone repository
git clone <your-repo-url>
cd open-webui-cloned-from-fork

# Configure environment
cp .env.production .env
nano .env  # Edit with your values

# Deploy
docker compose -f docker-compose.coolify.yaml up -d
```

## Configuration Options

### Using OpenAI (Default)

The default configuration uses OpenAI. Just set:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_API_BASE_URL=https://api.openai.com/v1
```

### Using Local Ollama (Optional)

To use Ollama instead of OpenAI:

1. Uncomment the Ollama service in `docker-compose.coolify.yaml`
2. Uncomment the Ollama volume
3. Set environment variable:
   ```env
   OLLAMA_BASE_URL=http://ollama:11434
   ```

### Using PostgreSQL Database (Optional)

By default, SQLite is used. To use PostgreSQL:

1. Uncomment the PostgreSQL service in `docker-compose.coolify.yaml`
2. Uncomment the postgres volume
3. Set environment variables:
   ```env
   DATABASE_URL=postgresql://openwebui:your-password@postgres:5432/openwebui
   POSTGRES_PASSWORD=your-secure-password
   ```

### Adding Redis for Caching (Optional)

For better performance with multiple instances:

1. Uncomment the Redis service in `docker-compose.coolify.yaml`
2. Uncomment the redis volume

## Security Best Practices

1. **Generate a strong secret key:**
   ```bash
   openssl rand -hex 32
   ```

2. **Restrict CORS in production:**
   ```env
   CORS_ALLOW_ORIGIN=https://yourdomain.com
   ```

3. **Use environment variables for secrets:**
   - Never commit `.env` files with secrets to Git
   - Use Coolify's environment variable manager

4. **Enable HTTPS:**
   - Coolify handles this automatically with Let's Encrypt
   - For manual deployments, use nginx/traefik with SSL certificates

## Reverse Proxy Configuration

If using nginx or Traefik in front of the application:

### Nginx Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Traefik Labels (for docker-compose)

Add these labels to the `open-webui` service:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.openwebui.rule=Host(`yourdomain.com`)"
  - "traefik.http.routers.openwebui.entrypoints=websecure"
  - "traefik.http.routers.openwebui.tls.certresolver=letsencrypt"
  - "traefik.http.services.openwebui.loadbalancer.server.port=8080"
```

## Backup and Restore

### Backup Data

```bash
# Backup the data volume
docker run --rm -v open-webui:/data -v $(pwd):/backup \
  alpine tar czf /backup/open-webui-backup.tar.gz -C /data .
```

### Restore Data

```bash
# Restore from backup
docker run --rm -v open-webui:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/open-webui-backup.tar.gz"
```

## Troubleshooting

### Check logs

```bash
docker compose -f docker-compose.coolify.yaml logs -f open-webui
```

### Restart service

```bash
docker compose -f docker-compose.coolify.yaml restart open-webui
```

### Reset everything

```bash
docker compose -f docker-compose.coolify.yaml down -v
docker compose -f docker-compose.coolify.yaml up -d
```

### Common Issues

1. **Port already in use:**
   - Change `OPEN_WEBUI_PORT` in `.env`

2. **API key not working:**
   - Verify the key is correct in `.env`
   - Check logs for API errors

3. **Can't access from outside:**
   - Check firewall settings
   - Ensure port is exposed in docker-compose
   - Verify reverse proxy configuration

## Updating

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose -f docker-compose.coolify.yaml up -d --build
```

## Support

- [Open WebUI Documentation](https://docs.openwebui.com)
- [GitHub Issues](https://github.com/open-webui/open-webui/issues)
- [Discord Community](https://discord.gg/5rJgQTnV4s)
