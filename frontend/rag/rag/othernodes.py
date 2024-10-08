from rag.utils.file_operations import write_markdown_file
from .agents import question_category_generator, contextualize_qn_chain


def contextualise_question(state):
    """Take the initial qn and contextualise it"""
    print("\n---CONTEXTULAISING INPUT---")
    input_question = state['input']
    chat_history = state.get('chat_history', [])
    if chat_history:
      contextualised_qn = contextualize_qn_chain.invoke(
          {"input": input_question, "chat_history": chat_history})
      return {"initial_question": contextualised_qn}
    return {"initial_question": input_question}



def categorize_question(state):
    """take the initial question and categorize it"""
    print("\n---CATEGORIZING INITIAL question---")
    # print("---------State keys:", state.keys())
    initial_question = state['initial_question']
    ''' num_steps = int(state['num_steps'])
    num_steps += 1 '''

    question_category = question_category_generator.invoke(
        {"initial_question": initial_question})
    print("----The category is---: ", question_category)
    # save to local disk
    write_markdown_file(question_category, "question_category")
    print("---DONE CATEGORIZING---\n\n")

    return {"question_category": question_category}



def final_output_response(state):
  return{"final_answer":state["final_response"]}

def state_printer(state):
    """print the state"""
    print("---STATE PRINTER---")
    print(f"Initial question: {state['initial_question']} \n" )
    print(f"Question category: {state['question_category']} \n" )
    print(f"Draft question: {state['draft_response']} \n" )
    print(f"Final question: {state['final_response']} \n" )
    print(f"Final Answer: {state['final_answer']} \n" )
    print(f"Research Info RAG: {state.get('research_info_rag',[])} \n")
    print(f"Research Info WEB: {state.get('research_info_web',[])} \n")
    print(f"RAG Questions: {state.get('rag_questions', [])} \n")
    print(f"Chat_history: {state.get('chat_history', [])} \n")
    print("****************************************\n\n\n")
    return
