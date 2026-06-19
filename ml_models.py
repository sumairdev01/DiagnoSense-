import streamlit as st
import pickle
import numpy as np

@st.cache_resource
def load_models():
    models_dict = {}
    try:
        with open("diabetes_model.pkl", "rb") as f:
            models_dict["diabetes"] = pickle.load(f)
    except Exception as e:
        st.warning(f"Diabetes model load failed: {e}")
        models_dict["diabetes"] = None
    
    try:
        with open("liver_model.pkl", "rb") as f:
            models_dict["liver"] = pickle.load(f)
    except Exception as e:
        st.warning(f"Liver model load failed: {e}")
        models_dict["liver"] = None
    
    try:
        with open("cardio_model.pkl", "rb") as f:
            models_dict["cardio"] = pickle.load(f)
    except Exception as e:
        st.warning(f"Cardio model load failed: {e}")
        models_dict["cardio"] = None
    
    return models_dict

def predict_diabetes(pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, pedigree, age):
    models = load_models()
    if models["diabetes"] is None:
        return None, "Model not available"
    
    features = np.array([[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, pedigree, age]])
    prediction = models["diabetes"].predict(features)[0]
    
    try:
        probability = models["diabetes"].predict_proba(features)[0][1]
    except:
        probability = 0.5
    
    result = "Risk" if prediction == 1 else "Normal"
    return result, probability * 100

def predict_liver(age, gender, total_bilirubin, direct_bilirubin, alkaline_phosphatase, alt, ast, total_proteins, albumin, ag_ratio):
    models = load_models()
    if models["liver"] is None:
        return None, "Model not available"
    
    gender_num = 1 if gender == "Male" else 0
    features = np.array([[age, gender_num, total_bilirubin, direct_bilirubin, alkaline_phosphatase, alt, ast, total_proteins, albumin, ag_ratio]])
    prediction = models["liver"].predict(features)[0]
    
    try:
        probability = models["liver"].predict_proba(features)[0][1]
    except:
        probability = 0.5
    
    result = "Risk" if prediction == 1 else "Normal"
    return result, probability * 100

def predict_cardio(age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active):
    models = load_models()
    if models["cardio"] is None:
        return None, "Model not available"
    
    age_days = age * 365
    gender_num = 2 if gender == "Male" else 1
    features = np.array([[age_days, gender_num, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active]])
    prediction = models["cardio"].predict(features)[0]
    
    try:
        probability = models["cardio"].predict_proba(features)[0][1]
    except:
        probability = 0.5
    
    result = "Risk" if prediction == 1 else "Normal"
    return result, probability * 100
