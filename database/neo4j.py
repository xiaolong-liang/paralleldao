# from neo4j import GraphDatabase
from py2neo import Graph
from threading import Lock


class Neo4jKnowlege:
    _lock = Lock()
    _instance = None

    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="neo"):
        if not self._instance:
            with self._lock:
                if not self._instance:
                    self.driver = Graph(uri, user=user, password=password)

    def __enter__(self, uri="bolt://localhost:7687", user="neo4j", password="neo"):
        # self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print("entering")
        return self

    # def close(self):
    #     self.driver.close()

    def __exit__(self, type, value, trace):
        print('existing')
        self.close()

    def print_greeting(self, message):
        with self.driver.session() as session:
            greeting = session.write_transaction(self._create_and_return_greeting, message)
            print(greeting)

    def get_vote_proposals(self, message):
        sql = "match (n1:ns1__VoteAction)-[:ns1__hasObject]-(n2:ns1__Voter), (n1)-[:ns1__hasSubject]-(n3:ns1__Proposal) where n2.ns1__address=\"{}\" return n3".format(message)
        stmt = self.driver.run(sql)
        result = []
        for node in stmt:
            result.append(node[0]['ns1__meta'])
        return result

        # with self.driver.session() as session:
        #     greeting = session.write_transaction(self._get_vote_proposals, message)
        #     return greeting

    @staticmethod
    def _get_vote_proposals(tx, _id):
        sql = "match (n1:ns1__VoteAction)-[:ns1__hasObject]-(n2:ns1__Voter), (n1)-[:ns1__hasSubject]-(n3:ns1__Proposal) where n2.ns1__address=\"0x34750c3af93ceda1500d97de4493b13e509ea24a\" return n3"
        # result = tx.run("match (n1:ns1__VoteAction)-[:ns1__hasObject]-(n2:ns1__Voter), (n1)-[:ns1__hasSubject]-(n3:ns1__Proposal) where n2.ns1__address=\"$message\" return n3 limit 10", message=_id)
        result = tx.run(sql)
        return result

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]


if __name__ == "__main__":
    greeter = Neo4jKnowlege("bolt://localhost:7687", "neo4j", "neo")
    print(greeter.get_vote_proposals("0x34750c3af93ceda1500d97de4493b13e509ea24a"))