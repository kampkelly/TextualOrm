import asyncio
import hashlib
from src.database import Database
from src.db_redis import redis_setup, REDIS_PATH
from src.libs import SQLGenerator, LLMType


class Orm:
    def __init__(self, connection_string: str, llm_type: LLMType, redis_host: str, redis_port: int, min_size=1, max_size=5, **kwargs):
        self.connection_string = connection_string
        self.min_size = min_size
        self.max_size = max_size
        self.redis = None
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.db = None
        self.redis = None
        self.sql_generator = SQLGenerator(llm_type, **kwargs)
        self.llm_type = llm_type

    async def setup(self):
        '''
        Initializes the database connection
        '''
        self.redis = self.__connect_redis()
        self.db = await self._connect_database()

        self.sql_generator.setup()

    def __connect_redis(self):
        '''
        Connects to the Redis server
        '''
        return redis_setup(self.redis_host, self.redis_port)

    async def _connect_database(self):
        '''
        Connects to the database and sets up the connection
        '''
        db = Database(self.connection_string, self.redis)
        await db.setup()
        return db

    def get_llm_query(self, question: str, schemas: str):
        '''
        Gets sql query from question and schema. Validates the sql query to have non-destructive actions.
        '''
        query = self.sql_generator.generate_query(question, schemas)
        return query

    async def make_sql_request(self, question: str, tables: bool, request_data=False):
        try:
            result = await self.make_request(question, tables, request_data)
            return result
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return f"An unexpected error occurred: {e}"

    async def make_request(self, question: str, tables: list, request_data: bool):
        '''
        Starts query retrieval
        check if in redis, then quick return
        if not in redis, get sql query from llm

        if successful and before returning to user, store sql query and inputs in redis
        '''
        combined_str = None
        hash_str = None
        redis_path = None
        sql_query = ""
        tables_schema = ""

        if not tables:
            raise ValueError("Tables is required")

        strip_tables = [t.strip() for t in tables]
        c = ",".join(strip_tables)
        combined_str = question.strip() + " Tables: " + c            
        hash_str = hashlib.sha256(combined_str.encode()).hexdigest()
        redis_path = f"{REDIS_PATH}:{hash_str}"
        redis_val = self.redis.hgetall(redis_path)

        if redis_val:
            sql_query = redis_val.get("sql_query")
        else:
            for table_name in tables:
                schema = await self.db.get_table_schema(table_name)
                tables_schema = tables_schema + schema

        sql_query = self.get_llm_query(question, tables_schema)

        result = {"query": sql_query, "data": None}
        if request_data:
            if not redis_val:
                if tables and combined_str and hash_str:
                    self.redis.hset(redis_path, mapping={
                        'sql_query': sql_query,
                        'schemas': tables_schema
                    })

            data = await self.query_db(sql_query)
            result["data"] = data
        return result

    async def query_db(self, query_str: str):
        '''
        Executes a query on the connected database
        check if in redis
        '''
        query = await self.db.make_query(query_str)
        return query


# example usage
async def main():
    orm = Orm(connection_string="postgresql://",
              llm_type=LLMType.DEFAULT, redis_host="localhost",
              redis_port=6379, api_key="")
    await orm.setup()
    req = await orm.make_sql_request("List of settings", ["setting"])
    print(req)

asyncio.run(main())
