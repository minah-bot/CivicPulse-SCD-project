# ADR 002: Frontend Containerization

- Status: Accepted
- Date: 2026-09-25

## Context

The CivicPulse frontend needs a repeatable production deployment method.

The application is built into static frontend assets and does not require a Node.js runtime after the build is complete.

## Decision

The frontend uses a multi-stage Docker build.

The first stage uses Node.js to install dependencies and build the React application.

The second stage uses Nginx to serve the generated production files.

Docker Compose is provided at the project root for local container orchestration.

Kubernetes manifests are provided under the `k8s/` directory for cluster deployment.

## Consequences

The production container does not need the Node.js runtime after the build stage.

Nginx provides a lightweight production web server.

The same frontend image can be used as the basis for containerized deployment.

Docker and Kubernetes configuration can be integrated with the backend when the backend implementation is available.
