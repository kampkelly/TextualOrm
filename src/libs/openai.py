from src.libs.base import LLMBase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.errors import SQLGeneratorError


class OpenAILLM(LLMBase):
    def __init__(self, **kwargs):
        '''
        Initializes the OpenAI class
        '''
        self.api_key = kwargs.get("api_key", "")
        self.model = None
        self.prompt = ""
        self.get_prompt()

    def setup(self):
        '''
        Sets up the SQLGeneratorLLM by getting the model and tokenizer
        '''
        try:
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=self.api_key
            )
            self.llm = llm
        except Exception as e:
            raise SQLGeneratorError(e)

    def get_prompt(self):
        '''
        Generates the prompt template for SQL generation
        '''
        messages = [
            ("system", "You are a helpful assistant that generates sql queries. Here are some examples:"),
        ]

        examples = [
          (
            "CREATE TABLE album ( albumid INTEGER, title TEXT, artistid INTEGER )",
            "How many albums are there by the artist with id 1?",
            "SELECT COUNT(*) FROM album WHERE artistid = 1"
          ),
          (
            "CREATE TABLE album ( albumid INTEGER, title TEXT, artistid INTEGER )",
            "What is the title of the album with the lowest id and title starting with the letter 'Z'?",
            "SELECT title FROM album WHERE albumid = (SELECT MIN(albumid) FROM album) AND title LIKE 'Z%'"
          ),
          (
            "CREATE TABLE appellations ( no INTEGER, appelation TEXT, county TEXT, state TEXT, area TEXT, isava TEXT )",
            "What is the top 5 states with the highest appelation count?",
            "SELECT state, COUNT(*) as count FROM appellations GROUP BY state ORDER BY count DESC LIMIT 5;"
          )
        ]

        for example in examples:
            schema, question, query = example
            messages.append(
                (
                    "system",
                    f"""
                      Given the PostgreSQL schema
                      {schema}
                      generate only the sql query with no additional text for this question: {question}

                      {query}
                    """
                )
            )

        messages.extend([
            ("human", """
                      Given the PostgreSQL schema
                      {schema}
                      generate only the sql query with no additional text for this question: {question}   
                    """)
        ])
        self.prompt = ChatPromptTemplate.from_messages(messages)

    def get_query(self, question: str, schemas: str):
        '''
        Gets the SQL query based on the question and schemas
        '''
        chain = self.prompt | self.llm
        result = chain.invoke(
            {
                "schema": schemas,
                "question": question
            }
        )
        return result.content

    def generate_query(self, question: str, schemas: str):
        '''
        Generates the SQL query based on the question and schemas
        '''
        query = self.get_query(question, schemas)
        return query
