import json
import sys

import spaceship_pb2
import spaceship_pb2_grpc
import argparse
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from typing import Dict, List
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, model_validator
import logging
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, text
import os
import grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Client")

# validation part

class RightSpaceship(BaseModel):
    alignment: str
    name: str
    class_of_spaceship: str
    length: float
    crew_size: int
    armed: bool
    officers: List[Dict[str, str]]

    @model_validator(mode='after')
    @classmethod
    def validate(cls, model: 'RightSpaceship') -> 'RightSpaceship':
        alignment = model.alignment
        class_of_spaceship = model.class_of_spaceship
        model.length = round(model.length, 3)
        length = model.length
        crew_size = model.crew_size
        armed = model.armed
        if class_of_spaceship == 'Corvette':
            if not (80 <= length <= 250 and 4 <= crew_size <= 10):
                raise ValueError
        elif class_of_spaceship == 'Frigate':
            if not (300 <= length <= 600 and 10 <= crew_size <= 15 and alignment != 'ENEMY'):
                raise ValueError
        elif class_of_spaceship == 'Cruiser':
            if not (500 <= length <= 1000 and 15 <= crew_size <= 30):
                raise ValueError
        elif class_of_spaceship == 'Destroyer':
            if not (800 <= length <= 2000 and 50 <= crew_size <= 80 and alignment != 'ENEMY'):
                raise ValueError
        elif class_of_spaceship == 'Carrier':
            if not (1000 <= length <= 4000 and 120 <= crew_size <= 250 and not armed):
                raise ValueError
        elif class_of_spaceship == 'Dreadnought':
            if not (5000 <= length <= 20000 and 300 <= crew_size <= 500):
                raise ValueError

        return model

    def to_json(self) -> any:
        return self.json()

# DB part

class DB_info(BaseModel):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: int
    DB_NAME: str

    def make_url(self) -> str:
        url = f"postgresql+psycopg2://{self.DB_USER}:{
            self.DB_PASS}@{self.DB_HOST}/{self.DB_NAME}"
        return url


Base = declarative_base()

def create_coord_class(table_name: str) -> any:
    class Coord(Base):
        __tablename__ = f'Coordinates {table_name}'
        id = Column(Integer, primary_key=True, autoincrement=True)
        alignment = Column(String)
        name = Column(String)
        class_of_spaceship = Column(String)
        length = Column(Float)
        crew_size = Column(Integer)
        armed = Column(Boolean)
    return Coord


def create_team_class(table_name: str) -> any:
    actual_table_name = f'Crew on {table_name}'

    class Team(Base):
        __tablename__ = actual_table_name
        id = Column(Integer, primary_key=True, autoincrement=True)
        ship_id = Column(Integer, ForeignKey(f'Coordinates {table_name}.id'))
        first_name = Column(String)
        last_name = Column(String)
        rank = Column(String)
    return Team


def create_imposters_class() -> any:
    class Imposters(Base):
        __tablename__ = 'Imposters'
        id = Column(Integer, primary_key=True, autoincrement=True)
        first_name = Column(String)
        last_name = Column(String)
        rank = Column(String)
    return Imposters


def create_tables(engine: Engine, table_name: str) -> any:
    spaceships = create_coord_class(table_name)
    team = create_team_class(table_name)
    Base.metadata.create_all(engine, checkfirst=True)
    return spaceships, team


def create_imposters_table(engine: Engine) -> any:
    imposters = create_imposters_class()
    Base.metadata.create_all(engine, checkfirst=True)
    return imposters

# Core part

def fill_coord(coord: List[float]) -> spaceship_pb2.Coordinates:
    coord = spaceship_pb2.Coordinates(
        longitude_degrees=coord[0], longitude_minutes=coord[1], longitude_seconds=coord[2],
        latitude_degrees=coord[3], latitude_minutes=coord[4], latitude_seconds=coord[5])
    return coord


def sort_dicts(lst):
    return sorted([tuple(sorted(d.items())) for d in lst])


def scan_imposters(session: any, table_team: any, table_space: any, final_table: any) -> None:

    select_ally = session.query(table_team.first_name, table_team.last_name).join(
        table_space, table_team.ship_id == table_space.id).filter(table_space.alignment == 'ALLY')
    select_enemy = session.query(table_team.first_name, table_team.last_name).join(
        table_space, table_team.ship_id == table_space.id).filter(table_space.alignment == 'ENEMY')
    intersect_query = select_ally.intersect(select_enemy)

    for row in intersect_query:
        imposter = final_table(first_name=row.first_name,
                               last_name=row.last_name, rank='Imposter')
        session.add(imposter)
        session.commit()


