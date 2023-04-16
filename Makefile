COMPOSE=docker-compose

start:
	$(COMPOSE) up -d

rebuild:
	$(COMPOSE) up --build -d --remove-orphans

logs:
	$(COMPOSE) logs --follow

stop:
	$(COMPOSE) down

start-db:
	$(COMPOSE) up -d db

stop-db:
	$(COMPOSE) up -d db

clean:
	$(COMPOSE) down --remove-orphans --volumes

migrate:
	alembic upgrade head

migrations:
	alembic revision --autogenerate
db-shell:
	PGPASSWORD=$(DB_PASSWORD) psql -U postgres $(DB_NAME) -h $(DB_HOST) -p $(DB_PORT)
