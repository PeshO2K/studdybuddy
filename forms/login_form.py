import streamlit as st
from .generic_form import generic_form

credentials ={
    'password':'abcd'
}

login_fields = {
    'Title': ':green[Welcome Back]',
             'Subtitles': ['Please enter your username and password to log in'],
             'Textfields': {
                            'Username': 'Username',
                            'Password': 'Password',
                        },
             'Buttons': {'Submit': 'Log in ',
                            }


}

def login_form():
    form_values = generic_form('sidebar', login_fields, 'Login')
    st.text(form_values)
    # st.text(st.session_state.Username)
    if form_values['submit'] :
        if credentials['password']==form_values['Password']:
         st.session_state['authentication_status'] = True
         st.rerun()
