# Kimestry Helm Chart

This Helm chart deploys Kimestry - an LLM-powered system for matching Excel tables to database schemas and columns.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- A provisioned PersistentVolume for storage (if persistence is enabled)
- An external PostgreSQL database accessible from the cluster

## Installing the Chart

1. Install the chart with default values:
```bash
helm install kimestry ./kimestry-chart
```

Or install with custom values:
```bash
helm install kimestry ./kimestry-chart -f my-values.yaml
```

## Configuration

The following table lists the configurable parameters of the Kimestry chart and their default values.

### Database parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `database.host` | PostgreSQL host | `"your-postgres-host"` |
| `database.port` | PostgreSQL port | `5432` |
| `database.database` | PostgreSQL database name | `"kimestry"` |
| `database.username` | PostgreSQL username | `"postgres"` |
| `database.password` | PostgreSQL password | `"your-password"` |
| `database.sslMode` | PostgreSQL SSL mode | `"prefer"` |

### Backend parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.replicaCount` | Number of backend replicas | `1` |
| `backend.image.repository` | Backend image repository | `"kimestry-backend"` |
| `backend.image.tag` | Backend image tag | `"latest"` |
| `backend.service.port` | Backend service port | `8000` |
| `backend.resources` | CPU/Memory resource requests/limits | See values.yaml |

### Frontend parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.replicaCount` | Number of frontend replicas | `1` |
| `frontend.image.repository` | Frontend image repository | `"kimestry-frontend"` |
| `frontend.image.tag` | Frontend image tag | `"latest"` |
| `frontend.service.type` | Frontend service type | `LoadBalancer` |
| `frontend.service.port` | Frontend service port | `80` |

## Uninstalling the Chart

To uninstall/delete the `kimestry` release:
```bash
helm delete kimestry
```

## Local Development Setup

For local development with Docker Compose (requires external PostgreSQL):

```bash
# Make sure to update POSTGRES_CONNECTION_STRING in docker-compose.yml first
docker-compose up --build
```

This uses Dockerfile.backend and Dockerfile.frontend from the project root directory.
The application will be available at:
- Frontend: http://localhost
- Backend API: http://localhost/api (proxied to backend service)
- Backend API Docs: http://localhost/api/docs

## Quick Kubernetes Deployment

For quick Kubernetes deployment using the provided script:

```bash
# Run from project root
deploy-kimestry.bat
```

This will deploy the application using the Helm chart to a Kubernetes cluster.

## OpenShift Deployment

To deploy to OpenShift Container Platform (OCP):

1. Using Helm (recommended):
```bash
# From project root
helm install kimestry ./kimestry-chart --create-namespace --namespace kimestry
```

2. Alternatively, you can use `oc` CLI directly:
```bash
# Create the namespace/project
oc new-project kimestry

# Install using Helm with OpenShift
helm install kimestry ./kimestry-chart --namespace kimestry
```

3. If you need to customize database settings for OpenShift:
```bash
# Create a custom values file (e.g., openshift-values.yaml)
# Then install with custom values:
helm install kimestry ./kimestry-chart -f openshift-values.yaml --create-namespace --namespace kimestry
```

Make sure your OpenShift cluster has access to an external PostgreSQL database, 
or deploy PostgreSQL separately in your cluster before deploying Kimestry.

## Building Custom Images

To build custom Docker images:

Backend:
```bash
docker build -f Dockerfile.backend -t kimestry-backend .
```

Frontend:
```bash
docker build -f Dockerfile.frontend -t kimestry-frontend .
```

## Architecture

The application consists of:
- **Frontend**: React application that provides the user interface
- **Backend**: FastAPI application that processes requests and manages the pipeline logic
- **Database**: PostgreSQL database that stores pipeline results and benchmark data

## Accessing the Services

Once deployed, you can access:
- The frontend UI through the LoadBalancer service
- The backend API at `http://<backend-service>:8000`
- The backend API documentation at `http://<backend-service>:8000/docs`

To get the frontend URL:
```bash
export FRONTEND_URL=$(kubectl get svc --namespace <namespace> kimestry-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Frontend URL: http://$FRONTEND_URL"
```

## Troubleshooting

1. Check if all pods are running:
```bash
kubectl get pods
```

2. Check logs for issues:
```bash
kubectl logs -l app.kubernetes.io/name=kimestry-backend
kubectl logs -l app.kubernetes.io/name=kimestry-frontend
```

3. If using minikube or kind, you might need to use NodePort or port forwarding instead of LoadBalancer:
```bash
kubectl port-forward svc/kimestry-frontend 3000:80
```