### State

from typing_extensions import TypedDict
from typing import List
from langgraph.graph import END, StateGraph
from .researchers import research_info_search_rag, research_info_search_web
from .routers import route_to_research_rag, route_to_research_web, route_to_rewrite
from .othernodes import state_printer, final_output_response, categorize_question
from .writers import draft_response_writer, analyze_draft_response, rewrite_response, no_rewrite



class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        initial_question: question
        question_category: question category
        draft_question: LLM generation
        final_question: LLM generation
        research_info: list of documents
        info_needed: whether to add search info
        num_steps: number of steps
    """
    initial_question : str
    question_category: str
    draft_response : str
    final_response : str
    final_answer : str
    research_info_rag : List[str] # this will now be the RAG results
    research_info_web : List[str] # this will now be the web results
    info_needed : bool
    #num_steps : int
    draft_question_feedback : dict
    rag_questions : List[str]


workflow = StateGraph(GraphState)

# Define the nodes

workflow.add_node("categorize_question", categorize_question)
workflow.add_node("research_info_search_rag", research_info_search_rag) # rag search
workflow.add_node("research_info_search_web", research_info_search_web) # web search
workflow.add_node("state_printer", state_printer)
workflow.add_node("draft_response_writer", draft_response_writer)
workflow.add_node("analyze_draft_response", analyze_draft_response)
workflow.add_node("rewrite_response", rewrite_response)
workflow.add_node("no_rewrite", no_rewrite)
workflow.add_node("final_output_response", final_output_response)

workflow.set_entry_point("categorize_question")

workflow.add_conditional_edges(
    "categorize_question",
    route_to_research_rag,
    {
        "research_info": "research_info_search_rag",
        "draft_response": "draft_response_writer",
    },
)

workflow.add_conditional_edges(
    "research_info_search_rag",
    route_to_research_web,
    {
        "research_info_web": "research_info_search_web",
        "draft_response": "draft_response_writer",
    },
)
workflow.add_edge("research_info_search_rag", "draft_response_writer")
workflow.add_edge("research_info_search_web", "draft_response_writer")



workflow.add_conditional_edges(
    "draft_response_writer",
    route_to_rewrite,
    {
        "rewrite": "analyze_draft_response",
        "no_rewrite": "no_rewrite",
    },
)
workflow.add_edge("analyze_draft_response", "rewrite_response")
workflow.add_edge("no_rewrite", "final_output_response")
workflow.add_edge("rewrite_response", "final_output_response")
workflow.add_edge("final_output_response", "state_printer")
workflow.add_edge("state_printer", END)

# Compile
app = workflow.compile()
