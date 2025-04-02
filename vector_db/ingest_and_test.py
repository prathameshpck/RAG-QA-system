import weaviate
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
import uuid

# --- Config ---
PDF_PATH = "sample.pdf"
CLASS_NAME = "PdfChunk"
CHUNK_SIZE = 300
QUESTION = "Object detection and its types"

# --- Connect to Weaviate v4 ---
client = weaviate.connect_to_local(
    port=8080,
    grpc_port=50051,
    headers={},  # Optional auth headers
)

# --- Check or create the collection ---
collections = client.collections.list_all()
if CLASS_NAME not in collections:
    client.collections.create(
        name=CLASS_NAME,
        vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),  # Manual embedding
        properties=[
            weaviate.classes.config.Property(name="content", data_type=weaviate.classes.config.DataType.TEXT),
        ],
        vector_index_config=weaviate.classes.config.Configure.VectorIndex.hnsw()
    )

collection = client.collections.get(CLASS_NAME)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# --- Extract text from PDF and chunk it ---
def extract_chunks(path, chunk_size):
    all_words = []

    with fitz.open(path) as doc:
        for page_num, page in enumerate(doc):
            try:
                text = page.get_text()
                if not text:
                    continue
                lines = text.split("\n")
                for line in lines:
                    try:
                        words = line.strip().split()
                        all_words.extend(words)
                    except Exception as line_error:
                        print(f"⚠️ Skipping line on page {page_num + 1} due to error: {line_error}")
            except Exception as page_error:
                print(f"🚫 Skipping page {page_num + 1} due to error: {page_error}")

    # Chunk into sequences of n words
    chunks = [" ".join(all_words[i:i + chunk_size]) for i in range(0, len(all_words), chunk_size)]
    return chunks

# --- Ingest chunks into Weaviate ---
def ingest_chunks(chunks):
    for chunk in chunks:
        vector = embedder.encode(chunk, normalize_embeddings=True).tolist()
        collection.data.insert(
            properties={"content": chunk},
            vector=vector
        )

# --- Run a test query ---
def query(question, k=5):
    query_vector = embedder.encode(question, normalize_embeddings=True).tolist()
    results = collection.query.near_vector(
        near_vector=query_vector,
        limit=k,
    )

    for i, res in enumerate(results.objects):
        print(f"\n--- Match {i+1} ---\n{res.properties['content']}...")

# --- Main ---
if __name__ == "__main__":
    # chunks = extract_chunks(PDF_PATH, CHUNK_SIZE)
    # print(f"📄 Extracted {len(chunks)} chunks from {PDF_PATH}")
    # ingest_chunks(chunks)
    # print("✅ Ingestion complete")

    print(f"\n🔍 Running test query: {QUESTION}")
    query(QUESTION)
    client.close()
