import streamlit as st
from .generic_form import generic_form
from utils.error_handler import print_error
from utils.auth_handler import authorise, loggedin_session
import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = os.getenv('BASE_URL')



login_fields = {
    'Title': ':green[Password Reset]',
             'Subtitles': ['Please enter your new password password'],
             'Textfields': {
                            'Password': 'Password',
                            'Confirm Password': 'Confirm Password',
                        },
             'Buttons': {'Submit': 'Reset',
                            }


}

def reset_form():
    form_values = generic_form('sidebar', login_fields, 'Reset')
    st.text(form_values)
    json_data = validate_data(form_values)
    
    # st.text(st.session_state.Username)
    if json_data:
        json_data['token'] = st.session_state.reset_token
        res = loggedin_session.post(
            f'{BASE_URL}/reset-password', json=json_data)
        if res.status_code == 200:
            st.success("Reset successful")
            
            st.session_state.reset_token = None
            st.session_state.pwd_reset_link = False
            st.session_state.pwd_reset = False
            st.rerun()

        else:
            print_error("Error occured, Reset failed",'sidebar')


def validate_data(data):
   valid_data = None
   with st.sidebar:
    if data['submit']:
        if not data['Password']:
            print_error('Provide Password')

        if not data['Confirm Password']:
            print_error('Please Confirm Password')

        if not data['Confirm Password'] == data['Password']:
            print_error("Passwords Don't match")

        
        valid_data = {
            'new_password': data['Password'],
            
        }

   return valid_data
