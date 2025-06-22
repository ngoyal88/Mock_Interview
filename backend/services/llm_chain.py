from langchain_community.llms import LLMEndpoint
from langchain_core.output_parsers import StrOutputParser

# Connect to LM Studio running at localhost
llm = LLMEndpoint(
    endpoint_url="http://localhost:1234/v1/completions",
    model_kwargs={
        "stop": ["\n"],
        "temperature": 0.7,
        "max_tokens": 256
    }
)

parser = StrOutputParser()

def build_chain(prompt):
    """
    Builds a LangChain pipeline: prompt → LLM → string output
    """
    return prompt | llm | parser
