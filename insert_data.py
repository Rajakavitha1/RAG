# insert_data.py
import os
from dotenv import load_dotenv
from pymilvus import MilvusClient

load_dotenv()

def load_knowledge():
    client = MilvusClient(uri=os.getenv("MILVUS_ENDPOINT"))
    collection = os.getenv("COLLECTION_NAME")

    # Clean slate: If it exists, drop it (Simulating the production hazard!)
    if client.has_collection(collection):
        client.drop_collection(collection)

    # Create a simple schema structure
    client.create_collection(
        collection_name=collection,
        dimension=1536 # Matching standard OpenAI embedding dimensions
    )

    print(f"✅ Successfully initialized {collection} and loaded knowledge maps!")

if __name__ == "__main__":
    load_knowledge()

