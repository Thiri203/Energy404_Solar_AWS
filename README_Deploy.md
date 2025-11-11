# Energy404 — Cloud Deployment (Docker + DigitalOcean + GitHub Actions)

This guide covers **deployment only**: running your FastAPI backend (port **8000**) and Dash frontend (port **8050**) on a **DigitalOcean Droplet** with **CI/CD via GitHub Actions** using images hosted on **Docker Hub**.

---

## 1) What you’ll have at the end
- A DigitalOcean Droplet running:
  - **Backend**: FastAPI at `http://<DROPLET_IP>:8000` (`/docs` for Swagger)
  - **Frontend**: Dash at `http://<DROPLET_IP>:8050`
- A GitHub Actions pipeline that on every push to `main`:
  1) Builds Docker images for backend & frontend
  2) Pushes them to Docker Hub
  3) SSH-deploys to the Droplet and restarts services

---

## 2) Repo layout (minimum)
```
.
├── api.py
├── energy_dash.py
├── requirements.txt
├── Dockerfile               # Multi-stage build (builder + runtime)
├── docker-compose.yml       # Production compose used on the Droplet
├── pipeline/
│   ├── __init__.py
│   └── predict.py
├── models_local_backup/     # *.pkl models (runtime)
│   └── ...pkl
└── data/
    └── city_weather.csv     # small runtime csv
```
> Ensure `.dockerignore` **does not** exclude `models_local_backup/`, `pipeline/`, or `data/`.

---

## 3) DigitalOcean — one-time server setup

### 3.1 Create Droplet
- Image: **Ubuntu 22.04 LTS**
- Plan: 2 vCPU / 4 GB RAM (or higher)
- Disk: **≥ 20 GB**
- Networking / Firewall: allow inbound **22, 8000, 8050**

### 3.2 First login & install Docker
```bash
# SSH (example)
ssh -i /path/to/key.pem root@<DROPLET_IP>

# Install Docker & Compose
apt update -y
apt install -y docker.io docker-compose
systemctl enable docker && systemctl start docker

# (Optional) Create non-root 'deploy' user
adduser deploy
usermod -aG docker deploy
mkdir -p /home/deploy/app && chown -R deploy:deploy /home/deploy

# Add your SSH public key to /home/deploy/.ssh/authorized_keys if using 'deploy'
```

---

## 4) Production docker-compose.yml (used on server)

Place this **on the Droplet** at `/home/<USER>/app/docker-compose.yml`  
(The CI/CD workflow can upload this automatically each deploy.)

```yaml
version: "3.9"

services:
  backend:
    image: thiri248/energy404-backend:latest
    container_name: energy404_backend
    ports:
      - "8000:8000"
    restart: unless-stopped

  frontend:
    image: thiri248/energy404-frontend:latest
    container_name: energy404_frontend
    depends_on:
      - backend
    environment:
      - API_BASE_URL=http://backend:8000
    ports:
      - "8050:8050"
    restart: unless-stopped

networks:
  default:
    name: energy404_network
```

---

## 5) GitHub Actions — CI/CD workflow

Create **.github/workflows/cicd.yml**

```yaml
name: CI/CD to DigitalOcean Droplet

on:
  push:
    branches: [ main ]

env:
  BACKEND_IMAGE: thiri248/energy404-backend
  FRONTEND_IMAGE: thiri248/energy404-frontend
  TAG_SHA: ${{ github.sha }}
  TAG_LATEST: latest

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build & push backend
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: |
            ${{ env.BACKEND_IMAGE }}:${{ env.TAG_SHA }}
            ${{ env.BACKEND_IMAGE }}:${{ env.TAG_LATEST }}

      - name: Build & push frontend
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: |
            ${{ env.FRONTEND_IMAGE }}:${{ env.TAG_SHA }}
            ${{ env.FRONTEND_IMAGE }}:${{ env.TAG_LATEST }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo (for compose upload)
        uses: actions/checkout@v4

      - name: Upload docker-compose.yml
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.DO_HOST }}
          username: ${{ secrets.DO_USER }}
          key: ${{ secrets.DO_SSH_KEY }}
          source: "docker-compose.yml"
          target: "/home/${{ secrets.DO_USER }}/app"

      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: ${{ secrets.DO_HOST }}
          username: ${{ secrets.DO_USER }}
          key: ${{ secrets.DO_SSH_KEY }}
          script: |
            set -e
            cd /home/${{ secrets.DO_USER }}/app
            docker compose pull
            docker compose up -d
            docker system prune -f
```

---

## 6) GitHub Secrets (Actions → New repository secret)

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username (e.g., `thiri248`) |
| `DOCKERHUB_TOKEN` | Docker Hub Access Token |
| `DO_HOST` | Droplet public IP (e.g., `203.0.113.10`) |
| `DO_USER` | `deploy` (or `root`) |
| `DO_SSH_KEY` | **Private key** (PEM content) that matches the public key on the Droplet |

---

## 7) Deploy flow
1. Push to `main`
2. GitHub Actions builds & pushes images, uploads compose, and deploys
3. Test:
   - Frontend → `http://<DROPLET_IP>:8050`
   - Backend docs → `http://<DROPLET_IP>:8000/docs`

---

## 8) Useful server commands
```bash
docker ps
docker compose -f /home/<USER>/app/docker-compose.yml logs -f
cd /home/<USER>/app && docker compose up -d
cd /home/<USER>/app && docker compose down
docker system df
docker system prune -af
```

---

## 9) Troubleshooting
- Open ports **22, 8000, 8050** in DigitalOcean Firewall
- Add user to `docker` group: `sudo usermod -aG docker <USER> && newgrp docker`
- Resize disk or prune images if space runs out
- Ensure `API_BASE_URL=http://backend:8000` in compose and both services share the default network
