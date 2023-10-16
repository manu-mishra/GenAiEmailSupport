#test setup
import os
os.environ['KENDRA_INDEX'] = '3a0cd6b7-6031-47a0-816c-c4f932628dff'
os.environ['FAQ_DATASOURCE_REF'] = '818f5bdf-ee2c-4102-9e10-2cabe3b6b16e|3a0cd6b7-6031-47a0-816c-c4f932628dff'
os.environ['SUPPORT_DATASOURCE_REF'] = 'c02537d3-c3d2-483f-9bc1-e9b014d6b8e6|3a0cd6b7-6031-47a0-816c-c4f932628dff'

#test setup end

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains.llm import LLMChain
from chain_logic import generate_response 

kendra_search = KendraSearch()
#question = "What is Amazon Kendra?"
#question = "I am facing performance problems with Amazon Kendra? regards bob"
#question = "I am facing performance problem with my dogs running, can you help? regards bob"
question = "Is Open search better than Amazon Kendra? regards bob"
#question = "I am facing performance problem with my dogs running, can you help? regards bob"
#question = "I am facing performance problem with my dogs running, can you help? regards bob"

print(generate_response(question))
