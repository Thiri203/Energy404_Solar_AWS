# Energy404 — Beginner-Friendly CI/CD & Deployment Guide

This guide shows **every step** to run and deploy the Energy404 app — even if you’ve never deployed anything before.  
You’ll run it **locally with Docker**, **push images to Docker Hub**, and **auto-deploy to a DigitalOcean Droplet** with **GitHub Actions**.

---

## 0) What this project is

- **Backend (FastAPI)**: `api.py` exposes `/predict` (returns kWh/m² per year).
- **Frontend (Dash)**: `energy_dash.py` calls the API and renders the UI.
- **Containerization**: One **multi-stage `Dockerfile`** builds runtime images for both services.
- **Orchestration**: `docker-compose.yml` (dev parity, runs backend + frontend together).
- **CI/CD**: `.github/workflows/deploy.yml` auto-deploys to a **DigitalOcean Droplet**.
- **Model Artifacts**: large `.pkl` models live **outside** the image (e.g., **S3** or host mount) to keep images small and avoid OOM.

> If you’re totally new:  
> **Docker Desktop** runs containers locally; **Docker Hub** stores images;  
> a **Droplet** is a small cloud server; **GitHub Actions** is your auto-deploy pipeline.

---

## 1) Prerequisites

- Accounts: **GitHub**, **Docker Hub**, **DigitalOcean** (and **AWS** if you’ll use S3).
- Local tools: **Docker Desktop** (Mac/Windows) or Docker Engine (Linux); **Git**.
- SSH key (for CI/CD to connect to the Droplet):
  - Create: `ssh-keygen -t ed25519 -C "you@example.com"`
  - Add **public key** to DigitalOcean; keep **private key** for GitHub Secrets.

---

## 2) Project structure (key files)

.
├── api.py # FastAPI backend (port 8000)
├── energy_dash.py # Dash frontend (port 8050)
├── pipeline/
│ └── predict.py # lazy-loading of models
├── data/
│ └── city_weather.csv # small runtime CSV (included in image)
├── models_local_backup/ # model .pkl files (NOT in Git, NOT in image)
├── Dockerfile # multi-stage build (builder + runtime)
├── docker-compose.yml # local/dev orchestration
├── .dockerignore # excludes big files (e.g., *.parquet, *.pkl)
└── .github/workflows/deploy.yml # CI/CD (pull & run images on the Droplet)


> `.dockerignore` intentionally excludes huge datasets and `.pkl` so images stay small.

---

## 3) Run locally (Docker Compose)

1) Start both services:
```bash
docker compose up --build


Open:

Backend docs: http://localhost:8000/docs

Frontend app: http://localhost:8050

Stop:

docker compose down

4) Build images & push to Docker Hub

Replace <DOCKERHUB_USERNAME> with your Docker Hub username (e.g., thiri248).

# Login (one-time per machine)
docker login

# Tag local images (names created by compose)
docker tag rooftop-solar-potential-predictor-backend:latest  <DOCKERHUB_USERNAME>/energy404-backend:latest
docker tag rooftop-solar-potential-predictor-frontend:latest <DOCKERHUB_USERNAME>/energy404-frontend:latest

# Push to Docker Hub
docker push <DOCKERHUB_USERNAME>/energy404-backend:latest
docker push <DOCKERHUB_USERNAME>/energy404-frontend:latest


Confirm on Docker Hub → your profile → Repositories.

5) Prepare the DigitalOcean Droplet
A) Create the Droplet

Image: Ubuntu 22.04 LTS (x86_64/amd64)

Size: 2–4 vCPU / 4–8 GB RAM (more if your models are heavy)

Region: closest to you (e.g., Singapore for Thailand)

Authentication: add your SSH public key

B) SSH into it
ssh root@<DROPLET_IP>

C) Install Docker Engine
apt-get update
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
| tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
docker --version

D) Model artifacts (final approach)

Option 1 — S3 (recommended): download to a writable path on startup (or first request).
Option 2 — Host mount: put .pkl files in /opt/energy404_models on the Droplet and mount into the container.

mkdir -p /opt/energy404_models
# scp your models up if not using S3:
# scp lgb_models.pkl root@<DROPLET_IP>:/opt/energy404_models/


(Optional firewall if you’re not using DO’s network firewall):

ufw allow 22
ufw allow 8000
ufw allow 8050
ufw enable

6) CI/CD with GitHub Actions

This workflow deploys automatically on push to main.

A) Add GitHub Secrets (Repo → Settings → Secrets and variables → Actions)

DO_SSH_KEY — your private SSH key (content)

DO_HOST — Droplet public IP

DO_USER — root (or your admin user)

DOCKERHUB_USERNAME — your Docker Hub username

DOCKERHUB_TOKEN — Docker Hub access token

(If using S3) AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, and either MODEL_BASE_URL or specific model URLs

B) What .github/workflows/deploy.yml does

Checkout repo

SSH agent with DO_SSH_KEY

Docker Hub login

SSH to Droplet and:

docker pull <DOCKERHUB_USERNAME>/energy404-backend:latest

docker pull <DOCKERHUB_USERNAME>/energy404-frontend:latest

Stop & remove old containers (ignore if missing)

Start new containers:

Backend: -p 8000:8000

Frontend: -p 8050:8050 with API_BASE_URL=http://<DROPLET_IP>:8000

docker ps for confirmation

C) Trigger a deploy

Push/merge to main

Watch Actions tab → on success:

Frontend: http://<DROPLET_IP>:8050

Backend docs: http://<DROPLET_IP>:8000/docs

7) Troubleshooting (common issues)

Frontend can’t reach backend

Check API_BASE_URL on frontend container (should be http://<DROPLET_IP>:8000 when running on host).

docker logs -f energy404_backend to ensure backend is up.

Exit code 137 (OOM Kill)

Droplet RAM too small for your models.

Fix: reduce models / increase RAM / keep models on S3 and load selectively (final approach).

Platform/manifest mismatch

Build images for linux/amd64 (what Droplets use).

On Apple Silicon, avoid pushing arm64 images unless the server is arm64 too.

Models not found

Ensure /app/models_local_backup/*.pkl exists inside backend container.

If host mount: files must exist at /opt/energy404_models on the Droplet.

Ports closed

Open 22/8000/8050 in DO firewall or UFW.

Check port usage: ss -tulpn | grep ':8000\|:8050'.

8) Quick verification checklist

 docker compose up --build works locally (:8050 and :8000/docs open).

 Images visible on Docker Hub.

 Droplet has Docker installed and can pull images.

 Models available (S3 or /opt/energy404_models).

 GitHub Secrets added.

 Action green; containers Up on the Droplet.

9) Optional: Production compose (with model mount on Droplet)

Create docker-compose.prod.yml on the Droplet:

version: "3.9"
services:
  backend:
    image: <DOCKERHUB_USERNAME>/energy404-backend:latest
    container_name: energy404_backend
    ports: ["8000:8000"]
    restart: unless-stopped
    volumes:
      - /opt/energy404_models:/app/models_local_backup:ro

  frontend:
    image: <DOCKERHUB_USERNAME>/energy404-frontend:latest
    container_name: energy404_frontend
    ports: ["8050:8050"]
    restart: unless-stopped
    environment:
      - API_BASE_URL=http://localhost:8000


Run:

docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps

10) Why we chose this architecture

Simple for uni projects: one Droplet, two containers.

Fast deploys: small app images; models stored independently.

More reliable: lazy-loading avoids big startup spikes; keeping models out of the image avoids huge pulls & disk bloat.

Easy rollback: retag or pull previous versions.
