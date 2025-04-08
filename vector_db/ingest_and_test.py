import os
from pathlib import Path
from typing import List, Tuple
import weaviate
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import hashlib

# --- Config ---
DATA_DIR = "./data/processed_transcripts"
CHUNK_SIZE = 200
CLASS_NAME = "TextChunk"
QUERY = "What is the most important when it comes to attraction and sex?"


def connect_weaviate() -> weaviate.WeaviateClient:
    return weaviate.connect_to_local(
        port=8080,
        grpc_port=50051,
        skip_init_checks=True
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


def load_and_chunk_documents(folder: str, chunk_size: int) -> Tuple[List[str], List[Tuple[str, str]]]:
    doc_texts = []
    chunked_docs = []

    for filepath in Path(folder).glob("*.txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        words = text.split()
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        doc_texts.append(" ".join(words))  # full document text
        chunked_docs.extend([(chunk, filepath.stem) for chunk in chunks])

    return doc_texts, chunked_docs


def ingest_to_weaviate(collection, embedder, chunked_docs: List[Tuple[str, str]]):
    seen_hashes = set()

    for chunk, doc_id in chunked_docs:
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


# def run_topic_modeling(doc_texts: List[str], num_topics: int = 6):
#     vectorizer_model = CountVectorizer(stop_words="english", min_df=2, max_df=0.95)
#     topic_model = BERTopic(vectorizer_model=vectorizer_model)
#     topics, _ = topic_model.fit_transform(doc_texts)

#     # Create wordclouds for each topic
#     unique_topics = list(set(topics) - {-1})
#     fig_rows = (num_topics + 2) // 3
#     fig, axs = plt.subplots(fig_rows, 3, figsize=(15, fig_rows * 4))
#     axs = axs.flatten()

#     for i, topic in enumerate(unique_topics[:num_topics]):
#         words = dict(topic_model.get_topic(topic))
#         wc = WordCloud(width=400, height=300, background_color='white').generate_from_frequencies(words)
#         axs[i].imshow(wc, interpolation="bilinear")
#         axs[i].axis("off")
#         axs[i].set_title(f"Topic {topic}")

#     for j in range(i + 1, len(axs)):
#         axs[j].axis("off")

#     plt.tight_layout()
#     plt.show()



def run_topic_modeling_lda(doc_texts, num_topics = 50, max_words=15):
    # Step 1: Create the document-term matrix
    vectorizer = CountVectorizer(stop_words='english', max_df=0.95, min_df=2)
    dtm = vectorizer.fit_transform(doc_texts)
    vocab = vectorizer.get_feature_names_out()

    # Step 2: Fit the LDA 25model
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(dtm)

    # Step 3: Visualize each topic as a word cloud
    fig_rows = (num_topics + 2) // 3
    fig, axs = plt.subplots(fig_rows, 3, figsize=(15, fig_rows * 4))
    axs = axs.flatten()

    for topic_idx, topic in enumerate(lda.components_[:num_topics]):
        word_freqs = {vocab[i]: topic[i] for i in topic.argsort()[-max_words:]}
        wc = WordCloud(width=400, height=300, background_color='white').generate_from_frequencies(word_freqs)
        axs[topic_idx].imshow(wc, interpolation="bilinear")
        axs[topic_idx].axis("off")
        axs[topic_idx].set_title(f"Topic {topic_idx}")

    for j in range(topic_idx + 1, len(axs)):
        axs[j].axis("off")

    plt.tight_layout()
    plt.show()


def query_similar_chunks(collection, embedder, query: str, k: int = 5):
    vector = embedder.encode(query, normalize_embeddings=True).tolist()
    results = collection.query.near_vector(near_vector=vector, limit=k)

    print(f"\n🔍 Top {k} most relevant chunks for query: '{query}'")
    for i, res in enumerate(results.objects):
        print(f"\n--- Match {i + 1} ---")
        print(f"Source: {res.properties['source_doc']}")
        print(res.properties['content'][:500], "...\n")


def main():
    client = connect_weaviate()
    collection = setup_weaviate_class(client, CLASS_NAME)
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    doc_texts, chunked_docs = load_and_chunk_documents(DATA_DIR, CHUNK_SIZE)

    print(f"📄 Loaded {len(doc_texts)} documents and {len(chunked_docs)} chunks.")
    print("📥 Ingesting into Weaviate...")
    ingest_to_weaviate(collection, embedder, chunked_docs)
    print("✅ Ingestion complete.")

    print("\n🎯 Running topic modeling at document level...")
    run_topic_modeling_lda(doc_texts)

    print("\n🔎 Querying vector DB...")
    query_similar_chunks(collection, embedder, QUERY)

    client.close()


if __name__ == "__main__":
    main()
