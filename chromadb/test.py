import chromadb
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
print(chroma_client.heartbeat())

collection = chroma_client.get_or_create_collection(name="my_collection")
collection.add(
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges", 
        "This is document is about Volcanos"
    ],
    ids=["id1", "id2", "id3"]
)


results = collection.query(
    query_texts=["This is a query document about hawaii"], # Chroma will embed this for you
    n_results=2 # how many results to return
)
print(results)
