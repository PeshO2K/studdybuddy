from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder #Added this 7/10
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from .models import GROQ_LLM, retriever
from langchain_core.runnables import RunnablePassthrough

# ##***************************
# # GENERATE SUMMARY


# def summarise_chat(chat_messages: list, summary: str = None):
#   if summary is None:
#     summary_prompt = """Create a summary of the chat """
#   else:
#     summary_prompt = f"""This is summary of the conversation to date: {summary}\n\n
#     Ensure information from the previous summary in properly featured in the new summary. Extend the summary by taking into account these new messages:"""

#   summarise_history_prompt = ChatPromptTemplate.from_messages(
#       [
#           ("system", """You are a master at generating chat summaries with no preamble or exaplanation. Do not answer questions nor provide explanation. 
#           Strictly provide a succinct summary of the chat. Enusre all the important entitites are captured"""),
#           MessagesPlaceholder("chat_history"),
#           ("user", summary_prompt)
#       ]
#   )
#   summarise_history_chain = summarise_history_prompt | GROQ_LLM | StrOutputParser()
#   response = summarise_history_chain.invoke({"chat_history": chat_messages})
#   return response


# # GENERATE TITLE
# # gen_title_prompt = PromptTemplate(
# #     template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
# #     You are a master at summarising chat data and generating the most suitable title for the chat.


# #      <|eot_id|><|start_header_id|>user<|end_header_id|>
# #     Generate the most suitable title for the chat in a maximum of five words.


# #             Output the title only without preamble or explanation  \
# #             eg:
# #             'Nginx Configuration ' \

# #     CHAT:\n\n {chat} \n\n
# #     <|eot_id|>
# #     <|start_header_id|>assistant<|end_header_id|>
# #     """,
# #     input_variables=["chat"],
# # )


# def generate_title(chat_summary: str):
#     gen_title_prompt = PromptTemplate(
#         template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
#     You are a master at generating the most suitable title for a chat summary


#      <|eot_id|><|start_header_id|>user<|end_header_id|>
#     Generate the most suitable title for the summary in a maximum of five words.


#             Output the title only without preamble or explanation  \
#             eg:
#             'Nginx Configuration ' \

#     SUMMARY:\n\n {summary} \n\n
#     <|eot_id|>
#     <|start_header_id|>assistant<|end_header_id|>
#     """,
#         input_variables=["summary"],
#     )

#     title_generator = gen_title_prompt | GROQ_LLM | StrOutputParser()

#     return title_generator.invoke(chat_summary)


# # CONTEXTUALISE QUESTION : Added this 7/10
# # contextualize_q_system_prompt = (
# #     "Given a chat history and the latest user question "
# #     "which might reference context in the chat history, "
# #     "formulate a standalone question which can be understood "
# #     "without the chat history. Do NOT answer the question, "
# #     "just reformulate it if needed and otherwise return it as is.no preamble no explanation"
# # )
# # contextualize_q_prompt = ChatPromptTemplate.from_messages(
# #     [
# #         ("system", contextualize_q_system_prompt),
# #         MessagesPlaceholder("chat_history"),
# #         ("human", "{input}"),
# #     ]
# # )
# contextualize_q_prompt = PromptTemplate(
#     template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
#     You are a master at generating standalone contextualised questions which might reference context in the  
#      summary of previous chats 


#      <|eot_id|><|start_header_id|>user<|end_header_id|>
#     Given the latest user question, formulate a standalone question which can be understood
#     without the chat history.The formulated question must capture context from the summary if any. Do NOT answer the question, just reformulate it if needed and 
#     otherwise return it as is.no preamble no explanation


#             Output the question only without preamble or explanation  \
#             eg given the scenario below:
#             'summary: User asked for the sum of 2 and 4 \
#             question: what is their product?' \
#             the output will be: 'what is the product of 2 and 4'
            

#     QUESTION:\n\n {input} \n\n
#     SUMMARY:\n\n {chat_history} \n\n
#     <|eot_id|>
#     <|start_header_id|>assistant<|end_header_id|>
#     """,
#     input_variables=["input", "chat_history"],
# )
# contextualize_qn_chain = contextualize_q_prompt | GROQ_LLM | StrOutputParser()

