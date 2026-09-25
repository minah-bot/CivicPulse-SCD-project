# ADR 001: Frontend Architecture

- Status: Accepted
- Date: 2026-09-25

## Context

CivicPulse requires a web frontend for submitting complaints, viewing complaints, updating complaint status, and viewing statistics.

The frontend must be maintainable and communicate with the backend through the agreed REST API contract.

## Decision

The CivicPulse frontend uses React with TypeScript and Vite.

React Router is used for client-side navigation between:

- Submit Complaint
- Dashboard
- Statistics

API communication is centralized in `src/api/client.ts`.

Shared API models and status transition rules are defined in `src/api/types.ts`.

## Consequences

This structure keeps UI components separate from API communication and shared data types.

TypeScript provides compile-time checking for API-related data structures.

React Router allows the application to provide separate pages without requiring full page reloads.
