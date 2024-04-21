import streamlit as st
from setup import db_manager
from streamlit_option_menu import option_menu
from datetime import datetime
import hmac


st.set_page_config(
    page_title="Высшая Школа Ремонта",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Введите пароль", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Неверный пароль")
    return False


if not check_password():
    st.stop()

# import telegram webapp js
st.html('<script src="https://telegram.org/js/telegram-web-app.js"></script>')
st.title("😎 Ваш помощник в торге")
st.header("Добавьте новый кейс:")

# loading
try:
    user_id = st.query_params["user_id"]
except KeyError:
    user_id = -1
if user_id:
    try:
        user_cases = db_manager.get_user_cases(user_id=int(user_id))
    except Exception:
        pass
else:
    db_manager.add_user(
        user_id=user_id,
        name="None"
    )
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = user_id

with st.sidebar:
    st.page_link("main.py", label="Главная", icon="🏠")
    st.page_link("pages/cases.py", label="Список кейсов", icon="📃")

# add form for a new case
with st.form('Add new case here:'):
    deal_type = st.selectbox(
        'Какой тип объекта спора?',
        ('Услуги', 'Товары', 'Материалы'),
        key='deal_type'
    )
    counterparty_name = st.text_input(
        "Введите имя контрагента",
        placeholder="Михаил",
        key="counterparty_name",
    )
    counterparty_offer_text = st.text_input(
        "Введите предложение контрагента",
        placeholder="Добрый день. Направляю вам коммерческое предложение.",
        key="counterparty_offer_text",
    )
    counterparty_offer_price = st.text_input(
        "Введите предложенную стоимость",
        placeholder="15000",
        key="counterparty_offer_price",
    )
    budget = st.text_input(
        "Введите желаемую стоимость",
        placeholder="10000",
        key="budget",
    )
    submitted = st.form_submit_button("Submit")
    if submitted:
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d/%m/%Y %H:%M")
        case_id = db_manager.add_case(
            title=f'{formatted_datetime}: {deal_type}, {counterparty_name}, {counterparty_offer_price}, {budget}',
            user_id=user_id,
            case_type=deal_type,
            counterparty_name=counterparty_name,
            budget=budget,
            starting_price=counterparty_offer_price,
            target_price='-10%',
            incoming_offer=counterparty_offer_text
            )
        st.session_state['case_id'] = case_id
        st.success('Case successfully added!', icon="✅")
        st.switch_page("pages/cases.py")