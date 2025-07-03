import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from langchain.tools import BaseTool
from langchain_voyageai import VoyageAIEmbeddings

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "homeinsight"
COLLECTION_NAME = "properties"

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

embedding_model = VoyageAIEmbeddings()

vector_search = MongoDBAtlasVectorSearch(
    embedding=embedding_model,
    collection=collection,
    index_name="vector_index",
    text_key="description",  # your text searchable field
    embedding_key="embedding",
)

class RealEstateLookupTool(BaseTool):
    name = "real_estate_lookup"
    description = "Search for real estate property details using semantic search."

    def _run(self, query: str, n: int = 5):
        results = vector_search.similarity_search_with_score(query, n)
        return str(results)

    async def _arun(self, query: str, n: int = 5):
        return self._run(query, n)

mongo_tool = RealEstateLookupTool()
tools = [mongo_tool]
