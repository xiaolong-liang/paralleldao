import time
from enum import Enum
from rdflib import Graph

class RDFlibData:
    def __init__(self, path=None) -> None:
        self.g = Graph()
        if path:
            self.g.parse(path)

    def update(self, stmt):
        self.g.update(stmt)

    def query(self, stmt):
        return self.g.query(stmt)