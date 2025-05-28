# Support Ticket Assignment System

## Project Overview

This project implements a scalable, concurrent Django-based API for a customer support platform. The system efficiently assigns batches of unassigned support tickets to agents, ensuring:

- No ticket is assigned to more than one agent.
- Agents can fetch up to 15 tickets assigned exclusively to them.
- The system handles thousands of concurrent agents fetching tickets without blocking.
- Admins can manage tickets (create, update, delete).
- Agents can only sell tickets assigned to them.

---

## Key Features

- **Ticket Assignment**: Automatically assigns batches of up to 15 tickets per agent on request.
- **Concurrency-safe**: Uses database transactions and locking to prevent race conditions.
- **REST API**: Built with Django REST Framework for clean and secure endpoints.
- **Role-based Access Control**: Admins manage tickets; agents fetch and sell assigned tickets.
- **Containerized**: Includes Docker and Docker Compose setup for easy deployment.
- **Tested**: Includes API tests covering correctness and concurrency.

---

## Architecture

- **Backend**: Django 4.x, Django REST Framework
- **Database**: PostgreSQL
- **Containerization**: Docker and Docker Compose
- **Concurrency Control**: Database transactions with `select_for_update(skip_locked=True)`

### Entity Relationship Diagram (ERD)

![ERD](erd/Support%20Tickets%20ERD.png)  
*(See `/erd/Support Tickets ERD.png` for detailed schema diagram)*

---

## Postman Collection

A Postman collection containing all the API endpoints with example requests and responses:

- `postman/Support Ticket API.postman_collection.json`

You can import this collection into Postman by:

1. Opening Postman
2. Clicking **Import** → **Upload Files**
3. Selecting the JSON file above

This collection helps you quickly test the API endpoints including admin ticket management, agent ticket fetching, and selling tickets.

## API Endpoints

### Admin Endpoints (Require Admin Authentication)

- `GET /api/users/` — Get users
- `GET /api/users/{id}/` — Get user
- `POST /api/users/` — Create users
- `PUT /api/users/{id}/` — Update users
- `PATCH /api/users/{id}/` — Partial Update users
- `DELETE /api/users/{id}/` — Delete users

- `POST /api/tickets/` — Create ticket
- `PUT /api/tickets/{id}/` — Update ticket
- `PATCH /api/tickets/{id}/` — Partial Update ticket
- `DELETE /api/tickets/{id}/` — Delete ticket

### Agent Endpoints

- `GET /api/tickets/fetch-tickets/`  
  Fetches up to 15 tickets assigned to the authenticated agent.  
  - If agent has <15 tickets, assigns more unassigned tickets up to 15.
  - Returns an empty list if no tickets available.

- `POST /api/tickets/{id}/sell/`  
  Marks a ticket as sold. Only allowed if ticket is assigned to the authenticated agent.

---

## Getting Started

### Prerequisites

- Docker & Docker Compose installed
- `.env` file with environment variables

### Setup & Run

```bash
git clone https://github.com/YasminaMohamed99/Assigning-Support-Tickets-.git
cd support-system

Ensure that Docker is running on your machine. If not, open Docker Desktop.

# Build and start containers
docker-compose up --build

# Run migrations (inside web container)
docker-compose exec web python manage.py migrate

# Create superuser for admin access
docker-compose exec web python manage.py createsuperuser

# To start the application
docker-compose up
