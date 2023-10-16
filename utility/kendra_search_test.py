#test setup
import os
os.environ['KENDRA_INDEX'] = '3a0cd6b7-6031-47a0-816c-c4f932628dff'
os.environ['FAQ_DATASOURCE_REF'] = '818f5bdf-ee2c-4102-9e10-2cabe3b6b16e|3a0cd6b7-6031-47a0-816c-c4f932628dff'
os.environ['SUPPORT_DATASOURCE_REF'] = 'c02537d3-c3d2-483f-9bc1-e9b014d6b8e6|3a0cd6b7-6031-47a0-816c-c4f932628dff'

#test setup end

from knowledgebase import KendraSearch

search = KendraSearch()

print(search.search_knowledge_base("What is Amazon Kendra?"))

print(search.support_case_requirements("What is Amazon Kendra?"))