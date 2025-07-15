from langchain_core.messages import HumanMessage, AIMessage
from graph import graph

def run_refund_agent():
    print("Refund Processing Agent")
    print("=" * 30)
    
    # Initialize conversation state - this persists across the entire session
    conversation_state = None
    
    while True: 
        user_complaint = input("\nPlease describe your refund issue (or 'quit' to exit): ")
        
        if user_complaint.lower() in ['quit', 'exit', 'q']:
            print("Thank you for using our refund service!")
            break
        
        if conversation_state is None:
            # First message - create initial state
            conversation_state = {
                "messages": [HumanMessage(content=user_complaint)],
                "user_current_message": user_complaint,
                "classification": None,
                "intent": None,
                "resolved": False,
                "notes": "",
                "transaction_id": None,
                "transaction_details": None,
                "refund_amount": None,
                "refund_status": None,
                "final_response": "",
                # New conversation fields
                "awaiting_clarification": False,
                "clarification_count": 0,
                "original_request": user_complaint,
                "conversation_context": "",
                "has_sufficient_info": False
            }
        else:
            # Continuing conversation - add new message to existing state
            conversation_state["messages"].append(HumanMessage(content=user_complaint))
            conversation_state["user_current_message"] = user_complaint
        
        # Process through the agent
        result = graph.invoke(conversation_state)
        print(f"\nAgent Response: {result['final_response']}")
        
        # Update conversation state for next turn
        conversation_state = result
        
        # Show conversation status (optional - remove if you don't want to see this)
        if result.get('awaiting_clarification'):
            print("(The agent is waiting for more information from you)")
        
        # If case is resolved, offer to start new conversation
        if result.get('resolved'):
            new_case = input("\nCase resolved! Start a new case? (y/n): ")
            if new_case.lower() in ['y', 'yes']:
                conversation_state = None  # Reset for new conversation
            else:
                break

if __name__ == "__main__":
    run_refund_agent()