def check_on_duplicates(session: any, ship_name: str, table_team: any, table_space: any, team_to_add: List[Dict[str, str]]) -> bool:
    ships_id_with_same_name = session.query(
        table_space.id).filter(table_space.name == ship_name).all()
    if not ships_id_with_same_name:
        return True
    for id in ships_id_with_same_name:
        officers_with_id = session.query(table_team).filter(
            table_team.ship_id == id[0]).all()
        if len(officers_with_id) != len(team_to_add):
            return True
        else:
            team_was = [{"first_name": row.first_name, "last_name": row.last_name,
                         "rank": row.rank} for row in officers_with_id]
            if sort_dicts(team_was) == sort_dicts(team_to_add):
                return False
            else:
                return True


def run(message: spaceship_pb2.Coordinates, session, table_space: any, table_team: any) -> None:
    try:
        channel = grpc.insecure_channel('localhost:50051')
        stub = spaceship_pb2_grpc.ServiceStub(channel)
        answer = stub.SpaceServer(message)
        for spaceship in answer:
            try:

                spc = RightSpaceship(alignment=spaceship_pb2.Spaceship.Alignment.Name(spaceship.alignment),
                                     name=spaceship.name,
                                     class_of_spaceship=spaceship_pb2.Spaceship.Class.Name(
                    spaceship.class_of_spaceship),
                    length=spaceship.length,
                    crew_size=spaceship.size,
                    armed=spaceship.status,
                    officers=[{"first_name": off.name, "last_name": off.surname,
                               "rank": off.rank} for off in spaceship.officers]
                )
                if check_on_duplicates(session, spc.name, table_team, table_space, spc.officers):
                    ship = table_space(alignment=spc.alignment,
                                       name=spc.name,
                                       class_of_spaceship=spc.class_of_spaceship, length=spc.length, crew_size=spc.crew_size,
                                       armed=spc.armed)
                    session.add(ship)
                    session.commit()
                    for off in spc.officers:
                        session.add(table_team(ship_id=ship.id,
                                               first_name=off['first_name'], last_name=off['last_name'], rank=off['rank']))
                        session.commit()
                    print(f'\n{spc.to_json()}\n')
            except ValidationError as ve:
                continue
    except grpc.RpcError as re:
        logger.error(f" RPC error: {re}")
        sys.exit(1)
    except Exception as e:
        logger.error(f" An unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':

    load_dotenv()

    db_config = DB_info(DB_HOST=os.environ.get('DB_HOST'),
                        DB_PORT=os.environ.get('DB_PORT'),
                        DB_USER=os.environ.get('DB_USER'),
                        DB_PASS=os.environ.get('DB_PASS'),
                        DB_NAME=os.environ.get('DB_NAME'))

    parser = argparse.ArgumentParser()

    parser.add_argument('action', choices=[
                        'scan', 'list_traitors', 'default'], nargs='?')
    parser.add_argument('coords', type=float, nargs='*')

    args = parser.parse_args()

    engine = create_engine(url=db_config.make_url())

    if len(args.coords) != 6 and args.action != 'list_traitors':
        logger.error('Wrong format')
        sys.exit(1)

    else:
        with engine.connect() as conn:
            Session = sessionmaker(bind=engine)
            session = Session()
            if args.action == 'list_traitors':
                imposters = create_imposters_table(engine)
                users = session.query(imposters).all()
                for row in users:
                    print(json.dumps(
                        {'firs_name': row.first_name, 'last_name': row.last_name, 'rank': row.rank}))

            elif args.action == 'scan':
                space, team = create_tables(
                    engine, ' '.join([str(i) for i in args.coords]))
                imposters = create_imposters_table(engine)
                session.query(imposters).delete()
                session.commit()

                scan_imposters(session, team, space, imposters)

            else:
                space, team = create_tables(
                    engine, ' '.join([str(i) for i in args.coords]))
                imposters = create_imposters_table(engine)
                message: spaceship_pb2.Coordinates = fill_coord(args.coords)
                run(message, session, space, team)

            session.close()
