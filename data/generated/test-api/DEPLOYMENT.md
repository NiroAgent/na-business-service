# Deployment Guide

## Project: test-api
Version: 1.0.0
Target: staging

## Quick Start

### Local Development
```bash
docker build -t test-api .
docker run -p 8000:8000 test-api
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/
```

## CI/CD Pipeline

The project includes GitHub Actions workflow for automated testing and deployment.

### Pipeline Stages:
1. **Test** - Runs unit tests and linting
2. **Build** - Builds Docker image
3. **Deploy** - Deploys to target environment

## Monitoring

### Prometheus Metrics
- Endpoint: `/metrics`
- Scrape interval: 15s

### Grafana Dashboard
Import `monitoring/dashboard.json` into Grafana

### Alerts
- High Error Rate (>5%)
- High Response Time (>1s)
- Service Down

## Rollback Procedures

### Docker Rollback
```bash
docker pull docker.io/test-api:previous-version
docker run -p 8000:8000 docker.io/test-api:previous-version
```

### Kubernetes Rollback
```bash
kubectl rollout undo deployment/test-api -n default
```

## Health Checks
- Endpoint: `/health`
- Expected response: 200 OK

## Environment Variables
- `ENVIRONMENT`: staging
- Additional variables in `.env` file

## Support
For issues, check logs:
```bash
kubectl logs -f deployment/test-api -n default
```
