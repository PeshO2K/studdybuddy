import streamlit as st
from .generic_form import generic_form
from utils.error_handler import print_error
from utils.auth_handler import authorise, loggedin_session
import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = os.getenv('BASE_URL')



form_fields = {
    'Title': ':green[Reset Password Email]',
             'Subtitles': ['Please enter your email address to receive the reset link'],
             'Textfields': {
                            'Email': 'Email',
                        },
             'Buttons': {'Submit': 'Send Reset Link',
                            }


}

def reset_link_form():
    form_values = generic_form('sidebar', form_fields, 'Reset_Link')
    st.text(form_values)
    json_data = validate_data(form_values)
    # st.text(st.session_state.Username)
    if json_data:
        st.warning("Sending the data")
        REST_LINK_URL = BASE_URL+f'/forgot-password'
        response = loggedin_session.post(REST_LINK_URL, json=json_data)
        if response.status_code == 200:
            st.success("CHECK EMAIL FOR RESET LINK")
            # return

        else:
            print_error(response.json().get('detail'),'sidebar')


def validate_data(data):
   valid_data = None
   with st.sidebar:
    if data['submit']:
        if not data['Email']:
            print_error('Provide Email')

        valid_data = {
            'email': data['Email'],          
        }

   return valid_data
