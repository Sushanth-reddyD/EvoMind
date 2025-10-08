# Deployment Guide

## Local Development

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

```bash
# Clone repository
git clone https://github.com/Sushanth-reddyD/EvoMind.git
cd EvoMind

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Locally

#### CLI Mode
```bash
# Submit a task
python -m evomind.cli submit "Parse JSON data"

# List tools
python -m evomind.cli list-tools

# View metrics
python -m evomind.cli metrics
```

#### API Mode
```bash
# Start server
python -m evomind.api

# In another terminal, test the API
curl http://localhost:8000/health
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pip install pytest-cov
pytest --cov=evomind --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v
```

## Docker Deployment

### Build Image

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY evomind/ ./evomind/
COPY pyproject.toml .

# Create non-root user
RUN useradd -m -u 1000 evomind && \
    chown -R evomind:evomind /app
USER evomind

# Environment
ENV EVOMIND_LOG_LEVEL=INFO
ENV EVOMIND_SANDBOX_MEMORY_MB=512

# Expose port
EXPOSE 8000

# Run API server
CMD ["python", "-m", "evomind.api"]
EOF

# Build
docker build -t evomind:latest .

# Run
docker run -p 8000:8000 evomind:latest
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  evomind-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - EVOMIND_LOG_LEVEL=INFO
      - EVOMIND_SANDBOX_MEMORY_MB=512
      - EVOMIND_MAX_RETRIES=3
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  # Optional: Add Redis for shared state
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Kubernetes Deployment

### Basic Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: evomind-api
  labels:
    app: evomind
spec:
  replicas: 3
  selector:
    matchLabels:
      app: evomind
  template:
    metadata:
      labels:
        app: evomind
    spec:
      containers:
      - name: evomind
        image: evomind:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: EVOMIND_LOG_LEVEL
          value: "INFO"
        - name: EVOMIND_SANDBOX_MEMORY_MB
          value: "512"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: evomind-service
spec:
  selector:
    app: evomind
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s/deployment.yaml
```

### ConfigMap for Configuration

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: evomind-config
data:
  config.yaml: |
    confidence_threshold: 0.75
    max_retries: 3
    sandbox_cpu_limit: 30
    sandbox_memory_mb: 512
    log_level: INFO
```

### Persistent Storage for Registry

```yaml
# k8s/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: evomind-registry
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

Update deployment to use PVC:
```yaml
volumes:
- name: registry
  persistentVolumeClaim:
    claimName: evomind-registry

volumeMounts:
- name: registry
  mountPath: /app/data/registry
```

## Production Considerations

### Security

1. **Use Secrets for Sensitive Data**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: evomind-secrets
type: Opaque
stringData:
  llm-api-key: "your-api-key-here"
```

2. **Network Policies**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: evomind-netpol
spec:
  podSelector:
    matchLabels:
      app: evomind
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
```

3. **Pod Security Policies**
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: evomind-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

### Monitoring

1. **Prometheus Metrics**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: evomind-metrics
  labels:
    app: evomind
spec:
  ports:
  - name: metrics
    port: 9090
    targetPort: 9090
  selector:
    app: evomind
```

2. **Service Monitor**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: evomind-monitor
spec:
  selector:
    matchLabels:
      app: evomind
  endpoints:
  - port: metrics
    interval: 30s
```

### Scaling

1. **Horizontal Pod Autoscaler**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: evomind-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: evomind-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Logging

1. **Structured Logging Configuration**
```bash
export EVOMIND_LOG_STRUCTURED=true
export EVOMIND_LOG_LEVEL=INFO
```

2. **Log Aggregation** (Fluentd/Loki)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/evomind-*.log
      pos_file /var/log/fluentd-evomind.pos
      tag evomind.*
      <parse>
        @type json
        time_key timestamp
        time_format %Y-%m-%dT%H:%M:%S.%L
      </parse>
    </source>
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `EVOMIND_CONFIDENCE_THRESHOLD` | Planning confidence threshold | `0.7` |
| `EVOMIND_MAX_RETRIES` | Maximum retry attempts | `3` |
| `EVOMIND_LLM_PROVIDER` | LLM provider (openai, anthropic) | `openai` |
| `EVOMIND_LLM_MODEL` | LLM model name | `gpt-4` |
| `EVOMIND_LLM_API_KEY` | LLM API key | - |
| `EVOMIND_SANDBOX_CPU_LIMIT` | CPU time limit (seconds) | `30` |
| `EVOMIND_SANDBOX_MEMORY_MB` | Memory limit (MB) | `512` |
| `EVOMIND_SANDBOX_TIMEOUT` | Wall clock timeout (seconds) | `60` |
| `EVOMIND_LOG_LEVEL` | Log level (DEBUG, INFO, WARN, ERROR) | `INFO` |
| `EVOMIND_LOG_STRUCTURED` | Use structured JSON logging | `false` |
| `EVOMIND_API_HOST` | API server host | `0.0.0.0` |
| `EVOMIND_API_PORT` | API server port | `8000` |

## Health Checks

### Liveness Probe
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

### Readiness Probe
```bash
curl http://localhost:8000/
# Expected: {"name": "EvoMind Agent API", "version": "0.1.0", "status": "running"}
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Reduce `EVOMIND_SANDBOX_MEMORY_MB`
   - Increase pod memory limits
   - Monitor tool execution patterns

2. **Slow Response Times**
   - Check tool registry size
   - Monitor sandbox execution times
   - Increase replicas with HPA

3. **Tool Creation Failures**
   - Check logs for validation errors
   - Review policy restrictions
   - Verify LLM API connectivity

### Debug Mode

```bash
export EVOMIND_LOG_LEVEL=DEBUG
python -m evomind.api
```

## Backup and Recovery

### Registry Backup
```bash
# Backup
tar -czf registry-backup-$(date +%Y%m%d).tar.gz ~/.evomind/registry/

# Restore
tar -xzf registry-backup-20240101.tar.gz -C ~/.evomind/
```

### Database Backup (if using external DB)
```bash
# PostgreSQL
pg_dump evomind > evomind-backup-$(date +%Y%m%d).sql

# Restore
psql evomind < evomind-backup-20240101.sql
```

## Performance Tuning

### Optimization Tips

1. **Tool Caching**: Frequently used tools are cached
2. **Parallel Execution**: Independent tools can run in parallel
3. **Batch Processing**: Use batch endpoints for multiple requests
4. **Resource Limits**: Tune based on workload

### Recommended Settings

**Development**:
- Replicas: 1
- Memory: 512MB
- CPU: 500m

**Production**:
- Replicas: 3-10 (with HPA)
- Memory: 1-2GB
- CPU: 1-2 cores

**High Load**:
- Replicas: 10+ (with HPA)
- Memory: 2-4GB
- CPU: 2-4 cores
- Consider microVM isolation (Firecracker)
