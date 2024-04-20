from langchain.chains import (
    StuffDocumentsChain, LLMChain, ConversationalRetrievalChain
)
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage

# TODO : add the function to create
from dotenv import load_dotenv
import os

class WelcomeChatBot:

    def __init__(self, vector_db):
        self.vectorstore = vector_db
        self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={'k': 6})

        #self.memory = ConversationBufferMemory()
        self.chat_history = []

    
    def setup_config(self):

        load_dotenv()

        os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

        # set retriever's number of docs to get

        # This controls how the standalone question is generated.
        # Should take `chat_history` and `question` as input variables.

        self.template = (
            """ Anwer to the question given at the end, while using the given context, and chat history :
                context : 
                {context}

                chat_history:
                {chat_history}

                question:
                {question}

                Your Answer : 
            """
        )

        self.prompt = PromptTemplate.from_template(template=self.template)

        self.llm = ChatOpenAI(model="gpt-4-0613", temperature=0.5)

    def get_answer(self, user_query):
        
        docs = self.retriever.invoke(user_query)

        query = self.template.format(chat_history=self.chat_history, context=docs, question=user_query)

        answer = self.llm.invoke(query)

        self.chat_history.append(f'USER : {user_query}')
        self.chat_history.append(f'AI : {answer.content}')

        return answer.content        