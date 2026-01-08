import streamlit as st
import pandas as pd
import joblib
import os
import numpy as np

# --- PATHS --- WHERE FILES ARE STORES
BASE_DIR = os.getcwd()
MODEL_PATH = os.path.join(BASE_DIR, "models", "car_price_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")
ARTIFACTS_PATH = os.path.join(BASE_DIR, "models", "project_artifacts.pkl")

# --- CONFIGURATIONS ---
st.set_page_config(page_title="Car Price AI", page_icon="🚗", layout="centered")

# --- LOAD DATA ---
@st.cache_resource
def load_components():
    if not os.path.exists(MODEL_PATH):
        st.error(f"File not found: {MODEL_PATH}")
        st.stop()
        
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    artifacts = joblib.load(ARTIFACTS_PATH)
    
    return model, scaler, artifacts

# Load everything once
model, scaler, artifacts = load_components()

# "Knowledge Base" from artifacts
brand_to_models_dict = artifacts['brand_to_models']
brand_map = artifacts['brand_map']
model_map = artifacts['model_map']
tier_map = artifacts['tier_map']
rarity_map = artifacts['rarity_map']
feature_order = artifacts['features']

# --- APP UI ---
st.title("🚗 Auto Price Estimator")
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.header("1. Vehicle")
    
    # A. BRAND SELECTION
    sorted_brands = sorted(list(brand_to_models_dict.keys()))
    selected_brand = st.selectbox("Brand", sorted_brands)
    
    # B. MODEL SELECTION (Dynamic!)
    # Only show models that belong to the selected brand
    available_models = sorted(brand_to_models_dict.get(selected_brand, []))
    selected_model = st.selectbox("Model", available_models)
    
with col2:
    st.header("2. Details")
    selected_year = st.number_input("Year", min_value=2000, max_value=2025, value=2015)
    selected_mileage = st.number_input("Mileage", min_value=0, value=50000, step=1000)
    
    # C. AUCTION
    listing_type = st.radio("Listing Type", ["Buy It Now", "Auction"], index=0)
    is_auction = 1 if listing_type == "Auction" else 0

st.write("---")

# --- PREDICTION LOGIC ---
if st.button("💰 Estimate Value", type="primary", use_container_width=True):

    # Feature: car_age
    car_age = 2025 - selected_year
    
    # Feature: miles_per_year
    # Avoid division by zero for 2025 cars
    age_for_calc = car_age if car_age > 0 else 1
    miles_per_year = selected_mileage / age_for_calc
    
    # Feature: brand_encoded & model_encoded
    brand_id = brand_map.get(selected_brand, -1) 
    model_id = model_map.get(selected_model, -1)
    
    # Feature: brand_tier
    brand_tier = tier_map.get(selected_brand, 1)
    
    # Feature: model_rarity
    # Look it up by ID! If unknown, use a median value : 50
    model_rarity = rarity_map.get(model_id, 50)

    # 2. CREATE DATAFRAME
    input_data = pd.DataFrame([{
        'car_age': car_age,
        'mileage': selected_mileage,
        'miles_per_year': miles_per_year,
        'brand_tier': brand_tier,
        'model_rarity': model_rarity,
        'brand_encoded': brand_id,
        'model_encoded': model_id,
        'is_auction': is_auction
    }])
    
    input_data = input_data[feature_order]

    try:
        # 3. SCALE
        input_scaled = scaler.transform(input_data)
        
        # 4. PREDICT
        price = model.predict(input_scaled)[0]
        final_price = max(500, price)  # Prevent negative predictions

        # 5. DISPLAY
        st.balloons()
        st.metric(label="Estimated Market Value", value=f"${final_price:,.2f}")

    except Exception as e:
        st.error(f"An error occurred during prediction: {e}")