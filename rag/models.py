import os
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma


#LLM
GROQ_LLM = ChatGroq(
    api_key=os.environ["groq_API_Key"],
    model="llama3-70B-8192")



#LOAD VECTORDB
model_name = "BAAI/bge-base-en"
encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity

bge_embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cuda'},
    encode_kwargs=encode_kwargs
)

persist_directory = '/content/db' #replace with path to db
embedding = bge_embeddings
vectordb=Chroma(persist_directory=persist_directory,embedding_function=embedding)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})
