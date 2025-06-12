import streamlit as st
import sqlite3
import random
import time
import smtplib
from datetime import datetime, timedelta

# --- Configurações SMTP para envio do código MFA ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = GMAILBRENDO
SENDER_PASSWORD = ACESSOAPP  # senha do app gerada no gmail

# --- Banco SQLite ---
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

# Criar tabela users (se não existir)
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    name TEXT,
    email TEXT,
    password TEXT
)
""")

# Criar tabela mfa_codes (para guardar códigos e timestamp)
c.execute("""
CREATE TABLE IF NOT EXISTS mfa_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    code TEXT,
    created_at INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")
conn.commit()

# --- Funções banco ---
def add_user(username, name, email, password):
    try:
        c.execute("INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)",
                  (username, name, email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(username):
    c.execute("SELECT id, username, name, email, password FROM users WHERE username = ?", (username,))
    return c.fetchone()

def save_mfa_code(user_id, code):
    now = int(time.time())
    c.execute("INSERT INTO mfa_codes (user_id, code, created_at) VALUES (?, ?, ?)", (user_id, code, now))
    conn.commit()

def get_latest_mfa_code(user_id):
    c.execute("SELECT code, created_at FROM mfa_codes WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
    return c.fetchone()

def clear_old_codes(user_id):
    # Opcional: deletar códigos antigos
    c.execute("DELETE FROM mfa_codes WHERE user_id = ?", (user_id,))
    conn.commit()

# --- Função envio email ---
def send_email(to_email, subject, body):
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            msg = f"Subject: {subject}\n\n{body}"
            smtp.sendmail(SENDER_EMAIL, to_email, msg)
        return True
    except Exception as e:
        st.error(f"Erro ao enviar email: {e}")
        return False

# --- App Streamlit ---
def signup():
    st.header("Cadastro")
    username = st.text_input("Usuário")
    name = st.text_input("Nome Completo")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    confirm_password = st.text_input("Confirme a senha", type="password")

    if st.button("Cadastrar"):
        if not username or not name or not email or not password:
            st.error("Preencha todos os campos")
            return
        if password != confirm_password:
            st.error("Senhas não coincidem")
            return
        if add_user(username, name, email, password):
            st.success("Usuário cadastrado com sucesso! Faça login.")
        else:
            st.error("Usuário já existe")

def login():
    st.header("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = get_user(username)
        if user is None:
            st.error("Usuário não encontrado")
            return
        if password != user[4]:
            st.error("Senha incorreta")
            return
        
        user_id = user[0]
        user_name = user[2]
        user_email = user[3]

        # MFA
        now_ts = int(time.time())
        mfa_data = get_latest_mfa_code(user_id)
        code_valid = False

        # Timeout 3 dias = 3*24*3600
        timeout_seconds = 3 * 24 * 3600

        if mfa_data:
            code, created_at = mfa_data
            if now_ts - created_at < timeout_seconds:
                code_valid = True
            else:
                # Código expirou, limpar
                clear_old_codes(user_id)
                code_valid = False

        if "mfa_passed" not in st.session_state:
            st.session_state.mfa_passed = False

        if not st.session_state.mfa_passed or not code_valid:
            if not code_valid:
                # Gerar código novo
                code = f"{random.randint(100000, 999999)}"
                save_mfa_code(user_id, code)
                send_email(user_email, "Seu código de acesso", f"Olá {user_name}, seu código de acesso é: {code}")
                st.info("Código MFA enviado para seu email")

            codigo_input = st.text_input("Digite o código enviado no email")
            if st.button("Validar código"):
                if codigo_input == code:
                    st.session_state.mfa_passed = True
                    st.success(f"Bem-vindo, {user_name}! Você está autenticado.")
                else:
                    st.error("Código incorreto")

        else:
            st.session_state.mfa_passed = True
            st.success(f"Bem-vindo, {user_name}! Você está autenticado.")

def main():
    st.title("App com Cadastro + Login + MFA via Email")

    menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro"])
    if menu == "Login":
        login()
    else:
        signup()

if __name__ == "__main__":
    main()
