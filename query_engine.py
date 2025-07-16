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


def build_query_engine():
    system_prompt = (
    "You are a refund policy analysis agent. Your job is to analyze user messages against refund policies and provide clear classification guidance."
    
    "ANALYSIS TASK:"
    "- Determine if the user's situation is REFUNDABLE, NON-REFUNDABLE, or requires ESCALATION"
    "- Extract key details: transaction type, timeframe, amounts, error codes"
    "- Identify which specific policy rules apply"
    
    "RESPONSE FORMAT:"
    "Classification: [REFUNDABLE/NON-REFUNDABLE/ESCALATION]"
    "Reason: [Specific policy rule that applies]"
    "Key Details: [Transaction info, dates, amounts]"
    "Recommended Action: [What the agent should do next]"
    
    "POLICY RULES TO CHECK:"
    "1. System error + < 30 days = REFUNDABLE"
    "2. User error = NON-REFUNDABLE"
    "3. > 30 days = NON-REFUNDABLE"
    "4. > $15,000 = NON-REFUNDABLE"
    "5. Fraud flags = ESCALATE"
    "6. Unclear evidence = ESCALATE"
    
    "EXAMPLES:"
    "User: 'My payment failed but I was charged' → classification: REFUNDABLE, reason: System error"
    "User: 'I sent money to wrong account 2 months ago' → classification: NON-REFUNDABLE, reason: User error + > 30 days"
    
    "Use the context below to make accurate policy-based decisions:"
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
    query_result = create_retrieval_chain(retriever, question_answer_chain)

    return query_result


query_engine = build_query_engine()


def 
