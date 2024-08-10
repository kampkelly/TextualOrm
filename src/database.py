import asyncpg
import asyncio


class Database:
    '''
    This class is used to connect to the given postgres database
    Attributes:
    ----------
    connection_string : str
        The database string
    min_size : int
        The lower limit for connection pool
    max_size : str
        The upper limit for connection pool

    Methods:
    -------
    setup():
        Initializes the database connection.
    make_query():
        Accepts sql query and returns the result
    '''
    def __init__(self, connection_string: str, min_size=1, max_size=5):
        self.connection_string = connection_string
        self.conn = None
        self.min_size = min_size
        self.max_size = max_size
        self.pool = None
        self.initialized = True

    async def setup(self):
        '''
        Initializes the database connection pool
        '''
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.connection_string,
                min_size=self.min_size, max_size=self.max_size
            )
            # todo: pull in default max_pools with SHOW max_connections;
            print('Connection Succeded!')
        except Exception as error:
            print(f"An error occurred: {error}")
        finally:
            pass

    async def make_query(self, query_str: str):
        '''
        Pass in a sql query to get records
        '''
        try:
            results = await asyncio.wait_for(self.__make_query(query_str), timeout=30.0)
            return results
        except asyncio.TimeoutError:
            print("The query took too long to complete")

    async def __make_query(self, query_str: str):
        '''
        Executes the SQL query and fetches the results
        '''
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query_str)

            return rows
