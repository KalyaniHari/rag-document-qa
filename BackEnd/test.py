from rag import extract_Pdf_Text
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

content = extract_Pdf_Text("C:/DEV/Projects/legal-ai-assistant-poc/BackEnd/Uploads/CMS_AMA_CPT_license_agreement.pdf")

model = SentenceTransformer("all-MiniLM-L6-v2")

paragraphs = content.split("\n \n")

for i, paragraph in enumerate(paragraphs):
    print(f"---Paragraph{i+1}---")
    print(paragraph[:100])

embeddings = []
for paragraph in paragraphs:
    embedding = model.encode(paragraph)
    embeddings.append(embedding)
    
print(len(embeddings))

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(
    name = "Rag_Documents"
)

for i in range(len(paragraphs)):
    collection.add(
        documents =paragraphs[i],
        embeddings=embeddings[i].tolist(),
        ids=str(i)
    )
print("Data stored in ChromaDB successfully!")

results = collection.get()
#print(results)
#print(results["documents"])
query ="Give information about AMA waranties"
query_embedding=model.encode(query)

query_result = collection.query(
    query_embeddings=query_embedding.tolist(),
    n_results = 3
)

context="\n\n".join(query_result["documents"][0])

#llm calling
api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key = api_key)

messages = [
    {
        "role" : "system",
        "content": "You are a knowledge assistant and answer only based on the provided context. If you don't find answer in the given context, just say information is not available"
    },
    {
        "role" : "user",
        "content": f"""
        query:{query},
        context:{context}"""
    }
]

response = openai_client.chat.completions.create(
    model = "gpt-4o-mini",
    messages=messages
)

print(response.choices[0].message.content)













