# GalacticSentinel 

Three thouthands years from today, the mankind now have such great technologies we couldn't even imagine. The mankind now continues to explore universe, and even managed to sully settle on several planets.However, not all inhabitants of space are fond of new neighbours. Gradiully, contacts with some civilization escalated into tense conflicts, and mankind drawn into endless intergalactic wars.

To protect the colonies, humans developen the "Galactic Sentinel" - a system, capable of detecting and classifiying spacecrafts, distinguishing between allies and enemies and finding impostors. "Galactic Sentinel" has become a reliable shield for humanity in the depths of space.

## Overview 

This project is designed to manage spaceship data and their crew members. It involves communication with a gRPC service to retrieve spaceship information and store it in a PostgreSQL database. The project consists of three main parts:

- **Protobuf Definitions:** Defines the data structures and gRPC service.

- **Python script server.py:**  Receives a `Coordinates` object that characterizes the coordinates of the constellation and returns from 1 to 10 Spaceship objects that characterize ships located within coordinates. 

- **Python script client.py:** Receives the sent `Spaceship` objects, validates the information about the ships, and inserts it into the database. All actions are detailed in the "Usage" section.

## Setup
Install the required Python packages using pip:
```sh
pip install -r requirements.txt
```

### How to compile .proto

You should run this command:

```sh
python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. spaceship.proto   
```
After that, server and client can be run. 

### How to run server and client

 You should run this command to run the server:
```sh
python3 reporting_server.py
```

From a different terminal, run the client with coordinates:
```sh
python3 reporting_client.py 17 45 40.0409 -29 00 28.118
```

### How to create DB

Log in to PostgreSQL:
```sh
sudo -i -u postgres
```

Run psql as postgres(superuser):
```sh
psql -U postgres
```

Create user:
```sh
CREATE USER spaceships WITH PASSWORD '12345';
```

Create database:
```sh
CREATE DATABASE storage;
```

Grant all privileges:
```sh
GRANT ALL PRIVILEGES ON DATABASE storage TO spaceships;
GRANT ALL PRIVILEGES ON SCHEMA public TO spaceships;
```

Exit:
```sh
\q 
exit
```

Create .env file with info about DATABASE: 
```sh
touch .env 
```
 
It must look like that inside : 
```env
DB_HOST = smth
DB_PORT = smth
DB_USER = smth
DB_PASS = smth
DB_NAME = smth
```
## Troubleshooting

- **gRPC Errors:** Ensure the gRPC server is running and accessible at localhost:50051.
- **Database Errors:** Verify your .env configuration and database connectivity.


## Usage
Start the server.
```sh
python3 server.py
```

From a different terminal, run the client:
```
python client.py <action> [<longitude_degrees> <longitude_minutes> <longitude_seconds> <latitude_degrees> <latitude_minutes> <latitude_seconds>]
```

### Arguments

- **action**: specifies the action to perform. It can be one of the following:
    - **scan**: Scans for spaceships within the specified coordinates and updates the database.
    - **list_traitors**: Lists all traitors (imposters) from the database.
    - **default**: Runs the default action, which scans for spaceships and updates the database with the results.

- **[longitude_degrees, longitude_minutes, longitude_seconds, latitude_degrees, latitude_minutes, latitude_seconds]**: Coordinates to be used when performing the scan action. Each coordinate should be a floating-point number representing degrees, minutes, and seconds for longitude and latitude.