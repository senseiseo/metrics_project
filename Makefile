.PHONY: help bash shell dbshell test test-record lint typecheck format check-migrations

DC = docker-compose
WEB = $(DC) exec web

help:
	@printf "Available targets:\n"
	@printf "  make bash               # shell inside web container\n"
	@printf "  make shell              # Django shell\n"
	@printf "  make dbshell            # database shell\n"
	@printf "  make test               # run all metrics tests\n"
	@printf "  make test-record        # run record creation tests\n"
	@printf "  make lint               # run flake8\n"
	@printf "  make typecheck          # run mypy\n"
	@printf "  make format             # run isort + black\n"
	@printf "  make check-migrations   # ensure migrations are not missing\n"

bash:
	$(WEB) bash

shell:
	$(WEB) python manage.py shell

dbshell:
	$(WEB) python manage.py dbshell

test:
	$(WEB) pytest apps/metrics/tests/ -v

test-record:
	$(WEB) pytest apps/metrics/tests/test_create_record.py -v

lint:
	$(WEB) flake8 .

typecheck:
	$(WEB) mypy .

format:
	$(WEB) isort .
	$(WEB) black .

check-migrations:
	$(WEB) python manage.py makemigrations --check --dry-run
