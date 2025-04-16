import weaviate 
from sentence_transformers import SentenceTransformer 
from typing import List, Tuple 
import hashlib
from pathlib import Path
from tqdm import tqdm 
from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams

def load_and_chunk_documents(folder: str, chunk_size: int):
    """
        Loads documents from a folder, chunks them into smaller pieces. Returns both raw and 

    """
    doc_text = [] 
    chunked_docs = [] 
    chunked_texts = [] 
    for filepath in Path(folder).glob("*.txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        doc_text.append(text) 
        words = text.split()
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        chunked_docs.extend([(chunk, filepath.stem) for chunk in chunks])
        chunked_texts.extend(chunks)        

    return doc_text, chunked_docs, chunked_texts


def connect_weaviate() -> weaviate.WeaviateClient:
    return weaviate.connect_to_custom(
    http_host="weaviate",
    http_port="8080",
    http_secure=False,
    grpc_host="weaviate",
    grpc_port="50051",
    grpc_secure=False,
)

def setup_weaviate_class(client: weaviate.WeaviateClient, class_name: str):
    if class_name in client.collections.list_all():
        client.collections.delete(class_name)

    if class_name not in client.collections.list_all():
        client.collections.create(
            name=class_name,
            vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
            properties=[
                weaviate.classes.config.Property(name="content", data_type=weaviate.classes.config.DataType.TEXT),
                weaviate.classes.config.Property(name="source_doc", data_type=weaviate.classes.config.DataType.TEXT),
            ],
            vector_index_config=weaviate.classes.config.Configure.VectorIndex.hnsw()
        )
    return client.collections.get(class_name)

def ingest_to_weaviate(collection, embedder, chunked_docs: List[Tuple[str, str]]):
    """
    Ingests chunked documents into Weaviate, ensuring no duplicates are added.Also has code for non-batch import for benchmarking 

    """
    
    seen_hashes = set()
    for chunk, doc_id in tqdm(chunked_docs):
        # Compute a stable25 hash of the chunk
        chunk_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
        if chunk_hash in seen_hashes:
            continue
        seen_hashes.add(chunk_hash)

        # Generate vector and insert into Weaviate
        vector = embedder.encode(chunk, normalize_embeddings=True).tolist()
        collection.data.insert(properties={
            "content": chunk,
            "source_doc": doc_id
        }, vector=vector)


    # seen_hashes = set()
    # failed_count = 0
    # failed_objects = []

    # with collection.batch.dynamic() as batch:
    #     for chunk, doc_id in tqdm(chunked_docs, desc="Ingesting chunks to Weaviate"):
    #         # Compute a stable hash of the chunk
    #         chunk_hash = hashlib.md5(chunk.encode('utf-8')).hexdigest()
    #         if chunk_hash in seen_hashes:
    #             continue
    #         seen_hashes.add(chunk_hash)

    #         try:
    #             vector = embedder.encode(chunk, normalize_embeddings=True).tolist()
    #             batch.add_object(
    #                 properties={
    #                     "content": chunk,
    #                     "source_doc": doc_id
    #                 },
    #                 vector=vector
    #             )
    #         except Exception as e:
    #             failed_count += 1
    #             failed_objects.append({"chunk": chunk, "error": str(e)})
    #             if failed_count > 10:
    #                 print("Batch import stopped due to excessive errors.")
    #                 break

    # if failed_objects:
    #     print(f"Number of failed imports: {len(failed_objects)}")
    #     print(f"First failed object: {failed_objects[0]}")


def query_similar_chunks(collection, embedder, query: str, k: int = 5):
    vector = embedder.encode(query, normalize_embeddings=True).tolist()
    results = collection.query.near_vector(near_vector=vector, limit=k)
    return results

