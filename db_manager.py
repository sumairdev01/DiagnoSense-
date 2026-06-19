import mysql.connector
import hashlib
import json
import streamlit as st
from datetime import datetime
import sys

# Database Configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "port": 3306,
    "connect_timeout": 5
}

DB_NAME = "mediscan_db"

def get_db_connection(use_db=True):
    try:
        config = DB_CONFIG.copy()
        if use_db:
            config["database"] = DB_NAME
        db = mysql.connector.connect(**config)
        return db
    except Exception as e:
        print(f"DEBUG: Connection failed. Error: {e}")
        return None

def init_database():
    print("DEBUG: Starting database initialization...")
    # 1. Connect without database to create it if missing
    try:
        db = get_db_connection(use_db=False)
        if db is None:
            print("DEBUG: Could not connect to MySQL at all.")
            st.error("Could not connect to MySQL. Please ensure XAMPP MySQL is running on port 3306.")
            return False
        
        cursor = db.cursor()
        print(f"DEBUG: Creating database {DB_NAME} if not exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        db.commit()
        cursor.close()
        db.close()
        print("DEBUG: Database created or already exists.")
    except Exception as e:
        print(f"DEBUG: Error during DB creation: {e}")
        return False

    # 2. Now connect to the database and create tables
    try:
        db = get_db_connection(use_db=True)
        if db is None:
            print(f"DEBUG: Could not connect to {DB_NAME} after creation.")
            return False
        
        cursor = db.cursor()
        print("DEBUG: Creating tables...")
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                full_name VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin','doctor') NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doctor_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                cnic VARCHAR(50) NOT NULL UNIQUE,
                gender ENUM('Male','Female','Other') NOT NULL,
                age INT NOT NULL,
                phone VARCHAR(50) NOT NULL,
                address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Medical History table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NOT NULL,
                disease VARCHAR(255) NOT NULL,
                symptoms TEXT NOT NULL,
                treatment TEXT NOT NULL,
                diagnosis_date DATE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # AI Predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_name VARCHAR(255) NOT NULL,
                disease_type VARCHAR(100) NOT NULL,
                prediction_result VARCHAR(50) NOT NULL,
                confidence_score FLOAT,
                features_json TEXT,
                prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id VARCHAR(255) PRIMARY KEY,
                user_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        db.commit()
        
        # Create default users if none exist
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            print("DEBUG: Creating default users...")
            admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
            doctor_pass = hashlib.sha256("doctor123".encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (username, full_name, password_hash, role) 
                VALUES (%s, %s, %s, %s)
            """, ("admin", "System Administrator", admin_pass, "admin"))
            
            cursor.execute("""
                INSERT INTO users (username, full_name, password_hash, role) 
                VALUES (%s, %s, %s, %s)
            """, ("dr_johnson", "Dr. Robert Johnson", doctor_pass, "doctor"))
            
            db.commit()
        
        cursor.close()
        db.close()
        print("DEBUG: Database initialization complete.")
        return True
    except Exception as e:
        print(f"DEBUG: Error during table creation: {e}")
        return False

def create_session(user_id):
    import uuid
    session_id = str(uuid.uuid4())
    db = get_db_connection()
    if db is None: return None
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO user_sessions (session_id, user_id) VALUES (%s, %s)", (session_id, user_id))
        db.commit()
        return session_id
    except: return None
    finally:
        cursor.close()
        db.close()

def get_session_user(session_id):
    db = get_db_connection()
    if db is None: return None
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.* FROM users u
            JOIN user_sessions s ON u.id = s.user_id
            WHERE s.session_id = %s
        """, (session_id,))
        user = cursor.fetchone()
        return user
    except: return None
    finally:
        cursor.close()
        db.close()

def delete_session(session_id):
    db = get_db_connection()
    if db is None: return False
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM user_sessions WHERE session_id = %s", (session_id,))
        db.commit()
        return True
    except: return False
    finally:
        cursor.close()
        db.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    db = get_db_connection()
    if db is None:
        return False, None
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    
    if user and user["password_hash"] == hash_password(password):
        return True, user
    return False, None

def get_all_users():
    db = get_db_connection()
    if db is None: return []
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, full_name, role, created_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return users

def add_user(username, full_name, password, role):
    db = get_db_connection()
    if db is None: return False, "DB Connection failed"
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (username, full_name, password_hash, role) VALUES (%s, %s, %s, %s)",
                      (username, full_name, hash_password(password), role))
        db.commit()
        return True, "User added"
    except Exception as e: return False, str(e)
    finally:
        cursor.close()
        db.close()

