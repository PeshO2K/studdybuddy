import streamlit as st


#-------PAGE SETUP--------------
about_page=st.Page(
  page = "/content/drive/MyDrive/StuddyBuddyRepo/views/about.py",
  title="About me",
  icon=":material/account_circle:",
)
project_1_page=st.Page(
  page = "/content/drive/MyDrive/StuddyBuddyRepo/views/studybot.py",
  title="Study Buddy",
  icon=":material/smart_toy:",
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