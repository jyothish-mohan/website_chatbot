from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

load_dotenv()

def preprocess_data(url):
    try:
        loader = WebBaseLoader(url)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        texts = text_splitter.split_documents(data)

        embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

        db = FAISS.from_documents(texts, embeddings)
        return {"success":True, "db":db}
    except Exception as e:
        return {"success":False, "db":None}
    
