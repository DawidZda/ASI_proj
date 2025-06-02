import streamlit as st
import requests
import pandas as pd
import json
import os

# Set page title and description
st.title("Income Prediction App")
st.markdown("Predict if a person's income exceeds $50K per year based on census data.")

# Define categorical options based on the dataset
workclass_options = ["Private", "Self-emp-not-inc", "Self-emp-inc", "Federal-gov", 
                    "Local-gov", "State-gov", "Without-pay", "Never-worked"]

education_options = ["Bachelors", "Some-college", "11th", "HS-grad", "Prof-school", 
                    "Assoc-acdm", "Assoc-voc", "9th", "7th-8th", "12th", "Masters", 
                    "1st-4th", "10th", "Doctorate", "5th-6th", "Preschool"]

marital_status_options = ["Married-civ-spouse", "Divorced", "Never-married", 
                        "Separated", "Widowed", "Married-spouse-absent", "Married-AF-spouse"]

occupation_options = ["Tech-support", "Craft-repair", "Other-service", "Sales", 
                    "Exec-managerial", "Prof-specialty", "Handlers-cleaners", 
                    "Machine-op-inspct", "Adm-clerical", "Farming-fishing", 
                    "Transport-moving", "Priv-house-serv", "Protective-serv", "Armed-Forces"]

relationship_options = ["Wife", "Own-child", "Husband", "Not-in-family", 
                        "Other-relative", "Unmarried"]

race_options = ["White", "Asian-Pac-Islander", "Amer-Indian-Eskimo", "Other", "Black"]

sex_options = ["Female", "Male"]

country_options = [
    "United-States", "Cambodia", "England", "Puerto-Rico", "Canada", "Germany", 
    "Outlying-US(Guam-USVI-etc)", "India", "Japan", "Greece", "South", "China", 
    "Cuba", "Iran", "Honduras", "Philippines", "Italy", "Poland", "Jamaica", 
    "Vietnam", "Mexico", "Portugal", "Ireland", "France", "Dominican-Republic", 
    "Laos", "Ecuador", "Taiwan", "Haiti", "Columbia", "Hungary", "Guatemala", 
    "Nicaragua", "Scotland", "Thailand", "Yugoslavia", "El-Salvador", "Trinadad&Tobago", 
    "Peru", "Hong", "Holand-Netherlands"
]

# Create a form for user inputs
with st.form("prediction_form"):
    # Create two columns for a better layout
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", min_value=16, max_value=100, value=29)
        workclass = st.selectbox("Work Class", options=workclass_options, index=0)
        education = st.selectbox("Education", options=education_options, index=0)
        marital_status = st.selectbox("Marital Status", options=marital_status_options, index=0)
        occupation = st.selectbox("Occupation", options=occupation_options, index=4)  # Default to Exec-managerial

    with col2:
        relationship = st.selectbox("Relationship", options=relationship_options, index=2)  # Default to Husband
        race = st.selectbox("Race", options=race_options, index=0)  # Default to White
        sex = st.selectbox("Sex", options=sex_options, index=1)  # Default to Male
        hours_per_week = st.number_input("Hours per Week", min_value=1, max_value=168, value=40)
        country_of_birth = st.selectbox("Country of Birth", options=country_options, index=0)  # Default to United-States

    # Submit button
    submit_button = st.form_submit_button("Predict Income")

# Process the form submission
if submit_button:
    # Create input data for the API
    input_data = {
        "age": age,
        "workclass": workclass,
        "education": education,
        "marital_status": marital_status,
        "occupation": occupation,
        "relationship": relationship,
        "race": race,
        "sex": sex,
        "hours_per_week": hours_per_week,
        "country_of_birth": country_of_birth
    }
    
    # Display the input data
    st.subheader("Input Data")
    st.write(input_data)
    
    try:
        # Get API URL from environment variable or use default
        API_URL = os.environ.get("API_URL", "http://localhost:8000")
        
        # Make API call to the FastAPI endpoint
        response = requests.post(f"{API_URL}/income/predict", json=input_data)
        
        # Handle the response
        if response.status_code == 200:
            result = response.json()
            
            # Create an expander for the result details
            with st.expander("Prediction Result", expanded=True):
                # Show prediction outcome with appropriate styling
                if result["high_income"]:
                    st.success("Income Prediction: **>$50K per year**")
                else:
                    st.info("Income Prediction: **≤$50K per year**")
                
                # Show probability
                probability = result["probability"] * 100
                st.metric("Probability of High Income", f"{probability:.1f}%")
                
                # Show probability gauge
                st.progress(result["probability"])
                
                # Add some interpretation
                if result["high_income"]:
                    st.markdown(f"The model predicts with {probability:.1f}% confidence that this person earns **more than $50K per year**.")
                else:
                    st.markdown(f"The model predicts with {(100-probability):.1f}% confidence that this person earns **$50K or less per year**.")
        else:
            st.error(f"Error: {response.status_code}")
            st.json(response.json())
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("Make sure the FastAPI server is running at http://localhost:8000")

# Add information about the model
with st.sidebar:
    st.header("About the Model")
    st.markdown("""
    This application uses a machine learning model trained on census data to predict whether 
    a person's income exceeds $50,000 per year based on various demographic and employment factors.
    
    The model was trained using AutoGluon, a powerful AutoML framework, and achieves an accuracy 
    of approximately 82.3% on test data.
    
    **Key Features:**
    - Age
    - Work Class
    - Education Level
    - Marital Status
    - Occupation
    - Relationship Status
    - Race
    - Sex
    - Working Hours
    - Country of Birth
    """)
    
    st.divider()
    
    st.markdown("**To use the app:**")
    st.markdown("1. Fill out the form with the person's information")
    st.markdown("2. Click 'Predict Income'")
    st.markdown("3. View the prediction result")

# Add footer
st.markdown("---")
st.markdown("Income Prediction App | ASI Project")