import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = os.getenv('BASE_URL')

loggedin_session = requests.Session()

def authorise(token):
   st.session_state['authentication_status'] = True
   loggedin_session.headers.update(
          {'Authorization': 'Bearer ' + token})
   st.rerun()

# Function to handle log out


def logout():
  #  print("*******log out start ******")
   st.session_state.authentication_status = None
   loggedin_session.headers.pop(
       'Authorization')
   st.session_state.signing_up = False
   st.session_state.nav_position = 'hidden'
   st.rerun()

# Handle refresh


def handle_refresh():
   REFRESH_URL = BASE_URL+'/refresh'
   response = loggedin_session.get(REFRESH_URL)
   if response.status_code == 200:
      access_token = response.json().get('access_token')
      loggedin_session.headers.update(
          {'Authorization': 'Bearer ' + access_token})
      
      st.title(access_token)
      return access_token
   else:
      logout()


def handle_verification(token):
   VERIFICATION_URL = BASE_URL+f'/verify'
   response = loggedin_session.post(VERIFICATION_URL,json={"token":token})
   if response.status_code == 200:
      st.success("EMAIL HAS BEEN VERIFIED")
      st.query_params.clear()
      return
   
