import pandas as pd
import json
import os
import streamlit as st
import pandas as pd
import joblib
import json
import os

# --- PATHS ---
BASE_DIR = r"F:\Master\Web Scrapping\Scrapping\venv_new\Ebay_Project"
CSV_PATH = os.path.join(BASE_DIR, "data", "cleaned_car_data.csv")
MAPPINGS_PATH = os.path.join(BASE_DIR, "models", "mappings.json")

print(" Reading Data to build Linked Lists...")
df = pd.read_csv(CSV_PATH)

# 1. Create Basic Mappings (ID <-> Name)
brand_map_df = df[['brand_encoded', 'brand']].drop_duplicates().sort_values('brand')
brand_mapping = dict(zip(brand_map_df['brand_encoded'].astype(str), brand_map_df['brand']))

model_col = 'clean_model' if 'clean_model' in df.columns else 'title'
model_map_df = df[['model_encoded', model_col]].drop_duplicates().sort_values(model_col)
model_mapping = dict(zip(model_map_df['model_encoded'].astype(str), model_map_df[model_col]))

# 2. CREATE THE LINK (Brand -> List of Models)
# This dictionary will look like: {'BMW': ['328i', 'X5'], 'Toyota': ['Camry', 'Corolla']}
brand_to_models = {}

# Get the list of brand names
brands = df['brand'].unique()

for b in brands:
    # Find all models associated with this specific brand
    models = df[df['brand'] == b][model_col].unique().tolist()
    # Sort them alphabetically
    brand_to_models[b] = sorted(models)

# 3. Save Everything
full_mappings = {
    "brand_mapping": brand_mapping,
    "model_mapping": model_mapping,
    "brand_to_models": brand_to_models  
}

with open(MAPPINGS_PATH, "w") as f:
    json.dump(full_mappings, f)

print(" Success! Linked 'Brand -> Model' mapping saved.")

# --- PATHS ---
BASE_DIR = r"F:\Master\Web Scrapping\Scrapping\venv_new\Ebay_Project"
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "car_price_model.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
MAPPINGS_PATH = os.path.join(MODELS_DIR, "mappings.json")
CONFIG_PATH = os.path.join(MODELS_DIR, "feature_config.json")

# --- CONFIG ---
st.set_page_config(page_title="Car Price AI", page_icon="🚗", layout="centered")

# --- LOAD DATA ---
@st.cache_resource
def load_data():
    if not os.path.exists(MODEL_PATH):
        st.error("Model not found. Please check your paths.")
        st.stop()
        
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    
    with open(MAPPINGS_PATH, "r") as f:
        mappings = json.load(f)
        
    # Load config to know what the model expects
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            feature_names = config['features']
    else:
        # Fallback
        feature_names = ['year','mileage','model_encoded','brand_encoded','is_auction']
            
    return model, scaler, mappings, feature_names

model, scaler, all_mappings, feature_names = load_data()

# --- PREPARE DROPDOWNS ---
# 1. Get the Brand Map (Name -> ID)
brand_map_name_to_id = {v: int(k) for k, v in all_mappings['brand_mapping'].items()}
sorted_brands = sorted(brand_map_name_to_id.keys())

# 2. Get the Model Map (Name -> ID)
model_map_name_to_id = {v: int(k) for k, v in all_mappings['model_mapping'].items()}

# 3. Get the Linked List (Brand -> [Models])
brand_to_models_dict = all_mappings.get("brand_to_models", {})

# --- APP UI ---
st.title("🚗 Auto Price Estimator")
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.header("1. Vehicle")
    
    # A. BRAND SELECTION
    selected_brand = st.selectbox("Brand", sorted_brands)
    
    # B. MODEL SELECTION (Dynamic!) 🔗
    # Only show models that belong to the selected brand
    available_models = brand_to_models_dict.get(selected_brand, [])
    
    # Safety: If list is empty (rare error), fall back to full list
    if not available_models:
        available_models = sorted(model_map_name_to_id.keys())
        
    selected_model = st.selectbox("Model", available_models)
    
with col2:
    st.header("2. Details")
    selected_year = st.number_input("Year", min_value=1990, max_value=2025, value=2015)
    selected_mileage = st.number_input("Mileage", min_value=0, value=50000, step=1000)
    
    # Ask about Auction 
    listing_type = st.radio("Listing Type", ["Buy It Now", "Auction"], index=0)
    is_auction = 1 if listing_type == "Auction" else 0

st.write("---")

# --- PREDICTION ---
if st.button("💰 Estimate Value", type="primary", use_container_width=True):
    
    brand_id = brand_map_name_to_id[selected_brand]
    model_id = model_map_name_to_id[selected_model]
    
    # 2. Build Input
    # construct the dictionary with the fields
    input_dict = {
        'year': [selected_year],
        'mileage': [selected_mileage],
        'model_encoded': [model_id],
        'brand_encoded': [brand_id],
        'is_auction': [is_auction]
    }
    
    # 4. Create DataFrame & Order Correctly
    input_df = pd.DataFrame(input_dict)
    
    # 5. Predict
    input_scaled = scaler.transform(input_df)
    price = model.predict(input_scaled)[0]
    
    final_price = max(500, price)
    # 6. Display
    st.balloons()
    st.metric(label="Estimated Market Value", value=f"${final_price:,.2f}")
    
    if is_auction:
        st.info(" Price reflects Auction Starting Price.")