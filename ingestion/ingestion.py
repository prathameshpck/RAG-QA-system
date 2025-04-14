from ingestion_utils import *
import weaviate 
# from topic_modelling.preprocessing import load_and_chunk_documents 
from sentence_transformers import SentenceTransformer


def main():

    doc_texts, chunked_docs, chunked_texts = load_and_chunk_documents("./dataset", 350) 
    print("Loaded and chunked documents.")

    client = connect_weaviate() 
    collection = setup_weaviate_class(client, "Huberman_Lab")
    print("Connected to Weaviate and set up class.") 

    embedder = SentenceTransformer("all-MiniLM-L6-v2") 

    print("Loaded SentenceTransformer model.") 
    print("Ingesting data into Weaviate...")
    ingest_to_weaviate(collection, embedder, chunked_docs)

    print("Ingestion complete.")

    # print(f"Weaviate class 'Huberman_Lab' contains the following properties:{trans}")
    
    # query = "What is the best way to learn a new language?" 
    # k = 5 
    # print(f"Querying for similar chunks to: '{query}'") 
    # results = query_similar_chunks(collection, embedder, query, k)
    # # print(f"Query complete. Results: {results}")
    client.close()
if __name__ == "__main__":
    main()