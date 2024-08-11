import re
import torch
from abc import ABC, abstractmethod
from langchain_huggingface.llms import HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser
from langchain import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TextStreamer, pipeline
from peft import PeftModel
from langchain_core.prompts import PromptTemplate


class LLMBase(ABC):
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def get_prompt(self):
        pass

    @abstractmethod
    def generate_query(self, question: str, schemas: str):
        pass

    def validate_query(self, query: str):
        patterns = [r'\bcreate\b', r'\bupdate\b', r'\bdelete\b']
        if any(re.search(pattern, query.lower()) for pattern in patterns):
            return False, "Query contains modifier statements"
        return True, ""


class SQLGeneratorLLM(LLMBase):
    def __init__(self):
        self.base_model_name = "google/flan-t5-base"
        self.model_name = "kampkelly/sql-generator"
        self.tokenizer = None
        self.model = None
        self.prompt = ""
        self.get_prompt()

    def setup(self):
        self.get_model()
        self.get_tokenizer()

    def get_model(self):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.base_model_name, torch_dtype=torch.bfloat16)
        PeftModel.from_pretrained(self.model,
                                  self.model_name,
                                  torch_dtype=torch.bfloat16,
                                  is_trainable=False)

        return self.model

    def get_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        return self.tokenizer

    def get_prompt(self):
        template = """
          Given the PostgreSQL schema 
          {schemas}
          generate only the sql query with no additional text for this question: {question}
        """
        self.prompt = PromptTemplate.from_template(template)

        return self.prompt

    def get_llm(self):
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
        llm = self.get_llm()
        chain = self.prompt | llm | StrOutputParser()

        result = chain.invoke({"question": question, "schemas": schemas})
        return result

    def generate_query(self, question: str, schemas: str):
        query = self.get_query(question, schemas)
        return query
