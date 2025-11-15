import streamlit as st
import mysql.connector
import hashlib  # For basic password hashing (use bcrypt in production)
import os
import sys
sys.path.append(r'C:\Users\DELL\AppData\Roaming\Python\Python313\site-packages')
from dotenv import load_dotenv

load_dotenv()

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "megha1712"),
        database=os.getenv("DB_NAME", "quiz_app")
    )

# Hash password (basic example)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authenticate user
def authenticate(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE username = %s AND password = %s", (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

# Register new user
def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        conn.close()
        return False  # Username exists
    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')", (username, hash_password(password)))
    conn.commit()
    conn.close()
    return True

# Get user scores
def get_user_scores(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT score, total_questions, timestamp FROM scores WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
    scores = cursor.fetchall()
    conn.close()
    return scores

# Add question (admin only)
def add_question(question, a, b, c, d, correct):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_answer) VALUES (%s, %s, %s, %s, %s, %s)",
                   (question, a, b, c, d, correct))
    conn.commit()
    conn.close()

# Get all questions
def get_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY RAND() LIMIT 5")
    questions = cursor.fetchall()
    conn.close()
    return questions

# Save score
def save_score(user_id, score, total):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (user_id, score, total_questions) VALUES (%s, %s, %s)", (user_id, score, total))
    conn.commit()
    conn.close()

# Streamlit App
st.title("Quiz Application")

# Session state for login
if 'user' not in st.session_state:
    st.session_state.user = None

# Login Section
if st.session_state.user is None:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            user = authenticate(username, password)
            if user:
                st.session_state.user = user
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        st.subheader("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        if st.button("Register"):
            if reg_password != reg_confirm:
                st.error("Passwords do not match")
            elif register_user(reg_username, reg_password):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists")
else:
    user_id, role = st.session_state.user
    st.sidebar.write(f"Logged in as {role}")

    # Admin Mode
    if role == 'admin':
        st.subheader("Admin Panel")
        with st.form("add_question"):
            question = st.text_area("Question")
            a = st.text_input("Option A")
            b = st.text_input("Option B")
            c = st.text_input("Option C")
            d = st.text_input("Option D")
            correct = st.selectbox("Correct Answer", ['A', 'B', 'C', 'D'])
            if st.form_submit_button("Add Question"):
                add_question(question, a, b, c, d, correct)
                st.success("Question added!")

        # View Questions
        st.subheader("Existing Questions")
        questions = get_questions()
        for q in questions:
            st.write(f"Q{q[0]}: {q[1]} (Correct: {q[6]})")

    # User Mode (Quiz)
    else:
        st.subheader("Take Quiz")
        questions = get_questions()
        if questions:
            user_answers = {}
            for q in questions:
                st.write(q[1])
                user_answers[q[0]] = st.radio(f"Options for Q{q[0]}", [q[2], q[3], q[4], q[5]], key=q[0])

            if st.button("Submit Quiz"):
                score = 0
                for q in questions:
                    correct_option = {'A': q[2], 'B': q[3], 'C': q[4], 'D': q[5]}[q[6]]
                    if user_answers[q[0]] == correct_option:
                        score += 1
                save_score(user_id, score, len(questions))
                st.success(f"Your score: {score}/{len(questions)}")
        else:
            st.write("No questions available.")

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
