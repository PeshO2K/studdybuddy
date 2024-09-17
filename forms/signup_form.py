import streamlit as st
from .generic_form import generic_form

credentials = {
    'password': 'abcd'
}
login_fields = {
    'Title': ':green[Create Account]',
 			'Subtitles': ['Please provide an email, username and password to continue'],
 			'Textfields': {
                            'Username': 'Username',
                            'Email': 'Email',                            
                            'Password': 'Password',
                            'Confirm Password': ' Confirm Password',
                        },
 			'Buttons': {'Submit': 'Sign up'}


}

def signup_form():
    form_values = generic_form('sidebar', login_fields, 'Signup')
    st.text(form_values)
    # st.text(st.session_state.Username)
    if form_values['submit'] :
        if credentials['password']==form_values['Password']:
         st.session_state['authentication_status'] = None
         st.rerun()
