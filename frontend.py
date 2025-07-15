import streamlit as st
from langchain_core.messages import HumanMessage
from graph import graph

st.title("Refund Processing Agent")

# Initialize session state for conversation
if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Describe your refund issue"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process with agent
    if st.session_state.conversation_state is None:
        # First message
        initial_state = {
            "messages": [HumanMessage(content=prompt)],
            "user_current_message": prompt,
            "classification": None,
            "intent": None,
            "resolved": False,
            "notes": "",
            "transaction_id": None,
            "transaction_details": None,
            "refund_amount": None,
            "refund_status": None,
            "final_response": "",
            "awaiting_clarification": False,
            "clarification_count": 0,
            "original_request": prompt,
            "conversation_context": "",
            "has_sufficient_info": False
        }
        st.session_state.conversation_state = initial_state
    else:
        # Continue conversation
        st.session_state.conversation_state["messages"].append(HumanMessage(content=prompt))
        st.session_state.conversation_state["user_current_message"] = prompt

    # Get agent response
    try:
        result = graph.invoke(st.session_state.conversation_state)
        response = result["final_response"]
        
        # Update conversation state
        st.session_state.conversation_state = result
        
        # Add agent response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
            
        # Debug info in sidebar
        with st.sidebar:
            st.header("Debug Info")
            st.write(f"Intent: {result.get('intent')}")
            st.write(f"Classification: {result.get('classification')}")
            st.write(f"Transaction ID: {result.get('transaction_id')}")
            st.write(f"Awaiting Clarification: {result.get('awaiting_clarification')}")
            st.write(f"Resolved: {result.get('resolved')}")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write("Debug: Check your graph structure and node functions")