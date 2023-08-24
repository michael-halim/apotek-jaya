## Quickstart

Clone the project

```bash
  git clone https://github.com/michael-halim/apotek-jaya
```

Remove `.example` from `.env.dev.db.example`, `.env.dev.example`, `.env.prod.example`, `.env.prod.db.example` and set the credentials

Run Project in Development Mode

```bash
make run-dev
```

Start Project in Production Mode

```bash
make run-prod
```

## Other Commands

| Make Command | Description |
| :-------- | :------- |
| `make run-dev-su` | Running Development Django Application and Create Super User |
| `make create-dev-su` | Create Super User in Development Django Application |
| `make restart-dev-db` | Restarting Development Database |
| `make migrate-dev-db` | Migrating Development Database |
| `make run-dev-su` | Running Development Django Application and Create Super User |
| `make stop-dev` | Stopping Django Application in Development |
| `make run-dev-su` | Running Development Django Application and Create Super User |
| `make stop-dev-v` | Stopping Django Application in Development with Volumes |
| `make stop-prod` | Stopping Django Application in Production |
| `make stop-prod-v` | Stopping Django Application in Production with Volumes |