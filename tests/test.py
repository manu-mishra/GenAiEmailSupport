from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains.llm import LLMChain

llm = Bedrock(
      model_kwargs={"max_tokens_to_sample":300,"temperature":1,"top_k":250,"top_p":0.999,"anthropic_version":"bedrock-2023-05-31"},
      model_id="anthropic.claude-v2"
  )
  
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

retriever = AmazonKendraRetriever(index_id="f50aa19c-b4f1-4da2-943b-78ab1e1e4eee")

chain_type_kwargs = {"prompt": PROMPT}
    
chain= RetrievalQA.from_chain_type(
      llm, 
      chain_type="stuff", 
      retriever=retriever, 
      chain_type_kwargs=chain_type_kwargs, 
      return_source_documents=True
  )
result = chain("can you explain what is kendra? regards, Bob")
print(result['result'])

result = chain("how do i cure my dogs cancer? regards, Aly")
print(result['result'])

result = chain("What is Amazon AWS? regards, Bob")
print(result['result'])

result = chain("What is microsoft Azure? regards, Aly")
print(result['result'])