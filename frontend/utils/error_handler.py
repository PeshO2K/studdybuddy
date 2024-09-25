import streamlit as st
def print_error(msg: str, location: str = 'main', is_error: bool = True):
   if location == 'main':
      if is_error:
         st.error(msg)
      else:
         st.warning(msg)
   if location == 'sidebar':
       if is_error:
           st.sidebar.error(msg)
       else:
           st.sidebar.warning(msg)
   st.stop()
