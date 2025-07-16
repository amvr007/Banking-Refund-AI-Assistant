from core.state import State
from langchain_core.messages import AIMessage
from query_engine import query_engine
from typing import Dict, Any

def detect_unclear_request(state, query_engine):
    current_message = state["user_current_message"]
    
    # Simple keyword-based check first (faster and more reliable)
    has_transaction_id = any(pattern in current_message.lower() for pattern in [
        'transaction', 'order', '#', 'txn', '-', 'id:'
    ])
    
    has_issue_type = any(issue in current_message.lower() for issue in [
        'refund', 'duplicate', 'charged', 'failed', 'unauthorized', 'wrong', 'error'
    ])
    
    # If we have both, proceed immediately
    if has_transaction_id and has_issue_type:
        return {
            "has_sufficient_info": True,
            "awaiting_clarification": False
        }
    
    # Only ask for clarification if we're really missing key info
    return {
        "has_sufficient_info": False,
        "awaiting_clarification": True
    }


def generate_clarification_questions(state, query_engine):
    current_message = state["user_current_message"]
    
    # Be very specific about what's missing
    query = f"""
    Customer said: "{current_message}"
    
    QUICK ASSESSMENT: What's the ONE most important thing missing?
    - If no transaction ID mentioned: Ask for transaction ID only
    - If no clear problem mentioned: Ask what went wrong only
    - If both are present: Say "I understand you need help with a refund. Let me process this for you."
    
    Generate ONE specific question, not a list of questions.
    """
    
    response = query_engine.invoke({"input": query})
    
    return {
        "messages": [AIMessage(content=response['answer'])],
        "awaiting_clarification": True,
        "clarification_count": state.get("clarification_count", 0) + 1,
        "resolved": False
    }

def process_clarification_response(state, query_engine):
    # Get ALL messages, not just the last one
    conversation = []
    for msg in state["messages"]:
        conversation.append(f"{msg.__class__.__name__}: {msg.content}")
    
    conversation_text = "\n".join(conversation)
    
    query = f"""
    EXTRACTION TASK: From this conversation, extract:
    
    Conversation:
    {conversation_text}
    
    EXTRACT:
    1. Transaction ID (any UUID or alphanumeric code)
    2. Issue type (duplicate, failed, unauthorized, etc.)
    3. Any amounts mentioned
    4. Payment method if mentioned
    5. Any dates mentioned
    
    IMPORTANT: If transaction ID and issue type are found, respond with "SUFFICIENT_INFO_FOUND"
    Otherwise respond with "STILL_NEED_MORE"
    
    Summary the key details found.
    """
    
    response = query_engine.invoke({"input": query})
    
    # Check if we now have enough info
    has_sufficient = "SUFFICIENT_INFO_FOUND" in response['answer']
    
    return {
        "conversation_context": response['answer'],
        "user_current_message": conversation_text,  # Full context
        "awaiting_clarification": False,
        "has_sufficient_info": has_sufficient,
        "clarification_count": state.get("clarification_count", 0)
    }