from core.state import State
from core.models import llm

def classify_refundability(state: State) -> State:
    """
    classifies the issue as refundable or non_refundable based on the user_message.
    updates state['classification']
    """

    prompt = f"""
classify the user complaint as either: 
- refundable 
- non_refundable

refundable issues include:
- failed transactions 
- duplicate charges: getting charged twice for the same payment

non_refundable issues include: 
- money sent to the wrong person 
- the user regrets sneding a transaction
- wrong account transfer 


Only respond with one of these two labels. 

user complaint:
"{state['messages']}"
"""
    
    classification = llm.invoke(prompt).strip().lower()
    state["classification"] = classification
    state["notes"] += f"\n[System] Issue classified as: {classification}"
    return state


def classify_intent(state: State) -> State:
    """
    classifies the user intent in the case of the complaint being refundable.
    updates state['intent]
    """

    prompt = f"""
classify the user intent based on their complaint as either: 
- failed_transaction
- duplicate_transaction


only respond with the corresponding label above.

user complaint:
"{state['messages']}"
"""
    
    intent = llm.invoke(prompt).strip()
    state['intent'] = intent
    state["notes"] += f"\n[System] Intent classified as: {intent}"
    return state
