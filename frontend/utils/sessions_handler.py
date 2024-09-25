import streamlit as st
from .error_handler import print_error
from .auth_handler import *
import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = os.getenv('BASE_URL')


def fetch_user_sessions():
    def fetch_sessions():
        return loggedin_session.get(
            BASE_URL + '/users/me/sessions'
        )
    response = fetch_sessions()
    if response.status_code == 401 or response.status_code == 403:
        handle_refresh()
        response=fetch_sessions()
    
    if response.status_code == 200:
       return response.json()
    
    print_error("Oops! There was a problem retrieving your sessions.")
    return None


def fetch_session_log(session_id):
    #    returns a list of the session messages
    def fetch_log(): 
        return loggedin_session.get(
            BASE_URL + f'/users/me/sessions/{session_id}/log'
        )

    response = fetch_log()
    if response.status_code == 401 or response.status_code == 403:
        handle_refresh()
        response=fetch_log()
    if response.status_code == 200:
       session_log = response.json().get('messages')
       return session_log
   

    print_error("Oops! We couldn't retrieve your messages")
    return None


def create_new_session(session):
   def create_session():
       return loggedin_session.post(
           BASE_URL + '/users/me/sessions',           
           json=session
       )
   response = create_session()
   if response.status_code == 401 or response.status_code == 403:
       handle_refresh()
       response = create_session()


   if response.status_code == 200 or response.status_code == 201:
       created_session_id = response.json().get('session_id')
       # st.text(created_session_id)
       return created_session_id
   
   print_error("Oops! Chat could not be saved")
   return None


def save_session(session_id, messages):
   session = {"messages": messages}
   def update_session():
       return loggedin_session.put(
           BASE_URL + f'/users/me/sessions/{session_id}',
           json=session
       )
   response = update_session()
   if response.status_code == 401 or response.status_code == 403:
       handle_refresh()
       response = update_session()
   if response.status_code == 200:
      return True

   print_error("Oops! Chat could not be updated")
   return None
