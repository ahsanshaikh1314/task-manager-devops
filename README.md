# Task Manager — DevOps CSC418 Terminal Exam

## Architecture (3-Tier)
- **Frontend**: Nginx serving HTML/CSS/JS (Dockerfile.frontend)
- **Backend**: Node.js + Express REST API (Dockerfile.backend)
- **Database**: MongoDB 7.0 (official image)

## Quick Start (Docker Compose)

```bash
docker-compose up -d --build
```

- Frontend: http://localhost:80
- Backend API: http://localhost:3000
- Health check: http://localhost:3000/health

## Section A — Containerization

Build images separately:
```bash
docker build -f Dockerfile.backend  -t taskmanager-backend:latest .
docker build -f Dockerfile.frontend -t taskmanager-frontend:latest .
```

Run all services:
```bash
docker-compose up -d
docker-compose ps        # verify all running
docker-compose logs -f   # watch logs
```

## Section B — CI/CD (GitHub Actions)

Pipeline file: `.github/workflows/pipeline.yml`

Stages:
1. **Build** — installs deps, verifies files
2. **Test** — spins up MongoDB service, runs API health & CRUD tests
3. **Docker Build & Push** — builds both images, pushes to Docker Hub
4. **Deploy** — applies k8s manifests to AKS

Required GitHub Secrets:
| Secret | Value |
|--------|-------|
| `DOCKER_HUB_USERNAME` | Your Docker Hub username |
| `DOCKER_HUB_TOKEN` | Docker Hub access token |
| `AZURE_CREDENTIALS` | Azure service principal JSON |
| `AKS_RESOURCE_GROUP` | Your AKS resource group |
| `AKS_CLUSTER_NAME` | Your AKS cluster name |

## Section C — Kubernetes (AKS)

```bash
# Create AKS cluster (Azure CLI)
az aks create --resource-group myRG --name myAKS --node-count 2 --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group myRG --name myAKS

# Deploy
kubectl apply -f k8s/deployment.yaml

# Verify
kubectl get pods
kubectl get services

# Get public IP
kubectl get service taskmanager-frontend-service
```

## Section D — Selenium Tests

```bash
pip install selenium webdriver-manager
python selenium/test_taskmanager.py
```

Set `APP_URL` for remote testing:
```bash
APP_URL=http://<public-ip> python selenium/test_taskmanager.py
```

Tests:
1. Homepage loads correctly
2. Create a new task (form behaviour)
3. API response reflected in UI
4. Complete and Delete buttons work

## Project Structure
```
task-manager/
├── Dockerfile.backend      # Backend Docker image
├── Dockerfile.frontend     # Frontend (Nginx) Docker image
├── nginx.conf              # Nginx config (proxies /api/ → backend)
├── docker-compose.yml      # All 3 services
├── backend/
│   ├── server.js
│   └── package.json
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── k8s/
│   └── deployment.yaml     # PVC + MongoDB + Backend + Frontend + Services
├── selenium/
│   └── test_taskmanager.py # 4 Selenium test cases
└── .github/workflows/
    └── pipeline.yml        # GitHub Actions CI/CD
```


