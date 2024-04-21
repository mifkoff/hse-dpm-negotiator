import streamlit as st
from setup import db_manager, client
from utils import get_index_of_case, convert_mongodb_messages_to_langchain_format
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import content

st.set_page_config(
    page_title="Высшая Школа Ремонта",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialization
if "user_id" in st.session_state:
    user_id = int(st.session_state["user_id"])
else:
    user_id = -1
user_cases = db_manager.get_user_cases(user_id=int(user_id))

if "case_id" in st.session_state:
    case_id = st.session_state["case_id"]
    case_index = get_index_of_case(user_cases=user_cases, case_id=case_id)
else:
    case_index = None

# Instructions
with st.sidebar:
    st.page_link("main.py", label="Главная", icon="🏠")
    st.page_link("pages/cases.py", label="Список кейсов", icon="📃")
    st.write('---')
    content.INSTRUCTIONS_TEXT

# Case selection
selected_case = st.selectbox(
    'Выберите рассматриваемый кейс',
    (x["title"] for x in user_cases),
    index=case_index,
    placeholder="Выберите кейс..."
    )

# Dialogue log
if selected_case:
    st.write(f"💬 Диалог в рамках кейса «{selected_case}».")
    st.caption("Присылайте ответы контрагента сообщениями.")
    st.session_state["messages"] = []
    
    # Get case data
    case_data = db_manager.get_case_by_user_and_title(user_id=user_id, title=selected_case)

    if case_data is not None:
        # Get case messages
        messages = db_manager.get_messages_by_case_id(case_id=case_data["_id"])
        if len(messages) == 0:
            # Init dialogue
            init_messages = [
                SystemMessage(content=content.INIT_SYSTEM_TEXT.format(initial_price=case_data["starting_price"], buyers_budget=case_data["budget"], price_target=case_data["target_price"], seller_name=case_data["counterparty_name"], deal_type=case_data["case_type"])),
                HumanMessage(content=content.INIT_HUMAN_TEST.format(seller_offer=case_data["incoming_offer"])),
                SystemMessage(content=content.INIT_SYSTEM_USER_QUESTION)
            ]
            answer_result = client(init_messages)
            db_manager.add_message(case_id=case_data["_id"], role=content.SYSTEM_TYPE, content=init_messages[0].content)
            db_manager.add_message(case_id=case_data["_id"], role=content.HUMAN_TYPE, content=init_messages[1].content)
            db_manager.add_message(case_id=case_data["_id"], role=content.SYSTEM_TYPE, content=init_messages[2].content)
            db_manager.add_message(case_id=case_data["_id"], role=content.AI_TYPE, content=answer_result.content)
            st.session_state["messages"] = [
                SystemMessage(content=init_messages[0].content),
                HumanMessage(content=init_messages[1].content),
                SystemMessage(content=init_messages[2].content),
                AIMessage(content=answer_result.content)
            ]
        
        # st.write(messages) # debug

        if "messages" not in st.session_state or ("messages" in st.session_state and st.session_state["messages"] == []):
            st.session_state["messages"] = convert_mongodb_messages_to_langchain_format(messages=messages)
        
        # View case messages
        for msg in st.session_state.messages:
            if msg.type != "system":
                st.chat_message(msg.type).write(msg.content)
        
        # User's prompt:
        if prompt := st.chat_input(placeholder="Введите ответ контрагента"):
            st.chat_message(content.HUMAN_TYPE).write(prompt)
            db_manager.add_message(case_id=case_data["_id"], role=content.HUMAN_TYPE, content=prompt)
            st.session_state["messages"].append(HumanMessage(content=prompt))
            # TODO modify prompt
            answer_result = client(st.session_state["messages"])
            st.chat_message(content.AI_TYPE).write(answer_result.content)
            db_manager.add_message(case_id=case_data["_id"], role=content.AI_TYPE, content=answer_result.content)
            st.session_state["messages"].append(AIMessage(content=answer_result.content))
        st.html(
            f"""
                <script>
                    var input = window.parent.document.querySelectorAll("input[type=text]");
                    for (var i = 0; i < input.length; ++i) {{
                        input[i].focus();
                    }}
            </script>
            """,
            height=0,
        )
    else:
        st.error('Ошибка. Кейса не существует.', icon="🚨")
