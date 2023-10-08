# chain_logic.py

from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock

# Initialize the Bedrock model
llm = Bedrock(
    model_kwargs={
        "max_tokens_to_sample": 300,
        "temperature": 1,
        "top_k": 250,
        "top_p": 0.999,
        "anthropic_version": "bedrock-2023-05-31"
    },
    model_id="anthropic.claude-v2"
)

# Set up the prompt template
prompt_template = """
... (same as in your original code) ...
"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# Initialize the Amazon Kendra Retriever
retriever = AmazonKendraRetriever(index_id="f50aa19c-b4f1-4da2-943b-78ab1e1e4eee")

# Create the chain
chain_type_kwargs = {"prompt": PROMPT}
chain = RetrievalQA.from_chain_type(
    llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs=chain_type_kwargs,
    return_source_documents=True
)

def generate_response(question):
    """Generate a response using the chain."""
    response = chain(question)
    return response['result']
