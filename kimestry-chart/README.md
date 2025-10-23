# Kimestry-Benchmark Helm Chart

A simple Helm chart to deploy Kimestry-Benchmark - Schema and Column Matching System with two pods: backend and frontend.

## Prerequisites

- Kubernetes 1.19+
- Helm 3+
- An external PostgreSQL database accessible by the cluster
- A Kubernetes secret containing the database connection string

## Installing the Chart

First, create a secret with your PostgreSQL connection string:

```bash
kubectl create secret generic kimestry-db-secret \
  --from-literal=connection-string="postgresql://username:password@your-postgres-host:5432/kimestry"
```

Then install the chart:

```bash
helm install kimestry-benchmark ./kimestry-chart
```

To customize the installation, create a `values.yaml` file:

```bash
helm install kimestry-benchmark ./kimestry-chart -f your-values.yaml
```

## Configuration

The following table lists the configurable parameters of the kimestry-benchmark chart and their default values.

### Backend Configuration

| Parameter                    | Description                                         | Default                        |
| ---------------------------- | --------------------------------------------------- | ------------------------------ |
| `backend.replicaCount`       | Number of backend replicas                          | `1`                           |
| `backend.image.repository`   | Backend image repository                            | `kimestry-benchmark-backend`  |
| `backend.image.tag`          | Backend image tag                                   | `latest`                      |
| `backend.image.pullPolicy`   | Backend image pull policy                           | `IfNotPresent`                |
| `backend.service.type`       | Backend service type                                | `ClusterIP`                   |
| `backend.service.port`       | Backend service port                                | `8000`                        |
| `backend.resources`          | Backend resource requests and limits                | (see values.yaml)             |

### Frontend Configuration

| Parameter                     | Description                                         | Default                         |
| ----------------------------- | --------------------------------------------------- | ------------------------------- |
| `frontend.replicaCount`       | Number of frontend replicas                         | `1`                            |
| `frontend.image.repository`   | Frontend image repository                           | `kimestry-benchmark-frontend`  |
| `frontend.image.tag`          | Frontend image tag                                  | `latest`                       |
| `frontend.image.pullPolicy`   | Frontend image pull policy                          | `IfNotPresent`                 |
| `frontend.service.type`       | Frontend service type                               | `LoadBalancer`                 |
| `frontend.service.port`       | Frontend service port                               | `80`                           |
| `frontend.resources`          | Frontend resource requests and limits               | (see values.yaml)              |

### Ingress Configuration

| Parameter                    | Description                                         | Default                        |
| ---------------------------- | --------------------------------------------------- | ------------------------------ |
| `ingress.enabled`            | Enable ingress resource                             | `false`                        |
| `ingress.className`          | Ingress class name                                  | `""`                           |
| `ingress.annotations`        | Ingress annotations                                 | `{}`                          |
| `ingress.hosts`              | Ingress hosts configuration                         | (see values.yaml)              |
| `ingress.tls`                | Ingress TLS configuration                          | `[]`                          |

### Database Configuration

| Parameter                    | Description                                         | Default                        |
| ---------------------------- | --------------------------------------------------- | ------------------------------ |
| `database.secretName`        | Name of the secret containing the DB connection string | `kimestry-db-secret`         |

## Uninstalling the Chart

To uninstall/delete the `kimestry-benchmark` release:

```bash
helm delete kimestry-benchmark
```

## Values File Example

```yaml
backend:
  image:
    repository: myregistry/kimestry-benchmark-backend
    tag: v1.0.0
  service:
    type: ClusterIP
    port: 8000

frontend:
  image:
    repository: myregistry/kimestry-benchmark-frontend
    tag: v1.0.0
  service:
    type: LoadBalancer
    port: 80

ingress:
  enabled: true
  hosts:
    - host: kimestry.example.com
      paths:
        - path: /
          pathType: Prefix
```