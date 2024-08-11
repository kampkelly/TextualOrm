import torch
from langchain_huggingface.llms import HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser
from langchain import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from peft import PeftModel
from langchain_core.prompts import PromptTemplate
from src.libs.base import LLMBase
from src.errors import SQLGeneratorError


class SQLGeneratorLLM(LLMBase):
    def __init__(self):
        '''
        Initializes the SQLGeneratorLLM class
        '''
        self.base_model_name = "google/flan-t5-base"
        self.model_name = "kampkelly/sql-generator"
        self.tokenizer = None
        self.model = None
        self.prompt = ""
        self.get_prompt()

    def setup(self):
        '''
        Sets up the SQLGeneratorLLM by getting the model and tokenizer
        '''
        try:
            self.get_model()
            self.get_tokenizer()
        except Exception as e:
            raise SQLGeneratorError(e)

    def get_model(self):
        '''
        Retrieves the model for SQL generation
        '''
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.base_model_name, torch_dtype=torch.bfloat16)
        PeftModel.from_pretrained(self.model,
                                  self.model_name,
                                  torch_dtype=torch.bfloat16,
                                  is_trainable=False)

        return self.model

    def get_tokenizer(self):
        '''
        Retrieves the tokenizer for SQL generation
        '''
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        return self.tokenizer

    def get_prompt(self):
        '''
        Generates the prompt template for SQL generation
        '''
        template = """
          Given the PostgreSQL schema
          {schemas}
          generate only the sql query with no additional text for this question: {question}
        """
        self.prompt = PromptTemplate.from_template(template)

        return self.prompt

    def get_llm(self):
        '''
        Retrieves the language model for SQL generation
        '''
        generate_kwargs = {
            "num_beams": 3,
            "do_sample": True,
            "top_k": 50,
            "top_p": 0.75,
            "temperature": 0.1,
            "early_stopping": True
        }
        pipe = pipeline("text2text-generation", model=self.model, tokenizer=self.tokenizer, max_new_tokens=1000, **generate_kwargs)
        return HuggingFacePipeline(pipeline=pipe)

    def get_query(self, question: str, schemas: str):
        '''
        Gets the SQL query based on the question and schemas
        '''
        llm = self.get_llm()
        chain = self.prompt | llm | StrOutputParser()

        result = chain.invoke({"question": question, "schemas": schemas})
        return result

    def generate_query(self, question: str, schemas: str):
        '''
        Generates the SQL query based on the question and schemas
        '''
        query = self.get_query(question, schemas)
        return query
