import asyncio
from pprint import pprint
from src.database import Database


class Orm:
    def __init__(self, connection_string: str, min_size=1, max_size=5):
        self.connection_string = connection_string
        self.conn = None
        self.min_size = min_size
        self.max_size = max_size
        self.pool = None
        self.initialized = True
        self.redis = None
        self.db = None

    async def setup(self):
        '''
        Initializes the database connection
        '''
        self.db = await self._connect_database()
        pass

    def connect_redis(self):
        '''
        Connects to the Redis server
        '''
        pass

    async def _connect_database(self):
        '''
        Connects to the database and sets up the connection
        '''
        db = Database(self.connection_string)
        await db.setup()

        return db

    async def query_db(self, query_str: str, tables=None):
        '''
        Executes a query on the connected database
        '''
        query = await self.db.make_query(query_str)
        pprint(query)
        return query


# example usage
async def main():
    orm = Orm(connection_string="postgresql://runor:postgres@localhost:5432/bettersearch_main")
    await orm.setup()
    await orm.query_db("SELECT * FROM setting")

asyncio.run(main())
