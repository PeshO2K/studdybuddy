import streamlit as st
import time
from streamlit_chat import message
from rag.rag_app import app

#-----fetch user sessions----#
sessions={}

st.title("Study Buddy")


if "sessions_history" not in st.session_state:
   st.session_state.sessions_history = sessions

if "messages" not in st.session_state:
    print("Initializing session state for messages...")
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}]
session_id_to_index = {sid: idx for idx, sid in enumerate(
    st.session_state.sessions_history.keys())}

begin = st.sidebar.container()
if st.sidebar.button('New Chat'):
    st.session_state.pickname = "new-chat"

begin.selectbox("Chat History", st.session_state.sessions_history.keys(),key='pickname',
                format_func=lambda sid: st.session_state.sessions_history[sid]["session_title"],
                placeholder='Visit Previous Chat...',
                )
st.session_state.messages = st.session_state.sessions_history[st.session_state.pickname]["session_messages"]
st.session_state.active_session=st.session_state.pickname

# Display chat messages
for message in st.session_state.messages:
    avatar_link = "assets/face_5_50dp_blackNYellow.svg" if message[
        "role"] == "user" else "assets/robot_2_50dp_purple.svg"
    with st.chat_message(message["role"], avatar=avatar_link):
        st.write(message["content"])

if st.sidebar.button('In bot'):
    st.session_state.pickname = "new-chat"


# Function to stream response
def stream_output(stream_object):
  stream_objects = stream_object.split(" ")
  for chunk in stream_objects:
    # print(chunk)
    yield chunk + " "
    time.sleep(0.02)

# Function to generate response
def generate_response(prompt_input):
    print(f"Generating response for: {prompt_input}")
    inputs = {"initial_question": prompt_input}

    outputs = {}
    for step_output in app.stream(inputs):
       outputs.update(step_output)

    final_output_response = outputs.get(
        "final_output_response", {"final_answer": "No response generated"})
    response = final_output_response["final_answer"]
    return response



# Main chat interface
prompt = st.chat_input("Type question here:", key="user_input")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="assets/face_5_50dp_blackNYellow.svg"):
      st.markdown(prompt)

    with st.spinner("Thinking..."):
        
        llm_answer = generate_response(prompt)
        
        with st.chat_message("assistant", avatar="assets/robot_2_50dp_purple.svg"):
            st.write_stream(stream_output(llm_answer))


    st.session_state.messages.append(
        {"role": "assistant", "content": llm_answer})
  