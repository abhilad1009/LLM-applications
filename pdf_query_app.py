import streamlit as st
import pinecone
from langchain.llms import OpenAI
from langchain.agents import TextLoader, TextAskAgent


pinecone.init(api_key="YOUR_PINECONE_API_KEY", environment="YOUR_PINECONE_ENVIRONMENT")
index = pinecone.Index("pdf_index")

def upload_and_index_pdf(file):
    text = TextLoader.from_file(file).text
    index.upsert(text, {"id": file.name})
    st.success("PDF uploaded and indexed successfully!")

def query_pdfs(query):
    results = index.query(query, top_k=5)
    responses = []
    for result in results:
        pdf_id = result["id"]
        response = llm(query, documents=[{"id": pdf_id, "text": result["text"]}])
        responses.append((pdf_id, response["answer"]))
    return responses

if __name__ == "main":

    st.title("PDF Search with Langchain and Pinecone")

    llm = OpenAI(temperature=0.7)  # Adjust temperature as needed

    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file:
        upload_and_index_pdf(pdf_file)

    query = st.text_input("Enter your query")
    if query:
        responses = query_pdfs(query)
        for pdf_id, response in responses:
            st.write(f"**PDF:** {pdf_id}")
            st.write(f"**Answer:** {response}")



# pip install streamlit langchain pinecone

# streamlit run app.py
