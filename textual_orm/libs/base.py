import re
from enum import Enum
from abc import ABC, abstractmethod


class LLMType(Enum):
    DEFAULT = "default"
    OPENAI = "openai"


class LLMBase(ABC):
    @abstractmethod
    def setup(self):
        '''
        Abstract method to set up the LLM
        '''
        pass

    @abstractmethod
    def get_prompt(self):
        '''
        Abstract method to get the prompt for the LLM
        '''
        pass

    @abstractmethod
    def generate_query(self, question: str, schemas: str):
        '''
        Abstract method to generate a query based on the question and schemas
        '''
        pass

    def validate_query(self, query: str):
        '''
        Validates the generated query
        '''
        patterns = [r'\bcreate\b', r'\bupdate\b', r'\bdelete\b']
        if any(re.search(pattern, query.lower()) for pattern in patterns):
            return False, "Query contains modifier statements"
        return True, ""
