from core.state import State
from core.models import llm


def evaluate_refund_eligibility(state: State) -> State:
    """
    Evaluate whether a refund should be approved, denied, or escalated.
    Uses intent, transaction details, and user message to guide decision.
    """
    intent = state.get("intent", "")
    transaction = state.get("transaction_details", {})
    user_message = state.get("messages", "")


    prompt = f"""
You are a banking support assistant for Banked. Your job is to evaluate refund requests based on the user's message, intent, and transaction details.

Here is Banked’s official refund policy:

---
Eligibility for Refunds:
- Refunds are available for transactions that fail due to system errors or processing failures.
- Duplicate charges identified within 48 hours are eligible for refund.
- Merchant refunds not reflected within 7 business days can be escalated for investigation.

Non-Refundable Situations:
- Transfers made to incorrect accounts due to user error are non-refundable.
- Authorized transactions completed successfully cannot be reversed.
- Refund requests submitted after 30 days from the transaction date will not be accepted.

Refund Process:
- Customers must report disputes via Banked’s customer support within 30 days.
- Refunds will be processed within 5 business days after verification.
- Refunds will be credited back to the original payment source.

Limits and Conditions:
- Refund amount per transaction is capped at $15,000.
- Banked reserves the right to reject any refund request deemed fraudulent or suspicious.
---

Use this policy to decide whether to approve, deny, or escalate a refund request.

Only respond with one of: "approved", "denied", or "escalated", followed by a brief reason.

Intent: {intent}
Transaction Details: {transaction}
User Message: {user_message}
"""
    
    response = llm.invoke(prompt).strip().lower()
    if "approved" in response:
        refund_status = "approved"
    elif "denied" in response:
        refund_status = "denied"
    else:
        refund_status = "escalated"

    # Update state
    state["refund_status"] = refund_status
    state["notes"] += f"\n[System] Refund evaluation: {response}"

    if refund_status == "approved" and "amount" in transaction:
        state["refund_amount"] = transaction["amount"]
    else:
        state["refund_amount"] = None

    return state
