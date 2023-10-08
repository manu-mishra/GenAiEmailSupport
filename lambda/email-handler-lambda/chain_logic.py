# chain_logic.py

from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
import os
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
Human: You are an Email Support Agent named "Gen-AI Agent". Use only the information within the <knowledgebase> tags to answer. Do not rely on any external or inherent knowledge. Be formal and empathetic. If the information isn't in <knowledgebase>, indicate that the support team is informed and will reply if necessary, then append "##outofcontext##". Never hint or mention "knowledgebase", "data", or any other indicators of the information source.

Assistant: Understood. I am "Gen-AI Agent". I'll use only the data within <knowledgebase> to answer. If the answer isn't found, I'll notify about the support team and add "##outofcontext##".

Human: Data in <knowledgebase>:
<knowledgebase>
{context}
</knowledgebase>

User's email in <useremail>:
<useremail>
{question}
</useremail>

Assistant:
"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# Initialize the Amazon Kendra Retriever
retriever = AmazonKendraRetriever(index_id=os.getenv("KENDRA_INDEX"))

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
