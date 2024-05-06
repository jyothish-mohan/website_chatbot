from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm_response(user_input, db):
    llm = ChatOpenAI(model="gpt-3.5-turbo-0613", temperature=0.0, api_key=os.getenv("OPENAI_API_KEY"))

    DOCS_CHAIN_PROMPT = """
    You are a friendly assistant chatbot.
    Please use the following pieces of context to answer the question at the end.
    If you cant find the answer from the context, kindly only just say that "I dont know!".
    Dont answer anything which is not in the context.
    Try to answer in brief sentence.

    {context}

    Question: {question}  
    Answer:"""

    prompt = PromptTemplate(template=DOCS_CHAIN_PROMPT, input_variables=['context', 'question'])

    qa = ConversationalRetrievalChain.from_llm(llm, retriever=db.as_retriever(), 
                                           combine_docs_chain_kwargs={'prompt': prompt})
    
    res = qa.invoke({"question":user_input, "chat_history":[]}, verbose=False)

    return res["answer"]