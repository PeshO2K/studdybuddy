from agents import search_keyword_chain, question_rag_chain, rag_chain
from utils.file_operations import write_markdown_file
from tools.search import web_search_tool
from langchain.schema import Document


def research_info_search_rag(state):

    print("---RESEARCH INFO  IN RAG---")
    # print("---------State keys:", state.keys())
    initial_question = state["initial_question"]
    question_category = state["question_category"]
    ''' num_steps = int(state['num_steps'])
    num_steps += 1 '''

    # RAG search
    rag_questions = question_rag_chain.invoke(
        {"initial_question": initial_question, "question_category": question_category})
    rag_questions = rag_questions['questions']
    print("****The questions from the rag:  ", rag_questions)
    rag_results = []
    for question in rag_questions:
        # print(question)
        temp_docs = rag_chain.invoke(question)
        # print(temp_docs)
        question_results = question + '\n\n' + temp_docs + "\n\n\n"
        if rag_results is not None:
            rag_results.append(question_results)
        else:
            rag_results = [question_results]
    # print(rag_results)
    # print(type(rag_results))
    write_markdown_file(rag_results, "research_info_rag")
    write_markdown_file(rag_questions, "rag_questions")
    print("---DONE SEARCHING RAG---\n\n")
    return {"research_info_rag": rag_results, "rag_questions": rag_questions}


def research_info_search_web(state):

    print("---RESEARCH INFO: SEARCHING WEB---")
    initial_question = state["initial_question"]
    question_category = state["question_category"]
    # information from rag to research
    rag_agent_response = state["research_info_rag"]
    ''' num_steps = int(state['num_steps'])
    num_steps += 1 '''

    # Web search
    # ammend code to only search for question labeled research_info_web. return results
    keywords = search_keyword_chain.invoke({"initial_question": initial_question,
                                            "question_category": question_category,
                                            "rag_agent_response": rag_agent_response})
    # print("-----Questions: ",keywords['questions'])
    keywords = keywords['keywords']
    # print("-----Keywords",keywords)
    # print("-----Truncated Keywords",keywords[:1])

    full_searches = []
    for keyword in keywords[:1]:
        # print(keyword)
        temp_docs = web_search_tool.invoke({"query": keyword})
        if all(isinstance(item, str) for item in temp_docs):
          web_results = "\n".join(temp_docs)  # Join strings directly
        else:
          # Extract 'content' if available, otherwise use empty string
          web_results = "\n".join([d.get("content", "") for d in temp_docs])

        # web_results = "\n".join([d["content"] for d in temp_docs])
        web_results = Document(page_content=web_results)
        if full_searches is not None:
            full_searches.append(web_results)
        else:
            full_searches = [web_results]
   # print("*****Fullsearch in web researcher>>>>>",full_searches)
    # print(type(full_searches))
    print("---DONE SEARCHING WEB---\n\n")
    # write_markdown_file(full_searches, "research_info")
    return {"research_info_web": full_searches}
