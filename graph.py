from langgraph.graph import StateGraph, START, END
from core.state import State
from nodes.classification import classify_refundability, classify_intent
from nodes.evaluation import evaluate_refund_eligibility
from nodes.transactions import fetch_transaction_node, extract_transaction_id_node
from nodes.conversation import detect_unclear_request, generate_clarification_questions, process_clarification_response
from utils.routers import route_by_classification, route_by_intent, route_to_reply, route_by_clarity, route_after_clarification_check
from nodes.reply import give_user_reply
from query_engine import query_engine


graph_builder = StateGraph(State)

graph_builder.add_node("classify_refundability", classify_refundability)
graph_builder.add_node("classify_intent", classify_intent)
graph_builder.add_node("extract_transaction_id", extract_transaction_id_node)
graph_builder.add_node("evaluate_refund_eligibility", evaluate_refund_eligibility)
graph_builder.add_node("fetch_transaction_details", fetch_transaction_node)
graph_builder.add_node("give_user_reply", lambda state: give_user_reply(state, query_engine))
#conversation management nodes
graph_builder.add_node("detect_clarity", lambda state: detect_unclear_request(state, query_engine))
graph_builder.add_node("ask_questions", lambda state: generate_clarification_questions(state, query_engine))
graph_builder.add_node("process_answers", lambda state: process_clarification_response(state, query_engine))


graph_builder.add_edge(START, "detect_clarity")
graph_builder.add_conditional_edges("detect_clarity", route_after_clarification_check)
graph_builder.add_edge("ask_questions", END)
graph_builder.add_conditional_edges("process_answers", route_by_clarity)
graph_builder.add_conditional_edges("classify_refundability", route_by_classification)
graph_builder.add_conditional_edges("classify_intent", route_by_intent)
graph_builder.add_edge("extract_transaction_id", "fetch_transaction_details")
graph_builder.add_edge("fetch_transaction_details", "evaluate_refund_eligibility")
graph_builder.add_conditional_edges("evaluate_refund_eligibility", route_to_reply)
graph_builder.add_edge("give_user_reply", END)


graph = graph_builder.compile()