# ##***************************
# GENERATE SUMMARY
def summarise_chat(chat_messages: list, summary: str = None):
  if summary is None:
    summary_prompt = """Create a summary of the chat """
  else:
    summary_prompt = f"""This is summary of the conversation to date: {summary}\n\n
    Extend the summary by taking into account these new messages:"""

  summarise_history_prompt = ChatPromptTemplate.from_messages(
      [
          ("system", "You are a master at generating chat summaries with no preamble or exaplanation. Do not answer questions nor provide explanation. Strictly provide a succinct summary of the chat"),
          MessagesPlaceholder("chat_history"),
          ("user", summary_prompt)
      ]
  )
  summarise_history_chain = summarise_history_prompt | GROQ_LLM | StrOutputParser()
  response = summarise_history_chain.invoke({"chat_history": chat_messages})
  return response





# GENERATE TITLE
# gen_title_prompt = PromptTemplate(
#     template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
#     You are a master at summarising chat data and generating the most suitable title for the chat.
    

#      <|eot_id|><|start_header_id|>user<|end_header_id|>
#     Generate the most suitable title for the chat in a maximum of five words.


#             Output the title only without preamble or explanation  \
#             eg:
#             'Nginx Configuration ' \

#     CHAT:\n\n {chat} \n\n
#     <|eot_id|>
#     <|start_header_id|>assistant<|end_header_id|>
#     """,
#     input_variables=["chat"],
# )


def generate_title(chat_summary:str):
    gen_title_prompt = PromptTemplate(
        template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a master at generating the most suitable title for a chat summary


     <|eot_id|><|start_header_id|>user<|end_header_id|>
    Generate the most suitable title for the summary in a maximum of five words.


            Output the title only without preamble or explanation  \
            eg:
            'Nginx Configuration ' \

    SUMMARY:\n\n {summary} \n\n
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """,
        input_variables=["summary"],
    )


    title_generator = gen_title_prompt | GROQ_LLM | StrOutputParser()

    return title_generator.invoke(chat_summary)


# CONTEXTUALISE QUESTION : Added this 7/10
# contextualize_q_system_prompt = (
#     "Given a chat history and the latest user question "
#     "which might reference context in the chat history, "
#     "formulate a standalone question which can be understood "
#     "without the chat history. Do NOT answer the question, "
#     "just reformulate it if needed and otherwise return it as is.no preamble no explanation"
# )
# contextualize_q_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", contextualize_q_system_prompt),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ]
# )
contextualize_q_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a master at generating standalone contextualised questions which might reference context in the  
     summary of previous chats 


     <|eot_id|><|start_header_id|>user<|end_header_id|>
    Given the latest user question, formulate a standalone question which can be understood
    without the chat history. Do NOT answer the question, just reformulate it if needed and 
    otherwise return it as is.no preamble no explanation


            Output the title only without preamble or explanation  \
            eg:
            'Nginx Configuration ' \

    QUESTION:\n\n {input} \n\n
    SUMMARY:\n\n {chat_history} \n\n
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["input", "chat_history"],
)
contextualize_qn_chain = contextualize_q_prompt | GROQ_LLM | StrOutputParser()

#CATEGORIZE QUESTION
prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are the Question Categorizer Agent for the ALX Software Engineering Course,You are a master at \
    understanding what a student wants when they ask a question and are able to categorize \
    it in a useful way.  \

     <|eot_id|><|start_header_id|>user<|end_header_id|>
    Conduct a comprehensive analysis of the quesion provided and categorize it into one of the following categories:
        course_enquiry - used when someone is asking for information about the course and other things like the code of conduct etc \

        programming_enquiry - used when someone is asking for information about a programming language, feature, tool or service but not about the course \\

        off_topic when it doesnt relate to any other category \


            Output a single category only without preamble or explanation from the types ('course_enquiry', 'programming_enquiry', 'off_topic') \
            eg:
            'course_enquiry' \

    QUESTION:\n\n {initial_question} \n\n
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["initial_question"],
)

question_category_generator = prompt | GROQ_LLM | StrOutputParser()


#RAG
## ROUTE QUESTION TO RAG
rag_router_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an expert at reading the initial question and routing to our internal\
     knowledge system at ALX Software Engineering Course\
     or directly to a draft response. \n

    Use the following criteria to decide how to route the question: \n\n

    If the initial question only requires a simple response
    Just choose 'draft_response'  for questions you can easily answer, prompt engineering, and adversarial attacks.


    If you are unsure or the person is asking a question you don't understand then choose 'research_info'.
    Additonally, If question category is course_enquiry then choose 'research_info'.

    You do not need to be stringent with the keywords in the question related to these topics. Otherwise, use research-info.
    Give a binary choice 'research_info' or 'draft_response' based on the question. Return a JSON with a single key 'router_decision' and
    no premable or explaination. use both the initial question and question category to make your decision.
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Question to route INITIAL_QUESTION : {initial_question} \n
    QUESTION_CATEGORY : {question_category} \n

    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["initial_question", "question_category"],
)

rag_router = rag_router_prompt | GROQ_LLM | JsonOutputParser()

## RAG QUESTIONS
search_rag_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a master at working out the best questions to ask our knowledge agent \
    to get the best info for the student at ALX Software Engineering Course.

    given the INITIAL_QUESTION and QUESTION_CATEGORY. Work out the best questions that will find the best \
    info for helping to write the final response.  Write the questions to our knowledge system not to the student.

    Return a JSON with a single key 'questions' with no more than 3 strings of questions and no premable or explaination.

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    INITIAL_QUESTION: {initial_question} \n
    QUESTION_CATEGORY : {question_category} \n

    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["initial_question", "question_category"],
)

question_rag_chain = search_rag_prompt | GROQ_LLM | JsonOutputParser()


## ANSWER QUESTIONS FROM RAG
rag_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an assistant for question-answering tasks at ALX Software Engineering Course. Use the following pieces of \
    retrieved context to answer the question exhaustively.\
    Provide all available relavant information in the answer. \
    List relevant links o additional resources if they are available. \
      keep the answer concise. Additionanly, list the document sources below the answer. \
      List the document names only not the entire path. The document sources should only be listed if the anser is known. If you dont know the answer,Do not list the document sourcs at all.\
      If you don't know the answer strictly do not list the document sources and say respond with (research_info_web) only  with no preamble nor explanation.\n

     <|eot_id|><|start_header_id|>user<|end_header_id|>
    QUESTION: {question} \n
    CONTEXT: {context} \n
    Answer:

    Output 'research_info_web' as the answer If you don't know the answer with no premable nor explanation
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>


    """,
    input_variables=["question","context"],
)

