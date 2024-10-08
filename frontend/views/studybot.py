import streamlit as st
import time
import uuid
from rag.rag.rag_app import app
from rag.rag.agents import generate_title, summarise_chat
from utils.sessions_handler import fetch_user_sessions, fetch_session_log,save_session,create_new_session




user_sessions = fetch_user_sessions()


default_session = {
    "new-chat": {
        "title": "New Chat",
        "messages": [
            {"role": "assistant", "content": "How may I assist you today?"}
        ]
    }
}
sessions= {**default_session,**user_sessions}
# st.write(sessions)
st.title("Study Buddy")
if "render_counter" not in st.session_state:
   st.session_state.render_counter = 0

if "sessions_history" not in st.session_state:
   st.session_state.sessions_history = sessions


session_id_to_index = {sid: idx for idx, sid in enumerate(
    st.session_state.sessions_history.keys())}

# Display chat messages
def print_messages():
    for message in st.session_state.messages:
        avatar_link = "assets/face_5_50dp_blackNYellow.svg" if message[
            "role"] == "user" else "assets/robot_2_50dp_purple.svg"
        with st.chat_message(message["role"], avatar=avatar_link):
            st.write(message["content"])
            

# # update session_history
def update_history():
   print("--updating history--")
   
   if st.session_state.bot_active_session == 'new-chat':
      
      # TODO: use an llm to get an appropritate title for the chat
      temp_sess_id = str(uuid.uuid4())
      
      try:
        # get a summary of the chats and generate title
        chat_summary = summarise_chat(st.session_state.messages)
        new_title = generate_title(chat_summary)
      except Exception as e:
        new_title = f"New Chat {temp_sess_id[:8]}"
        
     
      session_details = {
          "title": new_title,
          "messages": st.session_state.messages,
          "summary":chat_summary
      }
      # create new session and get id using api
      new_sess_id = create_new_session(session_details)
      new_session = {new_sess_id:session_details}

      st.session_state.sessions_history = {
          **default_session, ** new_session, **user_sessions}
      st.session_state.pick_chat = new_sess_id
      return new_sess_id
   else:
       prev_log = user_sessions[st.session_state.bot_active_session]["messages"]
       updated_log = st.session_state.messages
       
       new_messages = updated_log[len(prev_log)-len(updated_log):]
       # add chat summariser
       old_chat_summary = st.session_state.get("summary",None)
       new_chat_summary = summarise_chat(new_messages, old_chat_summary)
       session_details = {"title":user_sessions[st.session_state.bot_active_session]["title"],"messages":new_messages, "summary":new_chat_summary}
       save_session(st.session_state.bot_active_session,session_details)



# Function to stream response
def stream_output(stream_object):
  stream_objects = stream_object.split(" ")
  for chunk in stream_objects:
    # print(chunk)
    yield chunk + " "
    time.sleep(0.08)


# Function to generate response
def generate_response(prompt_input):
    print(f"Generating response for: {prompt_input}")
    # inputs = {"initial_question": prompt_input}
    # inputs = {"input": prompt_input, "chat_history": st.session_state.messages}
    chat_summary = st.session_state.sessions_history[
        st.session_state.pick_chat].get("summary", "")
    inputs = {"input": prompt_input, "chat_history": chat_summary}

    # outputs = {"final_output_response": {
    #     "final_answer": "The ai has responded"}}
    outputs={}
    for step_output in app.stream(inputs):
       outputs.update(step_output)

    final_output_response = outputs.get(
        "final_output_response", {"final_answer": "No response generated"})
    response = final_output_response["final_answer"]

    # # Simulate error
    # raise Exception("Simulated error: Unable to generate response")
    return response




prompt = st.chat_input("Type question here:", key="user_input")

begin = st.sidebar.container()


if "pick_chat" not in st.session_state:
    st.session_state.pick_chat = 'new-chat'


if st.sidebar.button('New Chat'):
    st.session_state.pick_chat = "new-chat"
#debug:
print( "The picked session: ", st.session_state.sessions_history[
    st.session_state.pick_chat])
current_log = st.session_state.sessions_history[
    st.session_state.pick_chat]["messages"]

if st.session_state.pick_chat != 'new-chat':
    # fetch messages and update log
    # # if the current history is empty, fetch log:
    fetched_log = fetch_session_log(st.session_state.pick_chat)
    
    if len(current_log) == 0:
       st.title("Fetching from api")
       current_log = fetched_log
       st.session_state.sessions_history[
           st.session_state.pick_chat]["messages"] = current_log
    user_sessions[st.session_state.pick_chat]["messages"] = fetched_log

       
st.session_state.messages = current_log



if "messages" in st.session_state :
   print_messages()


# Main chat interface
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="assets/face_5_50dp_blackNYellow.svg"):
      st.markdown(prompt)
      print(prompt)

    with st.spinner("Thinking..."):
      # for debugging:
        llm_answer = generate_response(prompt)
        try:

            # llm_answer = generate_response(prompt)

            with st.chat_message("assistant", avatar="assets/robot_2_50dp_purple.svg"):
                st.write_stream(stream_output(llm_answer))
                print(stream_output(llm_answer))

            st.session_state.messages.append(
                {"role": "assistant", "content": llm_answer})
        except Exception as e:
            st.error(f"An error occurred: {e}")
            # st.error("An error occurred!")
            st.session_state.messages.append(
                {"role": "assistant", "content": "An error occurred while generating the response."})
    update_history()


begin.selectbox("Chat History", st.session_state.sessions_history.keys(),key='pick_chat',
                format_func=lambda sid: st.session_state.sessions_history[sid]["title"],
                placeholder='Visit Previous Chat...',
                )

st.session_state.bot_active_session=st.session_state.pick_chat
