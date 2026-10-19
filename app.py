import mysql.connector
import streamlit as st


@st.cache_resource
def get_db_connection():
  return mysql.connector.connect(
      host=st.secrets["mysql"]["host"],
      port=st.secrets["mysql"]["port"],
      user=st.secrets["mysql"]["user"],
      password=st.secrets["mysql"]["password"],
      database=st.secrets["mysql"]["database"],
      ssl_disabled=False,
  )


conn = get_db_connection()