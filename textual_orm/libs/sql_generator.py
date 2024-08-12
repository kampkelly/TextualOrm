from textual_orm.libs.default_llm import SQLGeneratorLLM
from textual_orm.libs.openai import OpenAILLM
from textual_orm.errors import SQLGeneratorError
from textual_orm.libs.base import LLMType


class SQLGeneratorFactory:
    @staticmethod
    def get_setting(llm_type, **kwargs):
        '''
        Returns the appropriate SQL generator based on the specified LLM type.

        Args:
            llm_type (LLMType): The type of language model to use.
            **kwargs: Additional keyword arguments for initializing the specific SQL generator.

        Returns:
            SQLGeneratorLLM or OpenAILLM: An instance of the selected SQL generator based on the LLM type.

        Raises:
            ValueError: If the specified LLM type is unknown.
        '''
        if llm_type == LLMType.DEFAULT:
            return SQLGeneratorLLM()
        elif llm_type == LLMType.OPENAI:
            return OpenAILLM(**kwargs)
        else:
            raise ValueError("Unknown llm type")


class SQLGenerator:
    def __init__(self, setting_type: LLMType, **kwargs):
        self.llm = SQLGeneratorFactory.get_setting(setting_type, **kwargs)

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
