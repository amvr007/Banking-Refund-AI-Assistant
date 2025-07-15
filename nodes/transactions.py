import pandas as pd 
from core.state import State
from typing import Dict, Any

df = pd.read_csv('data/transactions.csv')


import re
from typing import Optional, Dict, Any

def extract_transaction_id(message: str) -> Optional[str]:
    """Extract transaction ID from user message"""
    patterns = [
        r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',  # UUID format
        r'#?([A-Z]{3}\d+)',  # TXN123 or #TXN123
        r'#(\d{6,})',        # #123456
        r'order\s*#?(\w+)',  # order #123 or order 123
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def extract_transaction_id_node(state: State) -> Dict[str, Any]:
   """Extract transaction ID from message and add to state"""
   if state.get("transaction_id"):
       return {}  # Already have ID
   
   message = state.get("user_current_message", "")
   transaction_id = extract_transaction_id(message)
   
   if transaction_id:
       return {"transaction_id": transaction_id}
   return {}

def fetch_transaction_details(transaction_id: str, df: pd.DataFrame) -> dict:
    tx_row = df[df["Transaction_ID"] == transaction_id]

    if tx_row.empty: 
        return {}
    
    row = tx_row.iloc[0]
    return {
        "transaction_id": row["Transaction_ID"],
        "amount": float(row["Amount"]),
        "status": row["Status"],
        "date": row["Timestamp"],
    }

def fetch_transaction_node(state: State) -> Dict[str, Any]:  # Fix return type
    transaction_id = state.get("transaction_id")
    if not transaction_id:
        return {"transaction_details": {}}  # Return dict, don't mutate state

    transaction_details = fetch_transaction_details(transaction_id, df)
    return {"transaction_details": transaction_details}  # Return updates
