import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 600;
        }
        
        .main-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            border: 1px solid #e0e0e0;
        }
        
        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #1a73e8;
            border-bottom: 2px solid #1a73e8;
            padding-bottom: 0.5rem;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        
        .status-success {
            background: #4caf50;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            display: inline-block;
            font-size: 0.8rem;
        }
        
        .status-warning {
            background: #ff9800;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            display: inline-block;
            font-size: 0.8rem;
        }
        
        .status-danger {
            background: #f44336;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            display: inline-block;
            font-size: 0.8rem;
        }
        
        .stButton > button {
            background: #1a73e8;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            background: #0d47a1;
            transform: translateY(-2px);
        }
    </style>
    """, unsafe_allow_html=True)
