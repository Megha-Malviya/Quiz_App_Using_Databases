# Quiz App

A simple quiz application with Python, MySQL, and Streamlit.

## Local Setup
1. Install Python, MySQL.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the database setup script in MySQL: `mysql -u root -p < setup_db.sql` (enter your MySQL password when prompted)
6. Create a `.env` file in the project root with your database credentials (see .env.example)
7. Run the app: `streamlit run quiz_app.py`

## Default Credentials
- Admin Username: admin
- Admin Password: admin

## Deployment
Push to GitHub, deploy on Streamlit Cloud with secrets.
