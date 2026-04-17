# Deployments

This directory contains all deployment-related configurations and files.

## Structure

```
deployments/
├── docker/           # Docker-related files
│   ├── Dockerfile           # Standard CPU image
│   ├── Dockerfile.cuda      # NVIDIA GPU (CUDA) image
│   ├── docker-compose.yml   # Docker Compose configuration
│   └── .dockerignore        # Docker build context exclusions
│
└── monitoring/       # Monitoring stack (Prometheus + Grafana)
    ├── prometheus/
    │   └── prometheus.yml
    └── grafana/
        └── provisioning/
            ├── dashboards/
            └── datasources/
```

## Docker Usage

### Standard (CPU)

```bash
# Using Docker Compose from project root
docker compose up --build

# Or using the docker-compose in deployments/docker/
cd deployments/docker
docker compose up --build
```

### GPU (CUDA)

```bash
# Build CUDA image
docker build -f deployments/docker/Dockerfile.cuda -t yolo-toys:cuda .

# Run with GPU support
docker run --gpus all -p 8000:8000 yolo-toys:cuda
```

## Monitoring

To run with monitoring stack:

```bash
docker compose --profile monitoring up
```

Then access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (default admin/admin)
