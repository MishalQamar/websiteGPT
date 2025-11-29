import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st
import os


def start_crawling(url,prefix,depth):
    visited_urls=set()
    wanted_urls=set()

    def crawl_urls(url,prefix,depth):
        if depth<0:
            return
        visited_urls.add(url)
        try:
            response=requests.get(url)
            soup=BeautifulSoup(response.content,"html.parser")
            print(f"Crawling: {url}")
            for anchor in soup.find_all("a"):
                href=anchor.get("href")
                if href:
                    absoulte_url=urljoin(url,href)
                    print(f"Found URL: {absoulte_url}")
                    if absoulte_url.startswith(prefix):
                        parsed_url = urlparse(absoulte_url)
                        if not parsed_url.fragment:
                            wanted_urls.add(absoulte_url) 
                    if absoulte_url not in visited_urls:
                        crawl_urls(absoulte_url,prefix,depth-1)
        except requests.exceptions.RequestException as e:
            print(f"Error crawling {url}: {e}")
    crawl_urls(url,prefix,depth)
    return list(sorted(wanted_urls))  


def set_openai_api_key(api_key):
    if not st.session_state.get("openai_api_key"):
        st.error("Please set your OpenAI API key in the sidebar.")
        st.stop()
    
    os.environ["OPENAI_API_KEY"]=st.session_state.openai_api_key




def generate_database(urls):
    loaders = UnstructuredURLLoader(urls=urls)
    data = loaders.load()
    text_splitter= RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    docs = text_splitter.split_documents(data)
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(docs,embeddings)
    db.save_local("faiss_index")
    return db
