import os
from pathlib import Path
from typing import List, Tuple, Dict
import weaviate
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import hashlib
import json 
import math 


# --- Config ---
DATA_DIR = "./data/processed_transcripts"
CHUNK_SIZE = 300
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
    """Returns full document texts, chunked (text, doc_id) pairs, and chunked-only texts for LDA chunk-mode."""
    doc_texts = []
    chunked_docs = []
    chunked_texts = []

    for filepath in Path(folder).glob("*.txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        words = text.split()
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        doc_texts.append(" ".join(words))  # full document text
        chunked_docs.extend([(chunk, filepath.stem) for chunk in chunks])
        chunked_texts.extend(chunks)

    return doc_texts, chunked_docs, chunked_texts


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
#         axs[j].axis("):off")

#     plt.tight_layout()
#     plt.show()




def run_topic_modeling_lda(
    texts: List[str], num_topics: int = 10, max_words: int = 15,
    mode: str = "chunk", json_path: str = "./topic_words.json"
) -> Dict[int, Dict[str, float]]:
    """
    Perform LDA topic modeling and display paginated wordclouds for each topic.
    Also saves all topic word frequencies into a single JSON file.

    Returns:
        Dictionary of topic -> word: weight
    """
    assert mode in ["chunk", "document"], "mode must be 'chunk' or 'document'"

    print(f"🧠 Running LDA topic modeling at {mode}-level on {len(texts)} items...")

    vectorizer = CountVectorizer(stop_words='english', max_df=0.95, min_df=2)
    dtm = vectorizer.fit_transform(texts)
    vocab = vectorizer.get_feature_names_out()

    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(dtm)

    topic_word_dict = {}

    # Paginate: display 5 topics per page
    topics_per_page = 5
    num_pages = math.ceil(num_topics / topics_per_page)

    for page in range(num_pages):
        start_idx = page * topics_per_page
        end_idx = min((page + 1) * topics_per_page, num_topics)
        current_topics = end_idx - start_idx

        fig, axs = plt.subplots(current_topics, 1, figsize=(12, current_topics * 4))
        if current_topics == 1:
            axs = [axs]

        for i, topic_idx in enumerate(range(start_idx, end_idx)):
            topic = lda.components_[topic_idx]
            word_freqs = {vocab[j]: topic[j] for j in topic.argsort()[-max_words:]}
            topic_word_dict[topic_idx] = word_freqs

            wc = WordCloud(width=1000, height=400, background_color='white', max_font_size=80)
            wc.generate_from_frequencies(word_freqs)

            axs[i].imshow(wc, interpolation="bilinear")
            axs[i].axis("off")
            axs[i].set_title(f"Topic {topic_idx}", fontsize=16, pad=10)

        plt.tight_layout()
        plt.show()

    # Save topic word dictionary to JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(topic_word_dict, f, indent=2)
        print(f"✅ Saved topic words to {json_path}")

    return topic_word_dict


def query_similar_chunks(collection, embedder, query: str, k: int = 5):
    vector = embedder.encode(query, normalize_embeddings=True).tolist()
    results = collection.query.near_vector(near_vector=vector, limit=k)

    print(f"\n🔍 Top {k} most relevant chunks for query: '{query}'")
    for i, res in enumerate(results.objects):
        print(f"\n--- Match {i + 1} ---")
        print(f"Source: {res.properties['source_doc']}")
        print(res.properties['content'][:500], "...\n")


def main():
    # client = connect_weaviate()
    # collection = setup_weaviate_class(client, CLASS_NAME)
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    doc_texts, chunked_docs, chunked_texts = load_and_chunk_documents(DATA_DIR, CHUNK_SIZE)

    print(f"📄 Loaded {len(doc_texts)} documents and {len(chunked_docs)} chunks.")
    print("📥 Ingesting into Weaviate...")
    # ingest_to_weaviate(collection, embedder, chunked_docs)
    print("✅ Ingestion complete.")

    print("\n🎯 Running topic modeling at chunk level...")
    run_topic_modeling_lda(doc_texts, mode = "document")

    print("\n🔎 Querying vector DB...")
    # query_similar_chunks(collection, embedder, QUERY)

    # client.close()


if __name__ == "__main__":
    main()