def delete_user(user_id):
    db = get_db_connection()
    if db is None: return False
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s AND role != 'admin'", (user_id,))
    db.commit()
    cursor.close()
    db.close()
    return True

def get_all_patients():
    db = get_db_connection()
    if db is None: return []
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT p.*, u.full_name as doctor_name FROM patients p LEFT JOIN users u ON p.doctor_id = u.id ORDER BY p.created_at DESC")
    patients = cursor.fetchall()
    cursor.close()
    db.close()
    return patients

def delete_patient(patient_id):
    db = get_db_connection()
    if db is None: return False
    cursor = db.cursor()
    cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
    db.commit()
    cursor.close()
    db.close()
    return True

def get_all_medical_history():
    db = get_db_connection()
    if db is None: return []
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT h.*, p.name as patient_name, u.full_name as doctor_name
        FROM medical_history h
        JOIN patients p ON h.patient_id = p.id
        JOIN users u ON h.doctor_id = u.id
        ORDER BY h.diagnosis_date DESC
    """)
    history = cursor.fetchall()
    cursor.close()
    db.close()
    return history

def get_statistics():
    db = get_db_connection()
    if db is None: return {}
    cursor = db.cursor(dictionary=True)
    stats = {}
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'doctor'")
    stats["total_doctors"] = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) as count FROM patients")
    stats["total_patients"] = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) as count FROM medical_history")
    stats["total_records"] = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) as count FROM ai_predictions WHERE prediction_result = 'Risk'")
    stats["risk_cases"] = cursor.fetchone()["count"]
    cursor.close()
    db.close()
    return stats

def get_doctor_patients(doctor_id):
    db = get_db_connection()
    if db is None: return []
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients WHERE doctor_id = %s ORDER BY created_at DESC", (doctor_id,))
    patients = cursor.fetchall()
    cursor.close()
    db.close()
    return patients

def add_patient(doctor_id, name, cnic, gender, age, phone, address):
    db = get_db_connection()
    if db is None: return False, "DB Connection failed"
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO patients (doctor_id, name, cnic, gender, age, phone, address) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                      (doctor_id, name, cnic, gender, age, phone, address))
        db.commit()
        return True, "Patient registered"
    except Exception as e: 
        if "Duplicate entry" in str(e):
            return False, "This CNIC is already registered in the system."
        return False, str(e)
    finally:
        cursor.close()
        db.close()

def add_medical_history(patient_id, doctor_id, disease, symptoms, treatment, diagnosis_date):
    db = get_db_connection()
    if db is None: return False, "DB Connection failed"
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO medical_history (patient_id, doctor_id, disease, symptoms, treatment, diagnosis_date) VALUES (%s, %s, %s, %s, %s, %s)",
                      (patient_id, doctor_id, disease, symptoms, treatment, diagnosis_date))
        db.commit()
        return True, "Record saved"
    except Exception as e: return False, str(e)
    finally:
        cursor.close()
        db.close()

def get_patient_medical_history(patient_id):
    db = get_db_connection()
    if db is None: return []
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medical_history WHERE patient_id = %s ORDER BY diagnosis_date DESC", (patient_id,))
    history = cursor.fetchall()
    cursor.close()
    db.close()
    return history

def get_ai_predictions():
    db = get_db_connection()
    if db is None: return []
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ai_predictions ORDER BY prediction_date DESC LIMIT 100")
    predictions = cursor.fetchall()
    cursor.close()
    db.close()
    return predictions

def save_prediction(patient_name, disease_type, prediction_result, confidence_score, features):
    db = get_db_connection()
    if db is None: return False
    cursor = db.cursor()
    cursor.execute("INSERT INTO ai_predictions (patient_name, disease_type, prediction_result, confidence_score, features_json) VALUES (%s, %s, %s, %s, %s)",
                  (patient_name, disease_type, prediction_result, confidence_score, json.dumps(features)))
    db.commit()
    cursor.close()
    db.close()
    return True

def delete_prediction(prediction_id):
    db = get_db_connection()
    if db is None: return False
    cursor = db.cursor()
    cursor.execute("DELETE FROM ai_predictions WHERE id = %s", (prediction_id,))
    db.commit()
    cursor.close()
    db.close()
    return True
