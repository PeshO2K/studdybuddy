import streamlit as st
from .generic_form import generic_form
from utils.error_handler import print_error
from utils.auth_handler import authorise, loggedin_session
import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = os.getenv('BASE_URL')



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
    json_data = validate_data(form_values)
    # st.text(st.session_state.Username)
    if json_data:
        res = loggedin_session.post(f'{BASE_URL}/login', json=json_data)
        if res.status_code == 200:
            access_token = res.json().get('access_token')
            authorise(access_token)

        else:
            print_error("Incorrect username or password",'sidebar')


def validate_data(data):
   valid_data = None
   with st.sidebar:
    if data['submit']:
        if not data['Username']:
            print_error('Provide Username')

        if not data['Password']:
            print_error('Provide Password')

        
        valid_data = {
            'username': data['Username'],
            'password': data['Password'],
        }

   return valid_data
