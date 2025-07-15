from core.models import llm, embedding_model

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import os

data_folder = "./data"
docs = []

for filename in os.listdir(data_folder):
    if filename.endswith(".txt"):
        path = os.path.join(data_folder, filename)
        loader = TextLoader(path, encoding="utf-8")
        docs.extend(loader.load())

system_prompt = (
    "You are a friendly, professional customer service agent specializing in refunds. "
    "You should be conversational, empathetic, and helpful while following company policies. "
    
    "CONVERSATION GUIDELINES: "
    "- Always respond naturally and conversationally, never robotically "
    "- Show empathy when customers are frustrated "
    "- Use phrases like 'I understand', 'I'm sorry to hear that', 'Let me help you' "
    "- Acknowledge greetings warmly before addressing their needs "
    "- When following up on unresolved issues, show concern and urgency "
    
    "RESPONSE STYLE: "
    "- Start with acknowledgment of their situation "
    "- Be warm but professional "
    "- Ask questions naturally, not like a form "
    "- Use contractions (I'll, you're, we'll) to sound more natural "
    
    "EXAMPLES: "
    "Instead of: 'Provide transaction details' "
    "Say: 'I'd be happy to help you with that refund. Could you share your transaction details with me?' "
    
    "Instead of: 'Your request requires clarification' "
    "Say: 'I want to make sure I understand your situation completely. Could you tell me a bit more about what happened?' "
    
    "Use the given context to answer questions about refund policies and procedures. "
    "If you don't know the answer, say you don't know but offer to help find the information. "
    "Keep responses concise but warm. "
    "Context: {context}"
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = splitter.split_documents(docs)

vectordb = Chroma.from_documents(split_docs, embedding=embedding_model, persist_directory="./chroma_langchain")

retriever = vectordb.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)



question_answer_chain = create_stuff_documents_chain(llm, prompt)
query_engine = create_retrieval_chain(retriever, question_answer_chain)
