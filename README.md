# FastApi-Abstract

This is an abstract FastAPI project that includes key technologies like Redis, Celery, SQLAlchemy (for database), MinIO (for file storage), and JWT-based authentication. The project is designed to demonstrate an architecture that integrates these technologies.

## Features:
- **FastAPI**: High-performance web framework for building APIs.
- **Celery**: Asynchronous task queue to handle background tasks.
- **Redis**: In-memory data store used for caching, task queue backend, and session management.
- **MinIO**: Object storage service, used here for managing file uploads.
- **JWT Authentication**: Secure authentication mechanism using JSON Web Tokens.

## Prerequisites:
Before you can run the project, you will need the following:

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Setup Instructions:

### 1. Clone the repository
```bash 
  git https://github.com/Gor903/FastApi-Abstract.git
  cd FastApi-Abstract
```

### 2. Setup the .env
Copy the .env.example to .env
```bash
  cp .env.example .env
```
Update values as U want.

### 3. Run the project
```bash
  docker compose up --build
```

## Useful links
 - **Swagger**: http://0.0.0.0:8000/docs
### Documentation
 - **Docker**: https://docs.docker.com/get-started/
 - **Redis**: https://redis.io/docs/latest/
 - **Celery**: https://docs.celeryq.dev/en/stable/getting-started/introduction.html
 - **MinIO**: https://min.io/docs/kes/