from langchain.chains import (
    StuffDocumentsChain, LLMChain, ConversationalRetrievalChain
)
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import OpenAI

# TODO : add the function to create
from utils import get_vector_db

combine_docs_chain = StuffDocumentsChain(...)
vectorstore = get_vector_db()
retriever = vectorstore.as_retriever()

# set retriever's number of docs to get

# This controls how the standalone question is generated.
# Should take `chat_history` and `question` as input variables.
template = (
    "Combine the chat history and follow up question into "
    "a standalone question. Chat History: {chat_history}"
    "Follow up question: {question}"
)

prompt = PromptTemplate.from_template(template)

llm = OpenAI()

question_generator_chain = LLMChain(llm=llm, prompt=prompt)

chain = ConversationalRetrievalChain(
    combine_docs_chain=combine_docs_chain,
    retriever=retriever,
    question_generator=question_generator_chain,
    memory=ConversationBufferMemory(),
)