from typing import Annotated, Literal, TypedDict, Optional, Dict, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class manager_state(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_current_message: str
    message_history: str

    query_engine_result: Optional[Dict[str, Any]]
    refund_classification: Optional[Literal["REFUNDABLE", "NON-REFUNDABLE"]]
    classification_reason: str