
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import CharacterTextSplitter

def build_vectorstore_from_filtered(df, persist_dir="chroma_index", force_rebuild=False):
    embeddings = HuggingFaceEmbeddings(model_name="mixedbread-ai/mxbai-embed-large-v1")
    if force_rebuild and os.path.exists(persist_dir):
        import shutil
        shutil.rmtree(persist_dir)

    print(f"Building vectorstore from {len(df)} filtered meals.")
    loader = DataFrameLoader(df[['title']], page_content_column='title')
    documents = loader.load()
    splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    docs = splitter.split_documents(documents)
    return Chroma.from_documents(docs, embedding=embeddings, persist_directory=persist_dir)

def setup_rag_chain(vectorstore, k=25):
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": k})
