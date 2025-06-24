from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Connect to LM Studio running at localhost
llm = ChatOpenAI(
    model="local-model",  # Name doesn't matter much here
    temperature=0.7,
    openai_api_key="not-needed",  # Required by LangChain even for local
    openai_api_base="http://localhost:1234/v1",  # LM Studio's endpoint
)

parser = StrOutputParser()

def build_chain(prompt):
    """
    Builds a LangChain pipeline: prompt → LLM → string output
    """
    return prompt | llm | parser
