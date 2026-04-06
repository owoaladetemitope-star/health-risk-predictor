import streamlit as st
import pandas as pd
import joblib
import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect("predictions.db")
c = conn.cursor()

# Create table
c.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vitamin_b12 REAL,
    iron REAL,
    bmi REAL,
    age INTEGER,
    prediction INTEGER,
    probability REAL,
    timestamp TEXT
)
""")

conn.commit()

# Load model and features
rf_model = joblib.load("rf_model.pkl")
model_features = joblib.load("model_features.pkl")

st.title("Health Risk Predictor")
st.write("Predict likelihood of numbness based on health data")

# User inputs
vitamin_b12 = st.number_input(
    "Vitamin B12 (% of RDA)", 
    min_value=0.0, max_value=500.0, value=100.0, step=10.0
)

iron = st.number_input(
    "Iron (% of RDA)", 
    min_value=0.0, max_value=500.0, value=100.0, step=10.0
)

bmi = st.number_input(
    "BMI", 
    min_value=10.0, max_value=60.0, value=25.0, step=1.0
)

age = st.number_input(
    "Age", 
    min_value=0, max_value=120, value=30, step=1
)

# Predict button
if st.button("Predict"):
    input_df = pd.DataFrame([{
        "vitamin_b12_percent_rda": vitamin_b12,
        "iron_percent_rda": iron,
        "bmi": bmi,
        "age": age
    }])

    prediction = rf_model.predict(input_df)[0]
    probability = rf_model.predict_proba(input_df)[0][1]

    # Save to database
    c.execute("""
    INSERT INTO predictions (vitamin_b12, iron, bmi, age, prediction, probability, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        vitamin_b12,
        iron,
        bmi,
        age,
        int(prediction),
        float(probability),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()

    if prediction == 1:
        st.error(f"High likelihood of numbness (Probability: {round(probability, 3)})")
        st.write("This may be associated with low vitamin B12 or iron levels.")
    else:
        st.success(f"Low likelihood of numbness (Probability: {round(probability, 3)})")
        st.write("Your inputs suggest a lower risk based on the model.")

st.subheader("Prediction History")

if st.button("Show History"):
    c.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()

    if rows:
        df_history = pd.DataFrame(rows, columns=[
            "ID", "B12", "Iron", "BMI", "Age", "Prediction", "Probability", "Time"
        ])

        # 👇 ADD THIS LINE RIGHT HERE
        df_history["Prediction"] = df_history["Prediction"].map({0: "Low", 1: "High"})

        st.dataframe(df_history)
    else:
        st.write("No history yet.")