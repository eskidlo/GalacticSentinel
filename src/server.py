import spaceship_pb2
import spaceship_pb2_grpc
from typing import List, Generator
import random
import grpc
from concurrent import futures


class SpaceServer(spaceship_pb2_grpc.ServiceServicer):
    def __init__(self):
        pass

    def __randomizer_officers(self, size: int) -> List[spaceship_pb2.Person]:
        random_person_surnames: List[str] = [
            'Kim', 'O\'Connor', 'Ross', 'Smit', 'Cooke', 'West', 'Martinez', 'Davis']
        random_person_names: List[str] = [
            'Alan', 'Kate', 'Timothy', 'Helen', 'Jane', 'Isabella', 'Emma', 'Omar']
        random_person_rank: List[str] = ['Captain', 'Commander',
                                         'Admiral', 'Lieutenan', 'Major General']

        officers: List[spaceship_pb2.Person] = []
        for i in range(size):
            person = spaceship_pb2.Person(name=random.choice(random_person_names), surname=random.choice(
                random_person_surnames), rank=random.choice(random_person_rank))
            officers.append(person)
        return officers

    def __randomizer(self) -> spaceship_pb2.Spaceship:

        random_name: List[str] = ['Normandy', 'Executor',
                                  'Stormbringer', 'Star Fortress', 'Meteor', 'Star Furry', 'Shadow Dragon', 'Galaxy Tornado']
        spaceship_alignment = list(
            spaceship_pb2.Spaceship.Alignment.DESCRIPTOR.values_by_name)
        spaceship_class = list(
            spaceship_pb2.Spaceship.Class.DESCRIPTOR.values_by_name)

        spaceship = spaceship_pb2.Spaceship()

        spaceship.alignment = random.choice(spaceship_alignment)
        spaceship.class_of_spaceship = random.choice(spaceship_class)
        spaceship.length = random.uniform(70, 20001)
        spaceship.size = random.randint(3, 501)
        spaceship.status = random.choice([True, False])

        if spaceship.alignment == spaceship_pb2.Spaceship.ALLY:
            spaceship.name = random.choice(random_name)
            officers: List[spaceship_pb2.Person] = self.__randomizer_officers(
                random.randint(1, 10))
        else:
            random_name.append('Unknown')
            spaceship.name = random.choice(random_name)
            officers = self.__randomizer_officers(random.randint(0, 10))

        for off in officers:
            new_officer = spaceship.officers.add()
            new_officer.CopyFrom(off)

        return spaceship

    def SpaceServer(self, request: spaceship_pb2.Coordinates, context: any) -> Generator[spaceship_pb2.Spaceship, None, None]:
        for _ in range(random.randint(1, 10)):
            spaceship: spaceship_pb2.Spaceship = self.__randomizer()
            yield spaceship


def serve() -> None:
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10))
    spaceship_pb2_grpc.add_ServiceServicer_to_server(SpaceServer(), server)
    server.add_insecure_port('localhost:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
