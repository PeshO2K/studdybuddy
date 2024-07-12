# Study Buddy App

## Overview

The Study Buddy App is an AI-powered companion designed to assist students of the ALX Software Engineering Course by categorizing their questions, retrieving relevant information, and drafting responses. Utilizing advanced language models and retrieval techniques, the app provides accurate and timely answers tailored to user inquiries.

---

## Features

- **Question Categorization:** Automatically classifies questions into predefined categories such as course inquiries, programming inquiries, or off-topic questions.
- **Retrieval-Augmented Generation (RAG):** Combines internal knowledge with web searches to provide comprehensive answers.
- **Dynamic Drafting:** Generates initial draft responses based on categorized questions and retrieved information.
- **Quality Control:** Evaluates draft responses for completeness and accuracy, ensuring high-quality outputs.
- **Interactive Web Searching:** Performs web searches to enhance response quality when internal knowledge is insufficient.

---

## Requirements

- Python 3.x
- Google Colab or local environment
- API Keys for Groq and Hugging Face
- Necessary Python packages:
  - `langchain`
  - `streamlit`
  - `chromadb`

---

## Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-repo/study-buddy-app.git
   cd study-buddy-app
   ```

2. **Install Dependencies:**
   Ensure you have the required packages installed:
   ```bash
   pip install langchain streamlit chromadb
   ```

3. **Set Environment Variables:**
   Replace the placeholders with your actual API keys:
   ```python
   import os
   os.environ["groq_API_Key"] = 'your_groq_api_key'
   os.environ["hf_API_Key"] = 'your_huggingface_api_key'
   ```

---

## Usage

1. **Start the Application:**
   Run the Streamlit app to interact with the Study Buddy:
   ```bash
   streamlit run main_app.py
   ```

2. **Ask Questions:**
   Input your questions into the provided interface and receive categorized responses and insights.

---

## Code Overview

### Key Components

- **Categorization:**
  Uses `ChatGroq` to classify the questions based on predefined categories.

- **Research and Retrieval:**
  Implements RAG to gather additional context using `Chroma` and web search capabilities.

- **Drafting Responses:**
  Generates draft responses with `PromptTemplate`, which integrates various components of the app.

### Example Code Snippet

Here’s a simplified example of how to categorize a question:

```python
initial_question = "What is the code of conduct for the ALX program?"
question_category = question_category_generator.invoke({"initial_question": initial_question})
print(question_category)  # Outputs: 'course_enquiry'
```

---



---

## Future Enhancements

- **User Authentication:** Implement user login for personalized experiences.
- **Enhanced Search Capabilities:** Improve the web search integration for broader question coverage.
- **Feedback Loop:** Allow users to provide feedback on responses to improve accuracy over time.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

---

Feel free to customize this README as needed for your specific project details!
