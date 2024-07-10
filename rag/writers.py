from utils.file_operations import write_markdown_file
from agents import draft_writer_chain, draft_analysis_chain, rewrite_chain 


def draft_response_writer(state):
    print("---DRAFT response WRITER---")
    ## Get the state
    initial_question = state["initial_question"]
    question_category = state["question_category"]
    research_info_rag = state["research_info_rag"]
    research_info_web = state["research_info_web"]
    num_steps = state['num_steps']
    num_steps += 1

    # Generate draft response
    draft_response = draft_writer_chain.invoke({"initial_question": initial_question,
                                     "question_category": question_category,
                                     "research_info_web": research_info_web,
                                     "research_info_rag":research_info_rag})
    print(draft_response)
    # print(type(draft_response))

    response_draft = draft_response['response_draft']
    write_markdown_file(response_draft, "draft_response")

    return {"draft_response": response_draft, "num_steps":num_steps}

def analyze_draft_response(state):
    print("---DRAFT response ANALYZER---")
    ## Get the state
    initial_question = state["initial_question"]
    question_category = state["question_category"]
    draft_response = state["draft_response"]
    research_info_rag = state.get("research_info_rag", [])
    research_info_web = state.get("research_info_web", [])
    research_info = research_info_rag + research_info_web
    num_steps = state['num_steps']
    num_steps += 1

    # Generate draft response
    draft_response_feedback = draft_analysis_chain.invoke({"initial_question": initial_question,
                                                "question_category":question_category,
                                                "research_info":research_info,
                                                "draft_response":draft_response}
                                               )
    # print(draft_response)
    # print(type(draft_response))

    write_markdown_file(str(draft_response_feedback), "draft_response_feedback")
    return {"draft_response_feedback": draft_response_feedback, "num_steps":num_steps}




def rewrite_response(state):
    print("---ReWRITE response ---")
    ## Get the state
    initial_question = state["initial_question"]
    question_category = state["question_category"]
    draft_response = state["draft_response"]
    research_info = state["research_info_rag"] + state["research_info_web"]
    draft_response_feedback = state["draft_response_feedback"]
    num_steps = state['num_steps']
    num_steps += 1

    # Generate draft response
    final_response = rewrite_chain.invoke({"initial_question": initial_question,
                                                "question_category":question_category,
                                                "research_info":research_info,
                                                "draft_response":draft_response,
                                                "response_analysis": draft_response_feedback}
                                               )

    write_markdown_file(str(final_response), "final_response")
    return {"final_response": final_response['final_response'], "num_steps":num_steps}




def no_rewrite(state):
    print("---NO REWRITE EMAIL ---")
    ## Get the state
    draft_response = state["draft_response"]
    num_steps = state['num_steps']
    num_steps += 1

    write_markdown_file(str(draft_response), "final_response")
    return {"final_response": draft_response, "num_steps":num_steps}
