def encrypt(text, shift):
    result = ""
    for i in range(len(text)):
        char = text[i]
        if char.isupper():
            result += chr((ord(char) + shift - 65) % 26 + 65)
        elif char.islower():
            result += chr((ord(char) + shift - 97) % 26 + 97)
        else:
            result += char
    return result

def decrypt(text, shift):
    return encrypt(text, -shift)

plain_text = "jvn_Nzdq4Z4yhi5refx44JHpZJgbe3IB3xVyXJlN82wdQpw2XAqskbiq"
shift = -3

encrypted_text = encrypt(plain_text, shift)
print(f"Encrypted: {encrypted_text}")

decrypted_text = decrypt(encrypted_text, shift)
print(f"Decrypted: {decrypted_text}")

################################################
import os
import threading
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

def create_vector_db(json_dir, model_name, db_path):
    embed_function = HuggingFaceEmbeddings(model_name=model_name)

    # text splitter to chunk long documents into smaller sections
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    # store all documents
    documents = []

    for json_file in os.listdir(json_dir):
        if json_file.endswith(".json"):
            with open(os.path.join(json_dir, json_file), 'r') as f:
                data = f.read()
                chunks = text_splitter.split_text(data)
                for chunk in chunks: # create LangChain Document objects for each chunk
                    documents.append(Document(page_content=chunk, metadata={"source": json_file}))

    # create FAISS vector store using LangChain
    vector_store = FAISS.from_documents(documents, embed_function)

    # save the index to disk
    vector_store.save_local(db_path)
    print(f"Vector DB created and saved to {db_path}")

def similarity_search(embedding, db_path):
    # Load the FAISS vector store
    vector_store = FAISS.load_local(db_path)
    # Perform similarity search
    results = vector_store.similarity_search(embedding)
    print("Similarity search results:", results)
    return results

def process_document(json_dir, model_name, db_path):
    # Thread 1: Create vector DB
    thread1 = threading.Thread(target=create_vector_db, args=(json_dir, model_name, db_path))
    thread1.start()
    thread1.join()  # Ensure the vector DB is created before performing similarity search

    # Thread 2: Perform similarity search
    # Example embedding for similarity search (replace with actual embedding)
    example_embedding = [0.1, 0.2, 0.3]
    thread2 = threading.Thread(target=similarity_search, args=(example_embedding, db_path))
    thread2.start()
    thread2.join()

def main():
    json_dir = "/Users/abhiraj/Espresso/Developer_Stuff/projects/In-house/vectorDB/Information Technology"
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    db_path = "vectorDB/IT_skill_jsons_vectorDB_v1"

    process_document(json_dir, model_name, db_path)

if __name__ == "__main__":
    main()

################################################################
import os
import hashlib
import threading
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

def hash_document_content(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def create_vector_db(json_file, model_name, db_path):
    embed_function = HuggingFaceEmbeddings(model_name=model_name)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documents = []

    with open(json_file, 'r') as f:
        data = f.read()
        chunks = text_splitter.split_text(data)
        for chunk in chunks:
            documents.append(Document(page_content=chunk, metadata={"source": json_file}))

    vector_store = FAISS.from_documents(documents, embed_function)
    vector_store.save_local(db_path)
    print(f"Vector DB created and saved to {db_path}")

def similarity_search(embedding, db_path):
    vector_store = FAISS.load_local(db_path)
    results = vector_store.similarity_search(embedding)
    print("Similarity search results:", results)
    return results

def process_document(json_file, model_name, base_db_path):
    with open(json_file, 'r') as f:
        content = f.read()
    doc_hash = hash_document_content(content)
    db_path = os.path.join(base_db_path, f"{doc_hash}.faiss")

    if not os.path.exists(db_path):
        thread1 = threading.Thread(target=create_vector_db, args=(json_file, model_name, db_path))
        thread1.start()
        thread1.join()
    else:
        print(f"Vector DB for {json_file} already exists at {db_path}")

    example_embedding = [0.1, 0.2, 0.3]
    thread2 = threading.Thread(target=similarity_search, args=(example_embedding, db_path))
    thread2.start()
    thread2.join()

def main():
    json_dir = "/Users/abhiraj/Espresso/Developer_Stuff/projects/In-house/vectorDB/Information Technology"
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    base_db_path = "vectorDB"

    if not os.path.exists(base_db_path):
        os.makedirs(base_db_path)

    for json_file in os.listdir(json_dir):
        if json_file.endswith(".json"):
            process_document(os.path.join(json_dir, json_file), model_name, base_db_path)

if __name__ == "__main__":
    main()
