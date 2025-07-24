# prompt-lab

Self-hosted service using Docker with PostgreSQL database.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

### 1. Start the PostgreSQL database

```bash
docker-compose up -d
```

This will:
- Start a PostgreSQL 15 container
- Create the `prompt_lab` database
- Run the initialization script automatically
- Mount data volume to `./postgres_data` for persistence

### 2. Database Connection

- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `prompt_lab`
- **Username**: `postgres`
- **Password**: `postgres`
- **Connection URL**: `postgresql://postgres:postgres@localhost:5432/prompt_lab`

### 3. Database Schema

The initialization script creates:
- `team` table with UUID primary key
- `user` table with UUID primary key and foreign key to team
- Required indexes for performance
- pgcrypto extension for UUID generation
- Default team entry

### 4. Stop the database

```bash
docker-compose down
```

### 5. Reset database (delete all data)

```bash
docker-compose down -v
sudo rm -rf postgres_data
docker-compose up -d
```

## Environment Variables

You can create a `.env` file to customize database settings:

```env
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/prompt_lab
```

## Health Check

The PostgreSQL container includes a health check that verifies the database is ready to accept connections.

## Data Persistence

Database data is stored in the `./postgres_data` directory and will persist between container restarts.