rag_chain = (
    {"context": retriever , "question": RunnablePassthrough()}
    | rag_prompt
    | GROQ_LLM
    | StrOutputParser()
)

# WEB SEARCH
## ROUTE QUESTION TO WEB SEARCH TOOL
web_research_router_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an expert at analysing the response to an question from  our\
     internal knowledge system and routing to a web search\
     or directly to a draft response. \n

    Use the following criteria to decide how to route the response: \n\n

    If the response is 'research_info_web' the choose research_info_web. otherwise just choose 'draft_response'



    Give a binary choice 'research_info_web' or 'draft_response' based on the response. Return a JSON with a single key 'router_decision' and
    no premable or explaination. use the initial question , question category and the rag agent response  to make your decision
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Email to route INITIAL_QUESTION : {initial_question} \n
    QUESTION_CATEGORY : {question_category} \n
    RAG_AGENT_RESPONSE: {rag_agent_response} \n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["initial_question","question_category","rag_agent_response"],
)

web_research_router = web_research_router_prompt | GROQ_LLM | JsonOutputParser()

## GENERATE KEYWORDS
search_keyword_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a master at extracting questions that require a web search to find \
    the answers and working out the best keywords from a RAG agent response to \
    search for in a web search to get the best info for the student at ALX Software Engineering Course.

    given the INITIAL_ QUESTION, QUESTION_CATEGORY and RAG_AGENT_RESPONSE. The RAG_AGENT_RESPONSE \
    is a list of questions and answers separated by new lines. Strictly from the\
     RAG_AGENT_RESPONSE Work out the best keywords from the questions whose answer \
     is 'research_info_web' only that will find the best nfo for helping to write the final response.

    Return a JSON with a two keys 'questions' with the questions from the list whose\
     answers are 'research_info_web' from the RAG_AGENT_RESPONSE, 'keywords' with no\
      more than 3 keywords and no premable or explaination.

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    INITIAL_ QUESTION: {initial_question} \n
    QUESTION_CATEGORY : {question_category} \n
    RAG_AGENT_RESPONSE: {rag_agent_response} \n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["initial_question","question_category","rag_agent_response"],
)

search_keyword_chain = search_keyword_prompt | GROQ_LLM | JsonOutputParser()

