import os
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings

chroma_client = chromadb.HttpClient(
    host="13.51.235.2", port=8000, settings=Settings(allow_reset=True))


#LLM
GROQ_LLM = ChatGroq(
    api_key=os.environ["groq_API_Key"],
    model="llama3-70B-8192")



#LOAD VECTORDB
model_name = "BAAI/bge-base-en"
encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity

bge_embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cpu'},
    encode_kwargs=encode_kwargs
)

collection_name = "concept_documents"
vectordb = Chroma(
    client=chroma_client,
    collection_name=collection_name,
    embedding_function=bge_embeddings,
)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})
