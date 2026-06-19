"""
MediScan AI - Multi-Disease Early Prediction System
Professional Healthcare Management Platform (Stable Version)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json

# Import Custom Modules
from db_manager import (
    init_database, authenticate_user, get_all_users, add_user, delete_user,
    get_all_patients, delete_patient, get_all_medical_history, get_statistics,
    get_doctor_patients, add_patient, add_medical_history, get_patient_medical_history,
    get_ai_predictions, save_prediction, delete_prediction
)
from ml_models import predict_diabetes, predict_liver, predict_cardio
from ui_styles import apply_custom_styles

# ======================================================================
# SESSION STATE INITIALIZATION
# ======================================================================

def init_session_state():
    defaults = {
        "authenticated": False,
        "username": "",
        "full_name": "",
        "user_id": None,
        "role": "",
        "login_error": ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ======================================================================
# PAGE CONFIGURATION
# ======================================================================

st.set_page_config(
    page_title="MediScan AI - Healthcare Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()

def logout_user():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.full_name = ""
    st.session_state.user_id = None
    st.session_state.role = ""
    st.rerun()

# ======================================================================
# LOGIN PAGE
# ======================================================================

def show_login_page():
    st.markdown("""
    <div class="main-header" style="text-align: center;">
        <h1>MediScan AI</h1>
        <p>Professional Healthcare Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">System Access</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Information"])
        
        with tab1:
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Sign In", use_container_width=True):
                    if username and password:
                        success, user = authenticate_user(username, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.username = user["username"]
                            st.session_state.full_name = user["full_name"]
                            st.session_state.user_id = user["id"]
                            st.session_state.role = user["role"]
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please enter username and password")
        
        with tab2:
            st.markdown("**System Information**")
            st.markdown("- AI-based disease prediction")
            st.markdown("- Patient management system")
            st.markdown("- Medical history tracking")
            st.markdown("- Professional reporting")
            
            st.markdown("---")
            st.markdown("**Default Credentials**")
            st.markdown("Admin: admin / admin123")
            st.markdown("Doctor: dr_johnson / doctor123")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ======================================================================
# ADMIN DASHBOARD
# ======================================================================

def show_admin_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>Administrator Dashboard</h1>
        <p>System Management and Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    stats = get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats.get("total_doctors", 0)}</div><div class="metric-label">Total Doctors</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats.get("total_patients", 0)}</div><div class="metric-label">Total Patients</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats.get("total_records", 0)}</div><div class="metric-label">Medical Records</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats.get("risk_cases", 0)}</div><div class="metric-label">Risk Cases</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["User Management", "Patient Records", "Medical History", "AI Predictions"])
    
    with tab1:
        st.markdown('<div class="card-title">System Users</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            users = get_all_users()
            if users:
                st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
            else: st.info("No users found")
        with col2:
            st.markdown('<div class="card-title">Add New User</div>', unsafe_allow_html=True)
            with st.form("add_user_form"):
                new_username = st.text_input("Username")
                new_fullname = st.text_input("Full Name")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["doctor", "admin"])
                if st.form_submit_button("Create User", use_container_width=True):
                    if new_username and new_fullname and new_password:
                        success, msg = add_user(new_username, new_fullname, new_password, new_role)
                        if success: st.success(msg); st.rerun()
                        else: st.error(msg)
                    else: st.warning("Please fill required fields")
    
    with tab2:
        st.markdown('<div class="card-title">All Patients</div>', unsafe_allow_html=True)
        patients = get_all_patients()
        if patients:
            df_patients = pd.DataFrame(patients)
            display_cols = ["name", "cnic", "gender", "age", "phone", "doctor_name", "created_at"]
            st.dataframe(df_patients[[c for c in display_cols if c in df_patients.columns]], use_container_width=True, hide_index=True)
            with st.expander("Delete Patient Record"):
                patient_to_delete = st.selectbox("Select Patient to Delete", [f"{p['name']} - {p['cnic']}" for p in patients])
                if st.button("Delete Patient", type="primary"):
                    p_id = [p["id"] for p in patients if f"{p['name']} - {p['cnic']}" == patient_to_delete][0]
                    if delete_patient(p_id): st.success("Patient deleted"); st.rerun()
        else: st.info("No patients found")

    with tab3:
        st.markdown('<div class="card-title">Medical History Records</div>', unsafe_allow_html=True)
        history = get_all_medical_history()
        if history:
            df_history = pd.DataFrame(history)
            display_cols = ["patient_name", "doctor_name", "disease", "diagnosis_date", "treatment"]
            st.dataframe(df_history[[c for c in display_cols if c in df_history.columns]], use_container_width=True, hide_index=True)
        else: st.info("No medical history found")

    with tab4:
        st.markdown('<div class="card-title">AI Screening Results</div>', unsafe_allow_html=True)
        predictions = get_ai_predictions()
        if predictions:
            df_pred = pd.DataFrame(predictions)
            display_cols = ["patient_name", "disease_type", "prediction_result", "confidence_score", "prediction_date"]
            st.dataframe(df_pred[[c for c in display_cols if c in df_pred.columns]], use_container_width=True, hide_index=True)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                risk_counts = df_pred["prediction_result"].value_counts()
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%', colors=['#ff6b6b', '#51cf66'])
                ax.set_title("Risk vs Normal Cases")
                st.pyplot(fig)
                plt.close()
            with col2:
                disease_counts = df_pred["disease_type"].value_counts()
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.bar(disease_counts.index, disease_counts.values, color='#1a73e8')
                ax.set_title("Predictions by Disease")
                plt.xticks(rotation=45)
                st.pyplot(fig)
                plt.close()
        else: st.info("No AI predictions found")