# RESPONSE GENERATION
## DRAFT RESPONSE
draft_writer_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are the Response Writer Agent for the ALX Software Engineering Course, take the INITIAL_QUESTION below \
    from a human, the question_category \
    that the categorizer agent gave it and the research from the research agent and \
    write a helpful response in a  friendly and accurate way. State the answer directly. No salutations, no preamble e.g. "Hi" or "You are interested in"

            You never make up information that hasn't been provided by the research_info or in the initial_question.


            Return the response a JSON with a single key 'response_draft' and no premable or explaination.
            The Json should be  valid even if it contains a coding example. MAKE SURE THE JSON IS VALID JSON.
            Escape newline characters and double quotes

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    INITIAL_QUESTION: {initial_question} \n
    QUESTION_CATEGORY : {question_category} \n
    RESEARCH_INFO: {research_info_rag} + {research_info_web} \n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["initial_question","question_category","research_info_web","research_info_rag"],
)

draft_writer_chain = draft_writer_prompt | GROQ_LLM | JsonOutputParser()


## ANALYSE RESPONSE
draft_analysis_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are the Quality Control Agent at ALX Software Engineering Course read the INITIAL_QUESTION below  from a human,\
     the question_category that the categorizer agent gave it and the \
    research from the research agent and write an analysis of how the response.

    Check if the DRAFT_RESPONSE addresses the student's issues based on the question category and  \
    content of the initial question.\n

    Give feedback of how the response can be improved and what specific things can be added or change\
    to make the response more effective at addressing the student's issues.

    You never make up or add information that hasn't been provided by the research_info or in the initial_question.

    Return the analysis as a VALID JSON with a single key 'draft_analysis' and no premable or explaination.
    The Json should be  valid even if it contains a coding example. MAKE SURE THE JSON IS VALID JSON.
            Escape newline characters and double quotes

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    INITIAL_QUESTION: {initial_question} \n\n
    QUESTION_CATEGORY : {question_category} \n\n
    RESEARCH_INFO: {research_info} \n\n
    DRAFT_RESPONSE: {draft_response} \n\n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["initial_question","question_category","draft_response","research_info"],
)

draft_analysis_chain = draft_analysis_prompt | GROQ_LLM | JsonOutputParser()


## ROUTE TO REWRITE
rewrite_router_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an expert at evaluating the responses that are draft responses for the student\
     at ALX Software Engineering Course and deciding if they
    need to be rewritten to be better. \n

    Use the following criteria to decide if the DRAFT_RESPONSE needs to be rewritten: \n\n

    If the INITIAL_QUESTION only requires a simple response which the DRAFT_RESPONSE contains then it doesn't need to be rewritten.
    If the DRAFT_RESPONSE addresses all the concerns of the INITIAL_QUESTION then it doesn't need to be rewritten.
    If the DRAFT_RESPONSE is missing information that the INITIAL_QUESTION requires then it needs to be rewritten.

    Give a binary choice 'rewrite' (for needs to be rewritten) or 'no_rewrite' (for doesn't need to be rewritten) based on the DRAFT_RESPONSE and the criteria.
    Return a JSON with a single key 'router_decision' and no premable or explaination. \
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    INITIAL_QUESTION: {initial_question} \n
    QUESTION_CATEGORY : {question_category} \n
    DRAFT_RESPONSE: {draft_response} \n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["initial_question","question_category","draft_response"],
)

rewrite_router = rewrite_router_prompt | GROQ_LLM | JsonOutputParser()

## REWRITE RESPONSE
rewrite_response_prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are the Final Response Agent at ALX Software Engineering Course read \
    the response analysis below from the QC Agent \
    and use it to rewrite and improve the draft_response to create a final response.


    You never make up or add information that hasn't been provided by the research_info or in the initial_question.

    Return the final response as a VALID JSON with a single key 'final_response' which is a string and no premable or explaination.
    The Json should be  valid even if it contains a coding example. MAKE SURE THE JSON IS VALID JSON.
            Escape newline characters and double quotes

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    INITIAL_QUESTION:{initial_question}\n\n
    QUESTION_CATEGORY : {question_category} \n\n
    RESEARCH_INFO: {research_info} \n\n
    DRAFT_RESPONSE: {draft_response} \n\n
    DRAFT_RESPONSE_FEEDBACK: {response_analysis} \n\n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["initial_question",
                     "question_category",
                     "research_info",
                     "response_analysis",
                     "draft_response",
                     ],
)

rewrite_chain = rewrite_response_prompt | GROQ_LLM | JsonOutputParser()
