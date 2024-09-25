import streamlit as st
from .generic_form import generic_form
from utils.error_handler import print_error
import requests
import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = os.getenv('BASE_URL')


signup_fields = {
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
    form_values = generic_form('sidebar', signup_fields, 'Signup')
    st.text(form_values)
    json_data = validate_data(form_values)
    # st.text(st.session_state.Username)
    if json_data:
    
         res = requests.post(BASE_URL+'/signup',json=json_data)
         if res.status_code == 201:
             st.text(res.text)
         
             st.session_state['signing_up'] = False
         
         else:
           print_error("Error: User was not registered, please try again.")
         st.session_state['authentication_status'] = None
        
         st.rerun()
         
def validate_data(data):
   valid_data = None
   with st.sidebar:
    if data['submit']:
        if not data['Username']:
            print_error('Provide Username')

        if not data['Email']:
            print_error('Provide Email')

        if not data['Password']:
            print_error('Provide Password')

        if not data['Confirm Password']:
            print_error('Please Confirm Password')
            
        if not data['Confirm Password'] == data['Password']:
            print_error("Passwords Don't match")
            


        valid_data = {
            'username' : data['Username'],
            'email' : data['Email'],
            'password' : data['Password'],
                        }
    
   return valid_data