# ======================================================================
# DOCTOR DASHBOARD
# ======================================================================

def show_doctor_dashboard():
    st.markdown(f"""
    <div class="main-header">
        <h1>Welcome, Dr. {st.session_state.full_name}</h1>
        <p>Patient Management and AI Screening Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    my_patients = get_doctor_patients(st.session_state.user_id)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(my_patients)}</div><div class="metric-label">My Patients</div></div>', unsafe_allow_html=True)
    with col2:
        total_records = sum(len(get_patient_medical_history(p["id"])) for p in my_patients)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_records}</div><div class="metric-label">Medical Records</div></div>', unsafe_allow_html=True)
    with col3:
        predictions = get_ai_predictions()
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(predictions)}</div><div class="metric-label">AI Screenings</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["AI Screening", "Patient Management", "Medical History", "My Patients", "Reports"])
    
    with tab1:
        st.markdown('<div class="card-title">AI-Based Disease Screening</div>', unsafe_allow_html=True)
        screening_type = st.selectbox("Select Screening Type", ["Diabetes", "Liver Disease", "Cardiovascular"])
        
        patient_map = {p['name']: p['id'] for p in my_patients}
        patient_options = [""] + list(patient_map.keys())
        selected_patient_name = st.selectbox("Select Patient (Optional)", patient_options)
        
        st.markdown("---")
        
        if screening_type == "Diabetes":
            current_gender = "Female"
            if selected_patient_name:
                for p in my_patients:
                    if p['name'] == selected_patient_name:
                        current_gender = p['gender']
                        break
            
            col1, col2 = st.columns(2)
            with col1:
                if current_gender == "Male": pregnancies = 0
                else: pregnancies = st.number_input("Pregnancies", 0, 20, 0)
                glucose = st.number_input("Glucose Level", 0, 300, 120)
                bp = st.number_input("Blood Pressure", 0, 200, 80)
                skin = st.number_input("Skin Thickness", 0, 100, 20)
            with col2:
                insulin = st.number_input("Insulin", 0, 900, 80)
                bmi = st.number_input("BMI", 10.0, 60.0, 25.0)
                pedigree = st.number_input("Pedigree Function", 0.0, 3.0, 0.5)
                age = st.number_input("Age", 0, 120, 40)
            
            if st.button("Run Diabetes Screening", use_container_width=True):
                result, conf = predict_diabetes(pregnancies, glucose, bp, skin, insulin, bmi, pedigree, age)
                if result:
                    st.write(f"**Result:** {result} ({conf:.1f}%)")
                    if selected_patient_name:
                        feats = {"pregnancies": pregnancies, "glucose": glucose, "bp": bp, "skin": skin, "insulin": insulin, "bmi": bmi, "pedigree": pedigree, "age": age}
                        save_prediction(selected_patient_name, "Diabetes", result, conf, feats)

        elif screening_type == "Liver Disease":
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", 0, 120, 40)
                gender = st.selectbox("Gender", ["Male", "Female"])
                tb = st.number_input("Total Bilirubin", 0.0, 100.0, 1.0)
                db = st.number_input("Direct Bilirubin", 0.0, 50.0, 0.3)
                ap = st.number_input("Alkaline Phosphatase", 0, 2000, 80)
            with col2:
                alt = st.number_input("ALT", 0, 2000, 35)
                ast = st.number_input("AST", 0, 5000, 25)
                tp = st.number_input("Total Proteins", 0.0, 15.0, 7.0)
                alb = st.number_input("Albumin", 0.0, 10.0, 3.8)
                ag = st.number_input("A/G Ratio", 0.0, 5.0, 1.2)
            
            if st.button("Run Liver Screening", use_container_width=True):
                result, conf = predict_liver(age, gender, tb, db, ap, alt, ast, tp, alb, ag)
                if result:
                    st.write(f"**Result:** {result} ({conf:.1f}%)")
                    if selected_patient_name:
                        feats = {"age": age, "gender": gender, "tb": tb, "db": db, "ap": ap, "alt": alt, "ast": ast, "tp": tp, "alb": alb, "ag": ag}
                        save_prediction(selected_patient_name, "Liver Disease", result, conf, feats)

        else:
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", 0, 120, 45)
                gender = st.selectbox("Gender", ["Male", "Female"])
                h = st.number_input("Height (cm)", 100, 250, 170)
                w = st.number_input("Weight (kg)", 30, 200, 70)
                ap_hi = st.number_input("Systolic BP", 60, 250, 120)
            with col2:
                ap_lo = st.number_input("Diastolic BP", 40, 150, 80)
                chol = st.selectbox("Cholesterol", [1, 2, 3])
                gluc = st.selectbox("Glucose", [1, 2, 3])
                smoke = st.selectbox("Smoking", [0, 1])
                alco = st.selectbox("Alcohol", [0, 1])
                act = st.selectbox("Activity", [0, 1])
            
            if st.button("Run Cardiovascular Screening", use_container_width=True):
                result, conf = predict_cardio(age, gender, h, w, ap_hi, ap_lo, chol, gluc, smoke, alco, act)
                if result:
                    st.write(f"**Result:** {result} ({conf:.1f}%)")
                    if selected_patient_name:
                        feats = {"age": age, "gender": gender, "height": h, "weight": w, "ap_hi": ap_hi, "ap_lo": ap_lo, "chol": chol, "gluc": gluc, "smoke": smoke, "alco": alco, "active": act}
                        save_prediction(selected_patient_name, "Cardiovascular", result, conf, feats)

    with tab2:
        st.markdown('<div class="card-title">Register New Patient</div>', unsafe_allow_html=True)
        with st.form("add_patient_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name")
                cnic = st.text_input("CNIC Number")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                age = st.number_input("Age", 0, 150, 30)
            with col2:
                phone = st.text_input("Phone Number")
                address = st.text_area("Address")
            if st.form_submit_button("Register Patient", use_container_width=True):
                if name and cnic and phone:
                    success, msg = add_patient(st.session_state.user_id, name, cnic, gender, age, phone, address)
                    if success: st.toast(f"✅ {msg}")
                    else: st.error(f"❌ {msg}")
                else: st.warning("Please fill all required fields")

    with tab3:
        st.markdown('<div class="card-title">Medical History & Prescription</div>', unsafe_allow_html=True)
        if my_patients:
            patient_options = {p['name']: p['id'] for p in my_patients}
            selected_p = st.selectbox("Select Patient", [""] + list(patient_options.keys()), key="hist_p")
            
            if selected_p:
                p_id = patient_options[selected_p]
                
                # Auto-fetch latest AI result
                all_preds = get_ai_predictions()
                latest_ai = next((pr for pr in reversed(all_preds) if pr['patient_name'] == selected_p), None)
                
                obs_text = ""
                glucose_val = "N/A"
                bmi_val = "N/A"
                
                if latest_ai:
                    st.info(f"Latest AI Result: **{latest_ai['prediction_result']}** ({latest_ai['confidence_score']:.1f}%)")
                    try:
                        obs = json.loads(latest_ai['features_json'])
                        glucose_val = obs.get("glucose", "N/A")
                        bmi_val = obs.get("bmi", "N/A")
                        
                        # Highlighting Core Metrics
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown(f'<div style="background:#e8f0fe; padding:10px; border-radius:5px; text-align:center;"><b>Glucose Level</b><br><span style="font-size:20px; color:#1a73e8;">{glucose_val}</span></div>', unsafe_allow_html=True)
                        with m2: st.markdown(f'<div style="background:#e8f0fe; padding:10px; border-radius:5px; text-align:center;"><b>BMI Index</b><br><span style="font-size:20px; color:#1a73e8;">{bmi_val}</span></div>', unsafe_allow_html=True)
                        with m3: st.markdown(f'<div style="background:#e8f0fe; padding:10px; border-radius:5px; text-align:center;"><b>Prediction</b><br><span style="font-size:20px; color:#1a73e8;">{latest_ai["prediction_result"]}</span></div>', unsafe_allow_html=True)
                        
                        with st.expander("Show All Observations"):
                            col_a, col_b = st.columns(2)
                            count = 0
                            for k, v in obs.items():
                                label = k.replace('_', ' ').title()
                                obs_text += f"{label}: {v} | "
                                if count % 2 == 0: col_a.write(f"**{label}:** {v}")
                                else: col_b.write(f"**{label}:** {v}")
                                count += 1
                    except: 
                        obs_text = "N/A"
                
                with st.form("medical_history_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        disease = st.text_input("Diagnosis", value=latest_ai['disease_type'] if latest_ai else "")
                        diag_date = st.date_input("Date", value=datetime.now())
                    with col2:
                        symp = st.text_area("Symptoms (Observations)")
                        treat = st.text_area("Prescribed Treatment / Medicine")
                    
                    submitted = st.form_submit_button("Save Record")
                    if submitted:
                        if disease and symp:
                            success, msg = add_medical_history(p_id, st.session_state.user_id, disease, symp, treat, diag_date)
                            if success: st.success(msg)
                
                if st.button("🖨️ Generate Printable Prescription"):
                    printable_treat = treat.replace('\n', '<br>')
                    raw_html = f"""
                    <div style="border: 2px solid #1a73e8; padding: 30px; border-radius: 15px; background-color: #ffffff; color: #333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 800px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <!-- Header -->
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #1a73e8; padding-bottom: 15px; margin-bottom: 20px;">
                            <div style="text-align: left;">
                                <h1 style="margin: 0; color: #1a73e8; font-size: 28px;">MediScan AI CLINIC</h1>
                                <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">Dr. {st.session_state.full_name}</p>
                                <p style="margin: 2px 0 0 0; font-size: 14px; color: #666;">Specialist Physician</p>
                            </div>
                            <div style="text-align: right; color: #444;">
                                <p style="margin: 0;"><b>Date:</b> {datetime.now().strftime('%d-%m-%Y')}</p>
                                <p style="margin: 5px 0 0 0;"><b>Time:</b> {datetime.now().strftime('%I:%M %p')}</p>
                                <p style="margin: 5px 0 0 0; color: #1a73e8; font-weight: bold;">#{datetime.now().strftime('%H%M%S')}</p>
                            </div>
                        </div>

                        <!-- Patient Info Area -->
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid #1a73e8;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="width: 50%; padding: 5px 0;"><b>Patient Name:</b> {selected_p}</td>
                                    <td style="width: 50%; padding: 5px 0;"><b>Diagnosis:</b> {disease}</td>
                                </tr>
                            </table>
                        </div>

                        <!-- Observations Section -->
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #1a73e8; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-bottom: 10px;">VITAL OBSERVATIONS & AI SCREENING</h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; background: #fffbe6; padding: 10px; border-radius: 5px; border: 1px solid #ffe58f;">
                                <div style="text-align: center;"><b>Glucose:</b><br>{glucose_val} mg/dL</div>
                                <div style="text-align: center;"><b>BMI:</b><br>{bmi_val}</div>
                                <div style="text-align: center;"><b>AI Risk:</b><br>{latest_ai['prediction_result'] if latest_ai else 'N/A'}</div>
                            </div>
                            <p style="font-size: 13px; color: #555; margin-top: 10px; background: #f0f2f5; padding: 8px; border-radius: 4px;">
                                <b>Detailed Metrics:</b> {obs_text}
                            </p>
                        </div>

                        <div style="margin-bottom: 20px;">
                            <h4 style="color: #1a73e8; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-bottom: 10px;">SYMPTOMS / HISTORY</h4>
                            <p style="padding-left: 10px; font-style: italic; color: #333;">{symp if symp else 'No symptoms recorded.'}</p>
                        </div>

                        <!-- Prescription Section -->
                        <div style="margin-bottom: 40px; min-height: 200px; position: relative;">
                            <h3 style="color: #1a73e8; margin-bottom: 15px; border-bottom: 2px solid #1a73e8; width: 60px;">Rx</h3>
                            <div style="font-size: 18px; font-weight: 600; padding: 15px; line-height: 1.8; color: #000;">
                                {printable_treat if printable_treat else 'General observation and rest.'}
                            </div>
                        </div>

                        <!-- Footer -->
                        <div style="display: flex; justify-content: space-between; align-items: flex-end; padding-top: 20px; border-top: 1px solid #ddd;">
                            <div style="font-size: 12px; color: #999;">
                                System Generated Report<br>
                                MediScan AI Prediction Engine v2.0
                            </div>
                            <div style="text-align: center; border-top: 2px solid #333; width: 200px; padding-top: 5px;">
                                <b>Authorized Signature</b>
                            </div>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 15px;">
                        <p style="color: #666; font-size: 14px;">Press <b>Ctrl + P</b> to print this official medical slip</p>
                    </div>
                    """
                    prescription_html = "\n".join(line.lstrip() for line in raw_html.splitlines())
                    st.markdown(prescription_html, unsafe_allow_html=True)

        else: st.info("No patients found")

    with tab4:
        st.markdown('<div class="card-title">Patient Directory</div>', unsafe_allow_html=True)
        for p in my_patients:
            with st.expander(f"{p['name']} - {p['cnic']}"):
                st.write(f"**Age:** {p['age']} | **Gender:** {p['gender']} | **Phone:** {p['phone']}")
                st.write(f"**Address:** {p.get('address', 'N/A')}")
                hist = get_patient_medical_history(p["id"])
                if hist:
                    st.write("**Recent History:**")
                    for r in hist[:3]: st.write(f"- {r['diagnosis_date']}: {r['disease']}")
                
                st.markdown("---")
                if st.button(f"Delete {p['name']}", key=f"del_{p['id']}", type="secondary"):
                    if delete_patient(p['id']):
                        st.toast(f"Patient {p['name']} deleted")
                        st.rerun()

    with tab5:
        st.markdown('<div class="card-title">Detailed Reports & History</div>', unsafe_allow_html=True)
        rep_type = st.selectbox("Report Type", ["AI Screening History", "Patient Stats"])
        
        # Get only current doctor's patient names for filtering
        my_patient_names = {p['name'] for p in my_patients}
        
        if rep_type == "AI Screening History":
            all_predictions = get_ai_predictions()
            predictions = [r for r in all_predictions if r['patient_name'] in my_patient_names]
            if predictions:
                for res in predictions:
                    with st.expander(f"{res['patient_name']} - {res['disease_type']} ({res['prediction_result']})"):
                        st.write(f"**Date:** {res['prediction_date']}")
                        st.write(f"**Confidence:** {res['confidence_score']:.1f}%")
                        if res['features_json']:
                            try:
                                feats = json.loads(res['features_json'])
                                st.write("**Input Values used for Screening:**")
                                
                                mapping = {
                                    "age": "Age",
                                    "gender": "Gender",
                                    "tb": "Total Bilirubin",
                                    "db": "Direct Bilirubin",
                                    "ap": "Alkaline Phosphatase",
                                    "alt": "ALT (Alanine Aminotransferase)",
                                    "ast": "AST (Aspartate Aminotransferase)",
                                    "tp": "Total Proteins",
                                    "alb": "Albumin",
                                    "ag": "A/G Ratio",
                                    "pregnancies": "Pregnancies",
                                    "glucose": "Glucose",
                                    "bp": "Blood Pressure",
                                    "skin": "Skin Thickness",
                                    "insulin": "Insulin",
                                    "bmi": "BMI",
                                    "pedigree": "Pedigree Function",
                                    "height": "Height (cm)",
                                    "weight": "Weight (kg)",
                                    "ap_hi": "Systolic BP",
                                    "ap_lo": "Diastolic BP",
                                    "chol": "Cholesterol",
                                    "gluc": "Glucose Level",
                                    "smoke": "Smoking Status",
                                    "alco": "Alcohol Consumption",
                                    "active": "Physical Activity"
                                }
                                
                                col1, col2 = st.columns(2)
                                count = 0
                                for k, v in feats.items():
                                    label = mapping.get(k.lower(), k.replace('_', ' ').title())
                                    
                                    # Pretty print values
                                    if k.lower() in ["smoke", "alco", "active"]:
                                        v = "Yes" if v == 1 or v == "1" else "No"
                                    elif k.lower() in ["chol", "gluc"]:
                                        try:
                                            status_map = {1: "Normal", 2: "Above Normal", 3: "Well Above Normal"}
                                            v = status_map.get(int(v), v)
                                        except:
                                            pass
                                            
                                    if count % 2 == 0:
                                        col1.write(f"**{label}:** {v}")
                                    else:
                                        col2.write(f"**{label}:** {v}")
                                    count += 1
                            except:
                                st.write("No features recorded.")
                        
                        st.markdown("---")
                        if st.button("Delete Record", key=f"del_pred_{res['id']}", type="secondary"):
                            if delete_prediction(res['id']):
                                st.toast("Screening record deleted")
                                st.rerun()
            else: st.info("No AI screenings found for your patients")
        else:
            st.write(f"Total Patients: {len(my_patients)}")

# ======================================================================
# MAIN APPLICATION
# ======================================================================

def main():
    if not init_database():
        st.error("Database connection failed. Please check XAMPP.")
        return
    
    if not st.session_state.authenticated:
        show_login_page()
    else:
        if st.session_state.role == "admin": show_admin_dashboard()
        else: show_doctor_dashboard()
        
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**User:** {st.session_state.full_name}")
            if st.button("Logout", use_container_width=True): logout_user()

if __name__ == "__main__":
    main()