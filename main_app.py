import streamlit as st


#-------PAGE SETUP--------------
about_page=st.Page(
  page = "views/about.py",
  title="About me",
  icon="👀",
)
project_1_page=st.Page(
  page = "views/studybot.py",
  title="Study Buddy",
  icon="🧠",
  default=True,
)

pg=st.navigation(
  {
    "Projects":[project_1_page],
    "Info":[about_page],
  }
)
st.sidebar.text("Made By Pesh")
pg.run()
