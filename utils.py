import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Pinecone as PineconeVectorStore

from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain

from pinecone import Pinecone
from dotenv import load_dotenv

import streamlit as st
import os


load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")

import pinecone as pinecone_module
try:
    from pinecone.db_data.index import Index as PineconeIndex
    pinecone_module.Index = PineconeIndex
except ImportError:
    pass




def start_crawling(url, prefix, depth):
    visited_urls = set()
    wanted_urls = set()

    def crawl_urls(url, prefix, depth):
        if depth < 0:
            return
        visited_urls.add(url)

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            for anchor in soup.find_all("a"):
                href = anchor.get("href")

                if href:
                    absolute_url = urljoin(url, href)

                    if absolute_url.startswith(prefix):
                        parsed_url = urlparse(absolute_url)
                        if not parsed_url.fragment:
                            wanted_urls.add(absolute_url)

                    if absolute_url not in visited_urls:
                        crawl_urls(absolute_url, prefix, depth - 1)

        except requests.exceptions.RequestException as e:
            pass

    crawl_urls(url, prefix, depth)
    return list(sorted(wanted_urls))



def set_openai_api_key(api_key):
    if not st.session_state.get("openai_api_key"):
        st.error("Please set your OpenAI API key in the sidebar.")
        st.stop()

    os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key





def generate_pinecone_database(urls):
    loaders = UnstructuredURLLoader(urls=urls)
    data = loaders.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )
    docs = text_splitter.split_documents(data)

    embeddings = OpenAIEmbeddings()
    index_name = "websitegpt"

    pc = Pinecone(api_key=pinecone_api_key)

    indexes = pc.list_indexes()
    index_names = indexes.names()
    
    if index_name not in index_names:
        raise ValueError(
            f"Pinecone index '{index_name}' does NOT exist. "
            "Create it in the Pinecone dashboard first."
        )

    index = pc.Index(name=index_name)
    
    db = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        text_key="text",
        namespace="default"
    )
    
    db.add_documents(docs)
    return db



def load_pinecone_database():
    embeddings = OpenAIEmbeddings()
    index_name = "websitegpt"

    pc = Pinecone(api_key=pinecone_api_key)

    indexes = pc.list_indexes()
    index_names = indexes.names()
    
    if index_name not in index_names:
        raise ValueError(f"Pinecone index '{index_name}' does not exist!")

    index = pc.Index(name=index_name)
    
    db = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        text_key="text",
        namespace="default"
    )
    return db



def create_chain_type(db):
    llm = ChatOpenAI(model_name="gpt-4o-mini")
    retriever = db.as_retriever()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever,
        memory=memory
    )
    return chain

def generate_response(chain, question: str):
    response = chain({"question": question})
    return response
