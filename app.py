import mysql.connector
import streamlit as st


@st.cache_resource
def get_db_connection():
  return mysql.connector.connect(
      host=st.secrets["mysql"]["host"],
      port=int(st.secrets["mysql"]["port"]),
      user=st.secrets["mysql"]["user"],
      password=st.secrets["mysql"]["password"],
      database=st.secrets["mysql"]["database"],
      ssl_verify_cert=True,
      ssl_verify_identity=True,
  )


conn = get_db_connection()