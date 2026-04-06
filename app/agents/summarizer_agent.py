from langchain_groq import ChatGroq

summarizer_agent=ChatGroq(

    model="llama-3.3-70b-versatile",
    temperature=0.1
    
)