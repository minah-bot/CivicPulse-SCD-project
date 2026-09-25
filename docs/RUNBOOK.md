# CivicPulse Runbook

## 1. Project Overview

CivicPulse is a civic complaint management application.

The frontend is implemented using React, TypeScript, Vite, React Router, and Nginx.

## 2. Frontend Development

Frontend source code:

frontend/

Install dependencies:

npm ci

Start development server:

npm run dev

Build production version:

npm run build

## 3. Frontend Routes

/
    Submit Complaint

/dashboard
    Dashboard

/stats
    Statistics

## 4. API

The frontend uses the following API contract:

POST /api/complaints
GET /api/complaints
GET /api/complaints/{id}
PATCH /api/complaints/{id}/status
GET /api/stats
GET /api/meta/providers
GET /api/health

## 5. Docker

Frontend Docker files:

frontend/Dockerfile
frontend/.dockerignore
docker-compose.yml

Build the frontend image:

docker build -t civicpulse-frontend ./frontend

Run the frontend container:

docker run --rm -p 5173:80 civicpulse-frontend

## 6. Docker Compose

Build and start:

docker compose build
docker compose up

Stop:

docker compose down

## 7. Kubernetes

Kubernetes files are located in:

k8s/

Resources:

frontend-deployment.yaml
frontend-service.yaml
kustomization.yaml

Apply:

kubectl apply -k k8s/

Check deployment:

kubectl get deployments

Check pods:

kubectl get pods

Check service:

kubectl get services

## 8. GitHub Actions

Frontend CI workflow:

.github/workflows/frontend-ci.yml

The workflow installs Node.js 22, runs npm ci, and verifies the production build.

## 9. Troubleshooting

Check Node.js:

node --version
npm --version

Check Docker:

docker --version
docker compose version

Check Kubernetes:

kubectl cluster-info
kubectl get nodes

## 10. Current Limitation

The frontend is designed against the agreed CivicPulse API contract.

Full API integration requires the backend implementation to be available and running.

Docker and Kubernetes deployment require the corresponding tools to be installed and configured.

## 11. Useful Git Commands

Check status:

git status

View recent commits:

git log --oneline -5

Push changes:

git push
