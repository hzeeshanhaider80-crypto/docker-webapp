cd ~/docker-webapp
cat > README.md <<'EOF'
# 🐳 Dockerized Web App with CI/CD Pipeline

A multi-container web application (**Flask + Redis + Nginx**) packaged with **Docker**, run with **Docker Compose**, and deployed automatically to **AWS EC2** by a **GitHub Actions** CI/CD pipeline.

Every `git push` to `main` automatically **tests**, **builds** and **deploys** the app, with no manual steps.

---

## 📌 Project Overview

| | |
|---|---|
| **Goal** | Automate the full path from code change to running application |
| **App** | Python Flask web app with a visit counter stored in Redis |
| **Containers** | 3: `web` (Flask + Gunicorn), `redis` (database), `nginx` (reverse proxy) |
| **Registry** | GitHub Container Registry (GHCR) |
| **Server** | AWS EC2 (Ubuntu 24.04) running Docker |
| **CI/CD** | GitHub Actions: Test → Build & Push → Deploy |

---

## 🏗️ Architecture

```
 Developer: git push
      │
      ▼
 GitHub Actions ──► 1. TEST (pytest) ──► 2. BUILD image ──► push to GHCR (ghcr.io)
                                                                  │
                     3. DEPLOY: SSH into EC2 → docker compose pull + up
                                                                  ▼
 ┌──────────────── AWS EC2 (Ubuntu + Docker) ──────────────────────────┐
 │  Browser ──:80──► [ nginx ] ──► [ web (Flask) :5000 ] ──► [ redis ] │
 │                               private Docker network     (volume)  │
 └─────────────────────────────────────────────────────────────────────┘
```

- **Only Nginx is exposed** to the internet (port 80). The app and Redis are reachable only on Docker's private network.
- **Redis data is stored in a Docker volume**, so it survives container restarts and redeployments.

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| Application | Python 3.12, Flask, Gunicorn |
| Database | Redis 7 |
| Containers | Docker, Docker Compose |
| Reverse proxy | Nginx |
| CI/CD | GitHub Actions |
| Image registry | GitHub Container Registry (GHCR) |
| Cloud | AWS EC2 (Ubuntu 24.04) |
| Testing | pytest |

---

## ✨ Key Features

- **Multi-container setup** with Docker Compose (app, database, reverse proxy)
- **Optimized Dockerfile**: slim base image, layer caching, no cache files
- **Security**: app runs as a **non-root user**; only Nginx is publicly exposed
- **Health checks** for the app and Redis; containers start in the correct order
- **Persistent data** using a named Docker volume
- **Automatic restart** of crashed containers (`restart: unless-stopped`)
- **3-stage CI/CD pipeline**: failing tests stop the deployment
- **Versioned images** tagged with the Git commit ID, so **one-command rollback** is possible
- **Post-deploy health check**: the deploy fails if the app doesn't become healthy

---

## 📂 Project Structure

```
docker-webapp/
├── app/
│   ├── app.py                # Flask application (routes: /, /health, /api/info)
│   ├── templates/index.html  # Web page
│   ├── test_app.py           # Automated tests (pytest)
│   ├── requirements.txt      # Runtime dependencies
│   ├── requirements-dev.txt  # Test dependencies
│   ├── Dockerfile            # Builds the app image
│   └── .dockerignore         # Files excluded from the image
├── nginx/
│   └── default.conf          # Reverse proxy configuration
├── scripts/
│   └── deploy.sh             # Deploys a given image version + health check
├── .github/workflows/
│   └── ci-cd.yml             # CI/CD pipeline
├── docker-compose.yml        # Defines all 3 containers
└── README.md
```

---

## 🔄 CI/CD Pipeline

| Stage | What happens | Runs on |
|---|---|---|
| **1. Test** | Installs dependencies and runs `pytest` | Every push and pull request |
| **2. Build & Push** | Builds the Docker image and pushes it to GHCR with two tags: the commit ID and `latest` | Push to `main` only |
| **3. Deploy** | Connects to EC2 over SSH, syncs the code, pulls the new image, restarts the containers and runs a health check | Push to `main` only |

If any stage fails, the following stages are skipped, so **broken code never reaches the server**.

---

## 🚀 Run It Locally

**Requirements:** Docker and Docker Compose.

```bash
# Clone the repository
git clone https://github.com/<your-username>/docker-webapp.git
cd docker-webapp

# Build and start all containers
docker compose up -d --build

# Check status (web and redis should be "healthy")
docker compose ps
```

Then open **http://localhost** in your browser.

**Run the tests** (no Python installation needed):

```bash
docker run --rm -v "$PWD/app":/app -w /app python:3.12-slim \
  sh -c "pip install -q -r requirements.txt -r requirements-dev.txt && pytest -v -p no:cacheprovider"
```

---

## ☁️ Deployment Setup (AWS EC2)

1. Launch an **Ubuntu 24.04 EC2** instance. Security group: allow **SSH (22)** and **HTTP (80)**.
2. Install Docker on the server: `curl -fsSL https://get.docker.com | sudo sh`
3. Create a deploy SSH key on the server and add its public key to `~/.ssh/authorized_keys`.
4. Add these **GitHub repository secrets**:

| Secret | Value |
|---|---|
| `EC2_HOST` | Public IP address of the EC2 instance |
| `EC2_SSH_KEY` | Private deploy key |

5. Push to `main`. The pipeline deploys automatically.
6. After the first build, set the GHCR package visibility to **Public** so the server can pull the image.

---

## ⏪ Rollback

Every image is tagged with its commit ID, so you can redeploy any previous version:

```bash
git log --oneline                      # find an older commit ID (first 7 characters)
cd ~/prod/docker-webapp
bash scripts/deploy.sh ghcr.io/<your-username>/docker-webapp:<commit-id>
```

---

## 🧰 Useful Commands

```bash
docker compose ps                              # container status
docker compose logs -f web                     # live app logs
docker compose exec redis redis-cli get visits # read the counter from Redis
docker compose up -d --scale web=3             # run 3 app containers (load balanced by Nginx)
docker compose down                            # stop containers (data kept)
docker compose down -v                         # stop containers and delete data
```

---

## 📚 What I Learned

- Writing Dockerfiles with best practices (layer caching, non-root user, health checks)
- Running multi-container applications with Docker Compose (networks, volumes, dependencies)
- Using Nginx as a reverse proxy in front of an application
- Building a CI/CD pipeline with GitHub Actions (test, build, deploy)
- Publishing images to a container registry (GHCR) with versioned tags
- Deploying to AWS EC2 over SSH and rolling back safely
- Debugging containers with logs, health checks and `docker compose ps`

---

## 👤 Author

**Your Name**: Junior DevOps Engineer
GitHub: [github.com/<your-username>](https://github.com/<your-username>)
EOF
