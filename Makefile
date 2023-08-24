run-dev:
	@echo "Running Development Django Application"
	docker-compose up -d --build

run-dev-su:
	@echo "Running Development Django Application and Create Super User"
	docker-compose up -d --build
	docker-compose exec web python manage.py makemigrations
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py createsuperuser --noinput

create-dev-su:
	@echo "Create Super User in Development Django Application"
	docker-compose exec web python manage.py createsuperuser --noinput

restart-dev-db:
	@echo "Restarting Development Database"
	docker-compose exec web python manage.py flush --no-input
	docker-compose exec web python manage.py migrate

migrate-dev-db:
	@echo "Migrating Development Database"
	docker-compose exec web python manage.py makemigrations
	docker-compose exec web python manage.py migrate

stop-dev:
	@echo "Stopping Django Application in Development"
	docker-compose down

stop-dev-v:
	@echo "Stopping Django Application in Development with Volumes"
	docker-compose down -v

run-prod:
	@echo "Running Django Application in Production"
	docker-compose -f docker-compose.prod.yml up --build
	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
	docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear

stop-prod:
	@echo "Stopping Django Application in Production"
	docker-compose -f docker-compose.prod.yml down

stop-prod-v:
	@echo "Stopping Django Application in Production with Volumes"
	docker-compose -f docker-compose.prod.yml down -v