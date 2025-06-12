import streamlit as st
import sqlite3
import smtplib
import random
import time
import os

# Config SMTP (exemplo Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = os.environ.get("GMAILBRENDO")
SENDER_PASSWORD = os.environ.get("ACESSOAPP"

# Criar conexão com DB SQLite (arquivo local)
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    email TEXT,
    password TEXT,
    mfa_code TEXT,
    mfa_expiry INTEGER
)
""")
conn.commit()

def send_email(to_email, subject, message):
    import ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

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
    new_user = st.text_input("Usuário")
    new_email = st.text_input("Email")
    new_password = st.text_input("Senha", type="password")
    if st.button("Registrar"):
        cursor.execute("SELECT * FROM users WHERE username=?", (new_user,))
        if cursor.fetchone():
            st.error("Usuário já existe!")
        else:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (new_user, new_email, new_password))
            conn.commit()
            st.success("Usuário registrado! Faça login.")

def login():
    st.subheader("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            # Gerar código MFA válido por 3 dias (em segundos)
            code = f"{random.randint(100000, 999999)}"
            expiry = int(time.time()) + 3*24*3600
            cursor.execute("UPDATE users SET mfa_code=?, mfa_expiry=? WHERE username=?", (code, expiry, username))
            conn.commit()
            send_email(user[1], "Seu código de acesso", f"Seu código MFA é: {code}")
            st.session_state["username"] = username
            st.session_state["mfa_sent"] = True
            st.success("Código MFA enviado ao seu email.")
        else:
            st.error("Usuário ou senha incorretos")

def verify_mfa():
    st.subheader("Verificação MFA")
    code_input = st.text_input("Código enviado por email")
    if st.button("Validar código"):
        username = st.session_state.get("username")
        if username:
            cursor.execute("SELECT mfa_code, mfa_expiry FROM users WHERE username=?", (username,))
            row = cursor.fetchone()
            if row:
                code_db, expiry = row
                now = int(time.time())
                if now > expiry:
                    st.error("Código expirado, faça login novamente.")
                    st.session_state.clear()
                    st.experimental_rerun()
                elif code_input == code_db:
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
        if st.button("Logout"):
            logout()
    elif st.session_state.get("mfa_sent"):
        verify_mfa()
        if st.button("Logout"):
            logout()
    else:
        register()
        login()
