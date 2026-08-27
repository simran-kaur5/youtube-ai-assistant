import chromadb
from sentence_transformers import SentenceTransformer

class VideoRAG: 
    def __init__(self):
    
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient( path="./chroma_db" ) 

    def load_collection(self,video_id): 
        self.collection = self.client.get_collection( name=f"video_{video_id}" )

    def create_collection(self, video_id):
        self.collection = self.client.get_or_create_collection(
            name=f"video_{video_id}"
        )

    def add_chunks(self,chunks):
        documents = []
        ids = []
        metadatas = []

        for i, chunk in enumerate(chunks):

            print(f"Adding chunk {i+1}")

            if not chunk.strip():
                print(f"Skipping empty chunk {i}")
                continue

            documents.append(chunk)
            ids.append(f"chunk_{i}")

            first_line = chunk.splitlines()[0]

            metadatas.append({
                "timestamp": first_line
            })

        if not documents:
            raise ValueError("No valid chunks to add")

        embeddings = self.embedder.encode(
            documents
        ).tolist()

        print("Added chunks")
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
    def search(self, query, n_result=3):

    # 1. Convert user question into embedding
        query_embedding = self.embedder.encode([query]).tolist()

        # 2. Search ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_result,
            include=["documents", "metadatas", "distances"]
        )

        # 3. Display retrieved chunks
        # for doc, metadata, distance in zip(
        #     results["documents"][0],
        #     results["metadatas"][0],
        #     results["distances"][0]
        # ):
        #     print(f"Distance: {distance:.3f}")
        #     print(f"Timestamp: {metadata['timestamp']}")
        #     print("Document:")
        #     print(doc)
        #     print("-" * 50)

        return results

