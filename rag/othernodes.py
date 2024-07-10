from utils.file_operations import write_markdown_file
from agents import question_category_generator



def categorize_question(state):
    """take the initial question and categorize it"""
    print("---CATEGORIZING INITIAL question---")
    print("---------State keys:", state.keys())
    initial_question = state['initial_question']
    num_steps = int(state['num_steps'])
    num_steps += 1

    question_category = question_category_generator.invoke({"initial_question": initial_question})
    print(question_category)
    # save to local disk
    write_markdown_file(question_category, "question_category")

    return {"question_category": question_category, "num_steps":num_steps}


def final_output_response(state):
  return{"final_answer":state["final_response"]}

def state_printer(state):
    """print the state"""
    print("---STATE PRINTER---")
    print(f"Initial question: {state['initial_question']} \n" )
    print(f"Question category: {state['question_category']} \n" )
    print(f"Draft question: {state['draft_response']} \n" )
    print(f"Final question: {state['final_response']} \n" )
    print(f"Research Info RAG: {state['research_info_rag']} \n")
    print(f"Research Info WEB: {state['research_info_web']} \n")
    print(f"RAG Questions: {state['rag_questions']} \n")
    print(f"Num Steps: {state['num_steps']} \n")
    return


