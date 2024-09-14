PYTHON = python3
PROTO_FILES = spaceship.proto
PROTOC_FLAGS = -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=.

all: install proto create-env setup-postgres

install:
	pip install -r requirements.txt

proto:
	cd src/ && $(PYTHON) $(PROTOC_FLAGS) $(PROTO_FILES)

setup-postgres: create-env
	docker-compose -f src/db_spaceship.yml up

create-env:
	@echo "DB_HOST=localhost" > .env
	@echo "DB_PORT=8080" >> .env
	@echo "DB_USER=spaceships" >> .env
	@echo "DB_PASS=12345" >> .env
	@echo "DB_NAME=storage" >> .env

clean:
	docker-compose -f src/db_spaceship.yml down
	rm -rf *.pyi *.pyc .env src/spaceship_pb2.py src/spaceship_pb2.pyi src/spaceship_pb2_grpc.py src/__pycache__