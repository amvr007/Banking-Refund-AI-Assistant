from core.state import State


def route_by_classification(state: State) -> State:
    classification = state.get("classification")
    if classification == "refundable":
        return "classify_intent"
    
    else: 
        return "give_user_reply"
    

def route_by_intent(state: State) -> State:
    intent = state.get("intent")

    if intent in ["failed_transaction", "duplicate_transaction"]: 
        return "extract_transaction_id_node"
    
    else: 
        return "give_user_reply"
    

def route_to_reply(state):
    """
    This router decides how to handle the final response based on 
    whether we have enough information to make a decision.
    """
    # If we don't have sufficient info, ask for clarification
    if not state.get("has_sufficient_info", False):
        return "ask_questions"
    
    # If we're waiting for clarification, process their response first
    if state.get("awaiting_clarification", False):
        return "process_answers"
    
    # Otherwise, give the final reply
    return "give_user_reply"


def route_by_clarity(state):
    # FORCE PROCEED after 1 clarification attempt
    clarification_count = state.get("clarification_count", 0)
    
    if clarification_count >= 1:
        return "classify_refundability"  # Stop asking, just proceed
    
    if state.get("awaiting_clarification"):
        return "process_answers"
    
    if state.get("has_sufficient_info"):
        return "classify_refundability"
    else:
        return "ask_questions"

def route_after_clarification_check(state):
    """
    This router decides what to do after we've checked if the request is clear enough.
    It's like a customer service rep deciding: 'Now that I've assessed the situation,
    what's my next step?'
    """
    if state.get("has_sufficient_info"):
        return "classify_refundability"  # Request is clear, proceed with normal workflow
    else:
        return "ask_questions"  # Request is unclear, ask for clarification