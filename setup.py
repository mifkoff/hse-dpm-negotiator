from database_manager import DatabaseManager
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import streamlit as st

openai_api_key = st.secrets.openai.api_key
openai_model = st.secrets.openai.model
openai_temperature = st.secrets.openai.temperature
mongodb_uri = st.secrets.mongodb.uri
mongodb_database = st.secrets.mongodb.database

db_manager = DatabaseManager(mongodb_uri, mongodb_database)
client = ChatOpenAI(
    openai_api_key=openai_api_key,
    model=openai_model,
    temperature=0.9
)