import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import smtplib
import random
import time
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Variavens de secretas
mongo_atlas = os.environ.get("URLBANCO")
gmail = os.environ.get("GMAIL")
senhaacesso = os.environ.get("SENHAGMAIL")

# Variáveis de ambiente
MONGO_URI = mongo_atlas  # Ex: mongodb+srv://user:senha@cluster.mongodb.net/dbname
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = gmail
SENDER_PASSWORD = senhaacesso

# Conexão MongoDB
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client["meuapp"]  # assume o nome do banco do URI
users_collection = db["users"]
logs_collection = db["logs"]

def log_action(username, action, details=None):
    logs_collection.insert_one({
        "username": username,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow()
    })

def send_email(to_email, subject, message):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

def register():
    st.subheader("Registrar novo usuário")
    new_user = st.text_input("Usuário", key="register_user")
    new_email = st.text_input("Email", key="register_email")
    new_password = st.text_input("Senha", type="password", key="register_password")
    if st.button("Registrar", key="register_button"):
        if not new_user or not new_email or not new_password:
            st.error("Preencha todos os campos para registrar.")
            return
        if users_collection.find_one({"username": new_user}):
            st.error("Usuário já existe!")
        else:
            users_collection.insert_one({
                "username": new_user,
                "email": new_email,
                "password": new_password,
                "mfa_code": None,
                "mfa_expiry": None
            })
            st.success("Usuário registrado! Faça login.")

def login():
    st.subheader("Login")
    username = st.text_input("Usuário", key="login_user")
    password = st.text_input("Senha", type="password", key="login_password")
    if st.button("Entrar", key="login_button"):
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            code = f"{random.randint(100000, 999999)}"
            expiry = int(time.time()) + 3 * 24 * 3600
            users_collection.update_one({"username": username}, {"$set": {"mfa_code": code, "mfa_expiry": expiry}})
            send_email(user["email"], "Seu código de acesso", f"Seu código MFA é: {code}")
            st.session_state["username"] = username
            st.session_state["mfa_sent"] = True
            st.success("Código MFA enviado ao seu email.")
        else:
            st.error("Usuário ou senha incorretos")

def verify_mfa():
    st.subheader("Verificação MFA")
    code_input = st.text_input("Código enviado por email", key="mfa_code_input")
    if st.button("Validar código", key="mfa_validate_button"):
        username = st.session_state.get("username")
        if username:
            user = users_collection.find_one({"username": username})
            if user:
                now = int(time.time())
                if now > user.get("mfa_expiry", 0):
                    st.error("Código expirado, faça login novamente.")
                    st.session_state.clear()
                    st.experimental_rerun()
                elif code_input == user.get("mfa_code"):
                    st.success("Login confirmado!")
                    st.session_state["mfa_passed"] = True
                else:
                    st.error("Código inválido.")
            else:
                st.error("Usuário não encontrado.")
        else:
            st.error("Faça login primeiro.")

def logout():
    st.session_state.clear()
    st.experimental_rerun()

def app():
    if st.session_state.get("mfa_passed"):
        st.write(f"Bem-vindo, {st.session_state['username']}!")
        if st.button("Logout", key="logout_button"):
            logout()
    elif st.session_state.get("mfa_sent"):
        verify_mfa()
        if st.button("Logout", key="logout_button_2"):
            logout()
    else:
        option = st.selectbox("Escolha uma opção", ["Login", "Registrar"], key="login_register_select")
        if option == "Login":
            login()
        else:
            register()
