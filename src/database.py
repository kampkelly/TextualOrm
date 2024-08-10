import asyncpg
import asyncio
from src.responses import DatabaseError


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
    schema_query = """
        SELECT
            'CREATE TABLE ' || relname || E'\n(\n' ||
            string_agg(
                '    ' || column_name || ' ' ||  type || ' '|| not_null,
                E',\n'
            ) || E'\n);\n'
        FROM (
            SELECT
                c.relname, a.attname AS column_name,
                pg_catalog.format_type(a.atttypid, a.atttypmod) as type,
                CASE
                    WHEN a.attnotnull THEN 'NOT NULL' 
                    ELSE 'NULL' 
                END as not_null 
            FROM pg_class c,
                    pg_attribute a,
                    pg_type t
            WHERE c.relname = $1
                AND a.attnum > 0
                AND a.attrelid = c.oid
                AND a.atttypid = t.oid
            ORDER BY a.attnum
        ) as tabledefinition
        GROUP BY relname;
    """

    def __init__(self, connection_string: str, redis: any, min_size=1, max_size=5):
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

    async def get_table_schema(self, table_name: str):
        '''
        Gets a create table schema for the specified table
        '''
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(Database.schema_query, table_name)
                if result:
                    return result
                else:
                    raise DatabaseError(f"Table '{table_name}' not found.")

        except Exception as e:
            raise DatabaseError(f"Error retrieving table schema. {e}")
