from pypdf import PdfReader

def extract_Pdf_Text(pdf_path):
    reader = PdfReader(pdf_path)

    print(len(reader.pages))

    text=""

    for page in reader.pages:
        page_text=page.extract_text()
        text += page_text + "\n"

    return text


#Uploading document

#Extracting Pdf content

#Splitting the content into chunks

#Embedding the chunks

#Storing the vectors into chromaDB

#Retrieving the context from ChromaDB for given query

#Calling LLM with Query and context





