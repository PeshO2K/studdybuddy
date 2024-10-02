import streamlit as st
from forms.login_form import login_form
from forms.signup_form import signup_form
from forms.reset_form import reset_form
from forms.reset_link_form import reset_link_form
from utils.auth_handler import logout, handle_verification

# # #------Initialise session state attributes
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None

if 'signing_up' not in st.session_state:
   st.session_state.signing_up = False

if 'pwd_reset' not in st.session_state:
   st.session_state.pwd_reset = False
   
if 'pwd_reset_link' not in st.session_state:
   st.session_state.pwd_reset_link = False

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
    verification_token = st.query_params.get("token", None)

    if verification_token:
       handle_verification(verification_token)
    
    reset_token = st.query_params.get("reset", None)

    if reset_token:
       st.session_state.pwd_reset = True
       st.session_state.reset_token = reset_token
       st.query_params.clear()

    if st.session_state.pwd_reset:
       # render the reset form
       pg = st.navigation([st.Page(reset_form)])
      #  handle_verification(reset_token)
    elif st.session_state.pwd_reset_link:
       pg = st.navigation([st.Page(reset_link_form)])
    
    elif not st.session_state.signing_up:
      btn_container = st.sidebar.container()

      left, right = btn_container.columns([1,2], vertical_alignment="bottom")
      signup_btn = left.button("Sign Up", use_container_width=False)
      pwd_reset_btn = right.button("Forgot Password", use_container_width=True)

      pg = st.navigation([st.Page(login_form)])

      st.title("Logging In Page")

      if signup_btn:
        update_login_status()
      if pwd_reset_btn:
        st.session_state.pwd_reset_link = True
        st.rerun()

    else:
      login_btn = st.sidebar.button("Log in", use_container_width=True)

      if login_btn:
        update_login_status()
      # signup_form()
      pg = st.navigation([st.Page(signup_form)])
      st.title("Signing Up Page")
      
         

      

pg.run()  # Render the selected page
render_logout_btn()
