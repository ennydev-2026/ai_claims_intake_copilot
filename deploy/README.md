# Production deployment (example)

These steps are generic: substitute your SSH host, deploy path, domain name, and certificate tooling. Do not commit real hosts, domains, or secrets into this repository.

## 1. Upload project

Pick a directory on the server (example: `/opt/your-app`). From your machine:

```bash
rsync -avz --delete \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '.venv' \
  --exclude '*.pyc' \
  --exclude '.pytest_cache' \
  ./ YOUR_SSH_HOST:/opt/your-app/
```

Copy `.env` securely on the server (never commit `.env`):

```bash
scp .env YOUR_SSH_HOST:/opt/your-app/.env
```

## 2. Docker Compose

On the server, some installs use `docker compose` and others `docker-compose`; use whichever matches your Docker installation. Use `sudo` if required for the Docker socket.

```bash
ssh YOUR_SSH_HOST
cd /opt/your-app
sudo docker compose up --build -d
# or: sudo docker-compose up --build -d
sudo docker compose ps
curl -s http://127.0.0.1:8501/ | head -5
```

If you use the default Compose file, only the dashboard may be published on the host (`8501`). To reach the API from the host for smoke tests, use [`docker-compose.dev.yml`](../docker-compose.dev.yml) or check health from inside the Docker network.

## 3. Nginx reverse proxy

Point DNS for **your public hostname** at the server’s IP. Copy and adapt [`deploy/nginx/streamlit-reverse-proxy.example.conf`](nginx/streamlit-reverse-proxy.example.conf): set `server_name` and upstream port if needed. Enable the site, test, reload:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

## 4. TLS (example with Certbot + nginx)

```bash
sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d YOUR_DOMAIN
```

To dry-run renewal for one certificate only (useful on hosts with many certs):

```bash
sudo certbot renew --cert-name YOUR_DOMAIN --dry-run
```

## 5. Restart policy

Compose services use `restart: unless-stopped` in [`docker-compose.yml`](../docker-compose.yml) so containers restart after failures when Docker is running.
