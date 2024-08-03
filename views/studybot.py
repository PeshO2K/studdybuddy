import streamlit as st
import time
import uuid
from rag.rag_app import app

#-----fetch user sessions----#
user_sessions={}
default_session={} # new session with default message

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
            

# update session_history
def update_history():
   print("--uodating history--")
   if st.session_state.active_session == 'new-chat':
      #st.success("New chat!!!!")
      new_sess_id = str(uuid.uuid4())
      new_session = {}
      new_session[new_sess_id] = {
          "session_title": f"New Chat {new_sess_id[:8]}",
          "session_messages": st.session_state.messages
      }
      st.session_state.sessions_history = {
          **default_session, ** new_session, **user_sessions}
      st.session_state.pickname = new_sess_id
      st.session_state.new_chat_flag = False
      return new_sess_id


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
    inputs = {"initial_question": prompt_input}

    outputs = {"final_output_response": {
        "final_answer": "The ai has responded"}}
    for step_output in app.stream(inputs):
       outputs.update(step_output)

    final_output_response = outputs.get(
        "final_output_response", {"final_answer": "No response generated"})
    response = final_output_response["final_answer"]
    return response




prompt = st.chat_input("Type question here:", key="user_input")

begin = st.sidebar.container()
if "new_chat_flag" not in st.session_state:
    st.session_state.new_chat_flag = True

if "pickname" not in st.session_state:
    st.session_state.pickname = 'new-chat'

if "user_input" in st.session_state:
    st.session_state.new_chat_flag = False if st.session_state.user_input else True


if st.sidebar.button('New Chat'):
    st.session_state.pickname = "new-chat"
    st.session_state.new_chat_flag = True
    

if "messages" in st.session_state and not st.session_state.new_chat_flag :
   print_messages()


# Main chat interface
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="assets/face_5_50dp_blackNYellow.svg"):
      st.markdown(prompt)
      print(prompt)

    with st.spinner("Thinking..."):

        llm_answer = generate_response(prompt)

        with st.chat_message("assistant", avatar="assets/robot_2_50dp_purple.svg"):
            st.write_stream(stream_output(llm_answer))
            print(stream_output(llm_answer))

    st.session_state.messages.append(
        {"role": "assistant", "content": llm_answer})
    update_history()


begin.selectbox("Chat History", st.session_state.sessions_history.keys(),key='pickname',
                format_func=lambda sid: st.session_state.sessions_history[sid]["session_title"],
                placeholder='Visit Previous Chat...',
                )

st.session_state.messages = st.session_state.sessions_history[st.session_state.pickname]["session_messages"]
st.session_state.active_session=st.session_state.pickname

if "messages" in st.session_state and st.session_state.active_session == 'new-chat':
   st.session_state.new_chat_flag = False # Reset to enable printing of stored msgs
   print_messages()










      
