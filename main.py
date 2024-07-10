import streamlit as st
from rag.rag_app import app


st.title("Study Buddy")

if "messages" not in st.session_state.keys():
  st.session_state.messages=[{"role":"assistant", "content":"How may I assist you today?"}]

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.write(message["content"])

def clear_chat_history():
  st.session_state.messages=[{"role":"assistant","content":"How may I asssist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

if prompt := st.chat_input(placeholder="Type question here"):
  st.session_state.messages.append({"role":"user", "content":prompt})
  with st.chat_message("user"):
    st.write(prompt)

if st.session_state.messages[-1]["role"] != "assistant":
  with st.chat_message("assistant"):
    try:
      with st.spinner("Thinking.."):
        #time.sleep(4)
        inputs = {"initial_question": prompt, "num_steps": 0}
        output = {}

        for step_output in app.stream(inputs):
          output.update(step_output)


        final_email = output.get("final_output_response", "No response generated")
        response = final_email["final_answer"]
        st.write(response)
        placeholder = st.empty()
        full_response=''
        for item in response:
          full_response+=item
          placeholder.markdown(full_response)
        placeholder.markdown(full_response)
    except Exception as e:
                st.error("Error has occured", icon="⛔️")
                error_message = f"Error occurred: {str(e)}"

                # Write the error message to a file
                with open('error_log.txt', 'a') as f:
                    f.write(error_message + '\n')
                #logger.error(f"Error processing prompt: {e}")
  message = {"role":"assistant","content":full_response}
  st.session_state.messages.append(message)