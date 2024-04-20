from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-4",
    chunk_size=100,
    chunk_overlap=0,
)

def get_embeddings(model_name="nomic-ai/nomic-embed-text-v1"):
    model_kwargs = {'trust_remote_code': True}
    embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)
    return embeddings

def retrieve_documents(path) -> list:
    """
    Retrieve the documensts recursively
    :param path: path of documents
    :return: concatenated documents
    """
    documents = []
    root_dir = Path(path)
    for file_path in root_dir.rglob('*'):
        # read PDF/text file
        if file_path.is_file():
            pages = None
            if file_path.suffix == '.pdf':
                loader = PyPDFLoader(file_path)
                pages = loader.load_and_split(text_splitter=text_splitter)
            elif file_path.suffix == '.txt':
                loader = TextLoader(file_path)
                pages = loader.load_and_split(text_splitter=text_splitter)

            if pages:
                documents.extend(pages)

    return documents

def get_vector_db(documents, embeddings):
    """
    Return Vector Database from LangChain documents
    :param documents: LangChain documents
    :param embeddings: Embeddings
    :return: Vector database
    """
    faiss_index = FAISS.from_documents(documents, embeddings)
    return faiss_index

def create_db(vector_path, raw_file="data/raw_data/"):
    
    embedding = get_embeddings()

    if vector_path!='':
        vector_db = FAISS.load_local(folder_path=vector_path, index_name="faiss_index", embeddings=embedding, allow_dangerous_deserialization=True)
        return vector_db

    documents = retrieve_documents(raw_file)
    vector_db = get_vector_db(documents, embeddings=embedding)
    vector_db.save_local(folder_path="data/vector_db/", index_name="faiss_index")

    return vector_db