PYTHON = python3
PROTO_FILES = src/spaceship.proto
PROTOC_FLAGS = -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=.

all: install proto setup-postgres create-env

install:
	pip install -r requirements.txt

proto:
	$(PYTHON) $(PROTOC_FLAGS) $(PROTO_FILES)

setup-postgres: create-user create-db
	sudo -i -u postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE storage TO spaceships;"
	sudo -i -u postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON SCHEMA public TO spaceships;"

create-user:
	@if sudo -i -u postgres psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname='spaceships'" | grep -q 1; then \
		echo "User 'spaceships' already exists."; \
	else \
		sudo -i -u postgres psql -U postgres -c "CREATE USER spaceships WITH PASSWORD '12345';"; \
	fi

create-db:
	@if sudo -i -u postgres psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='storage'" | grep -q 1; then \
		echo "Database 'storage' already exists"; \
	else \
		sudo -i -u postgres psql -U postgres -c "CREATE DATABASE storage;";\
	fi

create-env:
	@echo "DB_HOST=localhost" > .env
	@echo "DB_PORT=5432" >> .env
	@echo "DB_USER=spaceships" >> .env
	@echo "DB_PASS=12345" >> .env
	@echo "DB_NAME=storage" >> .env

clean:
	rm -f *.pyi *.pyc __pycache__/* .env