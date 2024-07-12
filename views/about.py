import streamlit as st
from forms.contact_form import contact_form

@st.experimental_dialog("Contact Me")
def show_contact_form():
  contact_form()

#-------Hero section
col1,col2 =st.columns(2,gap="small",vertical_alignment='center')
with col1:
  st.image("assets/my_dip.jpg", width=200)
with col2:
  st.title("Patience Otuke", anchor=False)
  st.write("Electrical Engineer, Solutions Architect, FullStack Developer")
  st.write("I am a Jane of all Trades.\
   You are likely o find me in posession of pair of pliers than a tube of lipstick.\
   I like to to read and Stuff:)")
  if st.button("Contact me"):
    show_contact_form()

# --- EXPERIENCE & QUALIFICATIONS ---
st.write("\n")
st.subheader("Experience & Qualifications", anchor=False)
st.write(
    """
    - 7 Years experience extracting actionable insights from data
    - Strong hands-on experience and knowledge in Python and Excel
    - Good understanding of statistical principles and their respective applications
    - Excellent team-player and displaying a strong sense of initiative on tasks
    """
)

# --- SKILLS ---
st.write("\n")
st.subheader("Hard Skills", anchor=False)
st.write(
    """
    - Programming: Python (Scikit-learn, Pandas), SQL, VBA
    - Data Visualization: PowerBi, MS Excel, Plotly
    - Modeling: Logistic regression, linear regression, decision trees
    - Databases: Postgres, MongoDB, MySQL
    """
)
