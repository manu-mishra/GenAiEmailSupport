from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from knowledgebase import KendraSearch
import os

# Initialize the Bedrock model
llm = Bedrock(
    model_kwargs={
        "max_tokens_to_sample": 500,
        "temperature": 1,
        "top_k": 250,
        "top_p": 0.999,
        "anthropic_version": "bedrock-2023-05-31"
    },
    model_id="anthropic.claude-v2"
)

# Initialize the Bedrock model
search_tool = KendraSearch()

# Set up the prompt template
prompt_template = """
Human: Gen-AI Agent, as the Email Support Agent, your duty is to answer the user's query with well formatted email using the specific content found in <knowledgebase>. Ensure your answers are empathetic and formal. Do not mention that you are an AI assistant. If the question's answer isn't within the <knowledgebase> or if the <knowledgebase> tag is empty, simply let the user know that our support team has been notified and they might address it if deemed necessary, without suggesting alternatives or justifying that you dont know the answer. Only In such scenarios, append your response with "##outofcontext##". Under no circumstance should you refer to, or hint at, the <knowledgebase> or any tags or use word knowledgebase. Conclude your replies as "Gen-AI Agent".

Assistant: Understood.
Human: Respond to user's email based on following information. Remember to append ##outofcontext## if you are redirecting to support team.

{context}
{supportcaserequirements}


User's query:
<useremail>
{question}
</useremail>

Assistant:
"""


# Create the chain

chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template(prompt_template),
    verbose=True
)

def generate_response(question):
    """Generate a response using the chain."""
    context = search_tool.search_knowledge_base(question)
    support_case_requirements = search_tool.support_case_requirements(question)
    response = chain.run({"question": question, "context": context, "supportcaserequirements":support_case_requirements})
    return response
