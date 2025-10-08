# Docker Deployment Guide

This guide explains how to deploy the TestCase AI Agent using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ 
- Docker Compose 2.0+
- At least 2GB RAM available for the container
- Google Gemini API key

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd TestCaseAIAgent
```

### 2. Configure Environment

Copy the environment template and configure your API keys:

```bash
cp docker.env.template .env
```

Edit `.env` file and set your API keys:

```bash
# Required - Set your actual API key
GOOGLE_API_KEY=your_actual_gemini_api_key_here

# Optional - For enhanced search capabilities
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f testcase-ai-agent
```

### 4. Test the Application

```bash
# Run a quick test
docker-compose exec testcase-ai-agent python examples/basic_usage.py

# Or run the main application
docker-compose exec testcase-ai-agent python run.py
```

## Docker Commands

### Build and Run

```bash
# Build only
docker-compose build

# Build and start
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Development

```bash
# Run with debug mode
DEBUG_MODE=true docker-compose up

# View container logs
docker-compose logs testcase-ai-agent

# Execute commands in container
docker-compose exec testcase-ai-agent bash

# Restart service
docker-compose restart testcase-ai-agent
```

### Monitoring

```bash
# Check container status
docker-compose ps

# View resource usage
docker stats testcase-ai-agent

# Check health status
docker-compose exec testcase-ai-agent python -c "import sys; print('OK')"
```

## Configuration

### Environment Variables

All configuration is done through environment variables in the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | - | **Required** - Google Gemini API key |
| `TAVILY_API_KEY` | - | Optional - Tavily search API key |
| `GEMINI_MODEL_NAME` | `gemini-1.5-pro` | Gemini model to use |
| `GEMINI_TEMPERATURE` | `0.1` | Model temperature (0.0-1.0) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DEBUG_MODE` | `false` | Enable debug mode |
| `MAX_DOCUMENT_SIZE_MB` | `50` | Maximum document size |
| `SESSION_TIMEOUT_MINUTES` | `60` | Session timeout |

### Volumes

The following directories are mounted as volumes:

- `./data:/app/data` - Session data persistence
- `./output:/app/output` - Generated test case outputs
- `testcase-temp:/tmp/testcase_ai` - Temporary processing files

### Ports

- `8000:8000` - Main application port (if running as web service)

## Production Deployment

### Resource Limits

The Docker Compose configuration includes resource limits:

```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2.0'
    reservations:
      memory: 1G
      cpus: '1.0'
```

### Security

- Container runs as non-root user (`appuser`)
- Input validation and output sanitization enabled
- Health checks configured
- Resource limits applied

### Scaling

To run multiple instances:

```bash
# Scale to 3 instances
docker-compose up --scale testcase-ai-agent=3
```

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```bash
   ERROR: GOOGLE_API_KEY environment variable is not set!
   ```
   Solution: Set the `GOOGLE_API_KEY` in your `.env` file

2. **Out of Memory**
   ```bash
   Container killed due to memory limit
   ```
   Solution: Increase memory limits in `docker-compose.yml` or reduce `MAX_CONCURRENT_DOCUMENTS`

3. **Permission Denied**
   ```bash
   Permission denied: '/app/data'
   ```
   Solution: Ensure Docker has write permissions to mounted volumes

4. **Build Failures**
   ```bash
   Failed to build: No space left on device
   ```
   Solution: Clean up Docker images: `docker system prune -a`

### Debug Mode

Enable debug mode for detailed logging:

```bash
# In .env file
DEBUG_MODE=true
LOG_LEVEL=DEBUG
ENABLE_DETAILED_LOGGING=true

# Restart container
docker-compose restart testcase-ai-agent
```

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs testcase-ai-agent

# Follow logs in real-time
docker-compose logs -f testcase-ai-agent

# View last 100 lines
docker-compose logs --tail=100 testcase-ai-agent
```

## Performance Tuning

### Memory Optimization

```bash
# Reduce memory usage
MAX_CONCURRENT_DOCUMENTS=3
MAX_SESSION_MEMORY_SIZE=50
ENABLE_CACHING=false
```

### CPU Optimization

```bash
# Adjust worker threads
MAX_WORKER_THREADS=2
ENABLE_PARALLEL_PROCESSING=true
```

### Storage Optimization

```bash
# Reduce session timeout
SESSION_TIMEOUT_MINUTES=30
CACHE_TTL_SECONDS=1800
```

## Backup and Recovery

### Backup Data

```bash
# Backup session data
docker-compose exec testcase-ai-agent tar -czf /tmp/backup.tar.gz /app/data
docker cp testcase-ai-agent:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz
```

### Restore Data

```bash
# Restore session data
docker cp ./backup-20240101.tar.gz testcase-ai-agent:/tmp/
docker-compose exec testcase-ai-agent tar -xzf /tmp/backup-20240101.tar.gz -C /
```

## Integration

### With CI/CD

```yaml
# Example GitHub Actions
- name: Build and test
  run: |
    docker-compose build
    docker-compose run --rm testcase-ai-agent python -m pytest
```

### With Kubernetes

The Docker image can be deployed to Kubernetes using the included configuration or by adapting the Docker Compose setup.

## Support

For Docker-related issues:

1. Check the logs: `docker-compose logs testcase-ai-agent`
2. Verify environment variables: `docker-compose config`
3. Test the container: `docker-compose exec testcase-ai-agent python -c "import sys; print('OK')"`
4. Check resource usage: `docker stats testcase-ai-agent`

For additional help, refer to the main README.md or create an issue in the repository.

