from rag.agents import rag_router, web_research_router, rewrite_router


def route_to_research_rag(state):
    """
    Route question to web search or not.
    Args:
        state (dict): The current graph state
    Returns:
        str: Next node to call
    """

    print("---ROUTE TO RESEARCH---")
    initial_question = state["initial_question"]
    question_category = state["question_category"]

    router = rag_router.invoke(
        {"initial_question": initial_question, "question_category": question_category})
    # print(router)
    # print(type(router))
    print("*** Decision: ", router['router_decision'])
    if router['router_decision'] == 'research_info':
        print("***ROUTE question TO RESEARCH INFO***\n\n")
        return "research_info"
    elif router['router_decision'] == 'draft_response':
        print("***ROUTE question TO DRAFT response***\n\n")
        return "draft_response"


def route_to_research_web(state):
    """
    Route question to web search or not.
    Args:
        state (dict): The current graph state
    Returns:
        str: Next node to call
    """

    print("---ROUTE TO RESEARCH WEB OR DRAFT RESPONSE---")
    initial_question = state["initial_question"]
    question_category = state["question_category"]

    research_info_rag = state["research_info_rag"]
    # print("----> State Keys:", state.keys())
    # research_info_web = state["research_info_web"]

    router = web_research_router.invoke(
        {"initial_question": initial_question, "question_category": question_category, "rag_agent_response": research_info_rag})
    # print(router)
    # print(type(router))
    print("****Decision:  ", router['router_decision'])
    if router['router_decision'] == 'research_info_web':
        print("---ROUTE question TO RESEARCH INFO---\n\n")
        return "research_info_web"
    elif router['router_decision'] == 'draft_response':
        print("---ROUTE question TO DRAFT RESPONSE---\n\n")
        return "draft_response"


def route_to_rewrite(state):
    """Function to choose if the response 
    should be rewritten or not
    """

    print("---ROUTE TO REWRITE---")
    initial_question = state["initial_question"]
    question_category = state["question_category"]

    draft_response = state["draft_response"]
    router = rewrite_router.invoke({"initial_question": initial_question,
                                    "question_category": question_category,
                                    "draft_response": draft_response}
                                   )
    # print(router)
    print("***Decison: ", router['router_decision'])
    if router['router_decision'] == 'rewrite':
        print("---ROUTE TO ANALYSIS - REWRITE---\n\n")
        return "rewrite"
    elif router['router_decision'] == 'no_rewrite':
        print("---ROUTE RESPONSE TO FINAL RESPONSE---\n\n")
        return "no_rewrite"
