from typing import Annotated, Literal, TypedDict, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_current_message: str
    classification: Literal["refundable", "non_refundable"]
    intent: Optional[
        Literal[
            "failed_transaction",
            "duplicate_transaction",
        ]
    ]
    resolved: bool
    notes: str  #history of the conversation
    transaction_id: Optional[str]
    transaction_details: Optional[dict]
    refund_amount: Optional[float]
    refund_status: Optional[Literal["approved", "denied", "escalated"]]
    final_response: str
    current_step: Optional[str]
    awaiting_clarification: bool          # "Am I waiting for the user to answer my question?"
    clarification_count: int              # "How many times have I asked for clarification?"
    original_request: str                 # "What did the user first ask for?"
    conversation_context: str             # "Summary of what we've discussed so far"
    has_sufficient_info: bool

    