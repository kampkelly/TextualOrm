from src.libs.default_llm import SQLGeneratorLLM
from src.libs.openai import OpenAILLM
from src.errors import SQLGeneratorError
from src.libs.base import LLMType


class LLMFactory:
    @staticmethod
    def get_setting(llm_type, **kwargs):
        if llm_type == LLMType.DEFAULT:
            return SQLGeneratorLLM()
        elif llm_type == LLMType.OPENAI:
            return OpenAILLM(**kwargs)
        else:
            raise ValueError("Unknown llm type")


class SQLGenerator:
    def __init__(self, setting_type: LLMType, **kwargs):
        self.llm = LLMFactory.get_setting(setting_type, **kwargs)

    def setup(self):
        '''
        Sets up the SQLGenerator by calling the setup method of the underlying language model.
        '''
        return self.llm.setup()

    def generate_query(self, question: str, schemas: str):
        '''
        Generates a SQL query based on the given question and schemas using the underlying language model.
        Validates the query and raises an error if it is not valid.
        '''
        query = self.llm.generate_query(question, schemas)
        validate_query, message = self.llm.validate_query(query)
        if validate_query:
            return query
        raise SQLGeneratorError(f"Generated SQL query is not valid: \"{message}\". Please retry with a different prompt")
