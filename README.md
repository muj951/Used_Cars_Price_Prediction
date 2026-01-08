# 🚗 Used Car Price Prediction System

An end-to-end Machine Learning project that scrapes eBay listings, cleans data using a robust pipeline, and predicts fair market value using a deployed XGBoost model.

## 📊 Project Overview
* **Goal:** Automate used car valuation to identify under/overpriced assets.
* **Accuracy:** 84.5% ($R^2$) with a Mean Absolute Error of ~$4,300.
* **Tech Stack:** Python, Selenium/BS4, SQLite, Pandas, XGBoost, Streamlit, Docker.

## 🏗️ Architecture
1. **Extraction:** Scraped 4,600+ listings from eBay using resilient retry logic.
2. **Storage:** Relational SQLite database (`listings`, `cars_cleaned`).
3. **Engineering:** Engineered "Luxury Tier" and "Depreciation Curve" features.
4. **Modeling:** Benchmarked 8 models; **XGBoost** won (3.1s training time).
5. **Deployment:** Production-ready Streamlit app with negative-price safeguards.

## 🚀 How to Run
1. Clone the repo:
   ```bash
   git clone [https://github.com/muj951/Used_Cars_Price_Prediction.git](https://github.com/muj951/Used_Cars_Price_Prediction.git)
   ```

2. Build and Run:
   ```bash
   docker-compose up --build
   ```

   