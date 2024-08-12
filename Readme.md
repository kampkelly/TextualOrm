# TextualOrm
<img src="https://i.imgur.com/kTfe0vU.png" alt="Example Image" width="100"/>

This tool generates SQL queries from natural language and retrieves query results. This orm generates sql queries from your input and the specifics of your connected database and can also run them to retrieve records.

**Currently this orm will only honour retrieval queries. i.e any queries that perform delete, create or any crud actions wont be executed on your database**

The core of this application is the use of Large Language Models to generate the sql queries. This orm currently supports two LLMs:
1. [SQL Generator LLM](https://huggingface.co/kampkelly/sql-generator) - (free and the default llm used).
2. OpenAI (requires subscription to OpenAI)

You can find more information about the default SQL Generator by going to the link [here](https://huggingface.co/kampkelly/sql-generator). This has been fine-trained from the flan-t5-base model.

### Requirements
- Python
- Postgres
- Redis
*Note: Support for additional databases such as MySQL will be added in future updates.*


### Installation
`pip install sql-generator`

### Usage Instructions
1. Initialize the Generator
    ```
    from textual_orm import TextualOrm
    textual_orm = TextualOrm(connection_string="postgresql://user:password@host:port/db_name",
                llm_type=LLMType.DEFAULT, redis_host="localhost",
                redis_port=6379)
    ```

    To use the OpenAI implementation, add your api-key to the arguments:

    ```
    from textual_orm import TextualOrm
    textual_orm = TextualOrm(connection_string="postgresql://user:password@host:port/db_name",
                llm_type=LLMType.DEFAULT, redis_host="localhost",
                redis_port=6379, api-key="")

    ```

2. Call the setup method:
  `await textual_orm.setup()`

3. Generate the SQL query
    ```
    sql_query = await textual_orm.make_sql_request("List of settings", ["setting"])
    print(sql_query)
    ```
    This method takes three arguments:
      - question: Input question
      - tables: List of tables as reference
      - request_data: A boolean to indicate if it should query the database or return only the sql_query (default value is False)
    <br>
    By default, the make_sql_request does not actually query the database. It returns back the generated sql query which you can look at and verify. To get an alternative sql query, please modify your input question.

    To query the database with the generated sql query. Call the method passing in `request_data=True`. This will return a response in this format:

    ```
    {
      'query': 'SELECT * FROM setting ORDER BY created_at DESC LIMIT 5;',
      'data': [<records>]
    }
    ```
    Where data is a list of records from the query response. `data` will be None if `request_data=False` as in the default case.

Note that first time run may take a little time.
For better performance, speed and caching, redis is required.


#### Additional Arguments
This orm uses a default postgres max pool of 10. You can modify it if needed by passing your value to the `max_pool` argument.

Below is a list of other supported arguments to Orm:
`min_size=1` minimum size o pool
`max_size=10` maxiumum size of pool
`api_key=""` api key for the given llm
