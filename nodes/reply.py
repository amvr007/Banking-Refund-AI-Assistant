from core.state import State
from langchain_core.messages import AIMessage
from utils.query_engine import query_engine
from typing import Dict, Any

def give_user_reply(state: State, query_engine) -> Dict[str, Any]:
    intent = state.get("intent")
    classification = state.get("classification") 
    refund_status = state.get("refund_status")
    transaction_id = state.get("transaction_id")
    refund_amount = state.get("refund_amount")

    context_info = ""
    if transaction_id:
        context_info += f"Transaction ID: {transaction_id}. "
    if refund_amount:
        context_info += f"Refund amount: ${refund_amount}. "
    
    if intent is None or intent == "unknown":
        query_text = (
            f"{context_info}A customer has contacted us but their request is unclear. "
            "What should we ask them to better understand their refund-related issue? "
            "Provide a helpful response that guides them to give us the information we need."
        )
    elif classification == "non_refundable":
        query_text = (
            f"{context_info}A customer's transaction has been classified as non-refundable. "
            "Explain why this transaction doesn't qualify for a refund according to our policies, "
            "and offer any alternatives or next steps they might have."
        )
    elif refund_status == "approved":
        query_text = (
            f"{context_info}A customer's refund request has been approved. "
            "Provide them with confirmation details, processing timeline, "
            "and what they should expect next according to our refund processing procedures."
        )
    elif refund_status == "denied":
        query_text = (
            f"{context_info}A customer's refund request has been reviewed and denied. "
            "Explain this decision professionally while referencing our refund policies, "
            "and let them know about any appeal or escalation options available."
        )
    else:
        query_text = (
            f"{context_info}A customer is asking about their refund request status. "
            "Provide a helpful update about the review process and expected timelines "
            "according to our standard procedures."
        )

    try: 
        response = query_engine.invoke({"input": query_text})
        if isinstance(response, dict) and 'answer' in response:
            response_text = response['answer']
        elif hasattr(response, 'answer'):
            response_text = response.answer
        elif isinstance(response, str):
            response_text = response
        else:
            response_text = str(response)
        
        # Determine resolution status
        is_resolved = classification == "non_refundable" or refund_status in ["approved", "denied"]
        
    except Exception as e:
        response_text = (
            "I apologize, but I'm currently experiencing some technical difficulties "
            "accessing our refund policy information. Please hold on while I connect you "
            "with a specialist who can help you immediately, or feel free to try again in a moment."
        )
        is_resolved = False
        print(f"Query engine error: {str(e)}")

    ai_message = AIMessage(content=response_text)
    
    return {
        "messages": [ai_message],
        "final_response": response_text,
        "resolved": is_resolved,
        "current_step": "user_reply_given"
    }