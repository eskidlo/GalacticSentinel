# GalacticSentinel 

Three thouthands years from today, the mankind now have such great technologies we couldn't even imagine. The mankind now continues to explore universe, and even managed to sully settle on several planets.However, not all inhabitants of space are fond of new neighbours. Gradiully, contacts with some civilization escalated into tense conflicts, and mankind drawn into endless intergalactic wars.

To protect the colonies, humans developen the "Galactic Sentinel" - a system, capable of detecting and classifiying spacecrafts, distinguishing between allies and enemies and finding impostors. "Galactic Sentinel" has become a reliable shield for humanity in the depths of space.

## Overview 

This project is designed to manage spaceship data and their crew members. It involves communication with a gRPC service to retrieve spaceship information and store it in a PostgreSQL database. The project consists of three main parts:

- **Protobuf Definitions:** Defines the data structures and gRPC service.

- **Python script server.py:**  Receives a `Coordinates` object that characterizes the coordinates of the constellation and returns from 30 to 50 Spaceship objects that characterize ships located within coordinates. 

- **Python script client.py:** Receives the sent `Spaceship` objects, validates the information about the ships, and inserts it into the database. All actions are detailed in the "Usage" section.

## Setup

Run the following command:
```sh
make all
```

##Stop

Run the following command:
```sh
make clean
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
