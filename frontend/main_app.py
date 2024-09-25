import streamlit as st
from forms.login_form import login_form
from forms.signup_form import signup_form
from utils.auth_handler import logout

# # #------Initialise session state attributes
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None

if 'signing_up' not in st.session_state:
   st.session_state.signing_up = False

if 'nav_position' not in st.session_state:
   st.session_state.nav_position = 'sidebar'


def render_logout_btn():
    # Render a logout button
  if st.session_state.authentication_status:
    with st.sidebar:
      # st.text(st.session_state.access_token)
      for idx in range(10):
        st.empty().write(">>>>>>>>>>")
    logout_btn = st.sidebar.button("Log out", use_container_width=True)
    if logout_btn:
        logout()



def update_login_status():
  st.session_state.signing_up = not st.session_state.signing_up
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
    if not st.session_state.signing_up:
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

      st.title("Signing Up Page")

pg.run()  # Render the selected page
render_logout_btn()
