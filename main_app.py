import streamlit as st
from forms.login_form import login_form
from forms.signup_form import signup_form


# # #------Initialise session state attributes
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None

if 'signing_in' not in st.session_state:
   st.session_state.signing_in = False

if 'nav_position' not in st.session_state:
   st.session_state.nav_position = 'sidebar'

# Function to handle log out


def logout():
  #  print("*******log out start ******")
   st.session_state.authentication_status = None
   st.session_state.signing_in = False
   st.session_state.nav_position = 'hidden'
   st.rerun()
  #  print("*******log out end ******")

# Update signin to true or false in order to switch pages from log in to signin when respective button is clicked


def update_login_status():
  st.session_state.signing_in = not st.session_state.signing_in
  st.rerun()


# Create Page objects for navigation
about_page = st.Page(
    page="views/about.py",
    title="About me",
    icon="👀",
)
project_1_page = st.Page(
    page="views/studybot.py",
    # page=btns,
    title="Study Buddy",
    icon="🧠",
    # default=True,
)

page_dict = {

    "Projects": [project_1_page],
    "Info": [about_page],

}

# ------ Login/SignUp pages or the Main app depending on authentication status
if st.session_state.authentication_status:

    pg = st.navigation(page_dict, position='sidebar'if st.session_state.authentication_status else 'hidden'
                       )

else:
    if not st.session_state.signing_in:
      signup_btn = st.sidebar.button("Sign Up", use_container_width=True)
      pg = st.navigation([st.Page(login_form)])

      st.title("Logging In Page")

      if signup_btn:
        update_login_status()

    else:
      login_btn = st.sidebar.button("Log in", use_container_width=True)

      if login_btn:
        update_login_status()
      # signup_form()
      pg = st.navigation([st.Page(signup_form)])

      st.title("Signing In Page")

pg.run()  # Render the selected page


# Render a logout button
if st.session_state.authentication_status:
  with st.sidebar:
    for idx in range(10):
      st.empty().write(">>>>>>>>>>")
  logout_btn = st.sidebar.button("Log out", use_container_width=True)
  if logout_btn:
      logout()
