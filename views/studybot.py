import streamlit as st
#from rag.rag_app import app

st.title("Study Buddy")

# Initialize chat history if not present
if "messages" not in st.session_state:
    print("Initializing session state for messages...")
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}]

# Display chat messages
print("Displaying chat messages...")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to clear chat history


def clear_chat_history():
    print("Clearing chat history...")
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}]


# Clear chat history button
if st.sidebar.button('Clear Chat History', on_click=clear_chat_history):
    print("Chat history cleared!")

# Function to generate response


def generate_response(prompt_input):
    print(f"Generating response for: {prompt_input}")
    inputs = {"initial_question": prompt_input}
    outputs = {}  # Initialize outputs dictionary
    # Assuming 'app.stream' is properly defined and returns step outputs
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
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.spinner("Thinking..."):
        llm_answer = generate_response(prompt)
        with st.chat_message("assistant"):
          st.markdown(llm_answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": llm_answer})
