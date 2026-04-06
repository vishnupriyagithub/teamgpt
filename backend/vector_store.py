import chromadb

CHROMA_DB_DIR = "data/chroma"

client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

def get_project_collection(project_id: str):
    return client.get_or_create_collection(
        name=f"project_{project_id}",
        metadata={"project_id": project_id}
    )
    
