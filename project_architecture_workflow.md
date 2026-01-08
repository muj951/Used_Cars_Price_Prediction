# 🏗️ Project Architecture & Workflow

## 1. High-Level Overview
This project follows a standard **End-to-End Data Science Pipeline**, moving from raw unstructured web data to a deployed Machine Learning application.

The system is designed to be modular:
1.  **Extraction Layer:** Handles web scraping and raw data collection.
2.  **Storage Layer:** Persists raw data in a relational database.
3.  **Processing Layer:** Cleans text and engineers features.
4.  **Intelligence Layer:** Trains and optimizes the LightGBM model.
5.  **Application Layer:** Serves predictions via a Dockerized Web UI.

---

## 2. System Architecture Diagram

```mermaid
graph TD
    %% Define Styles
    classDef storage fill:#f9f,stroke:#333,stroke-width:2px;
    classDef process fill:#bbf,stroke:#333,stroke-width:2px;
    classDef script fill:#cfc,stroke:#333,stroke-width:2px;
    classDef user fill:#ff9,stroke:#333,stroke-width:2px;

    %% Nodes
    User([ Start]) -->|Trigger| Scraper[ Web Scraper Script]
    
    subgraph "Phase 1: Extraction & Storage"
        Scraper -->|Requests + BS4| HTML[📄 Raw HTML Files]
        HTML -->|Parse| RawCSV[( Raw CSV)]
        RawCSV -->|Ingest| DB[( SQLite Database)]
    end

    subgraph "Phase 2: Cleaning & Engineering"
        DB -->|Load| CleanScript[ Cleaning & Preprocessing]
        CleanScript -->|Regex & Feature Eng| ProcessedData[( Cleaned Data)]
    end

    subgraph "Phase 3: Modeling"
        ProcessedData -->|Train| Trainer[ Model Training Script]
        Trainer -->|XGBoost / LightGBM| ModelFile[ car_price_model.pkl]
        Trainer -->|Scaler| ScalerFile[ scaler.pkl]
    end

    subgraph "Phase 4: Deployment"
        ModelFile & ScalerFile --> App[ Streamlit App]
        App --> Docker[ Docker Container]
    end

    %% Final User Interaction
    EndUser([ End User]) -->|Browser| Docker
    Docker -->|Prediction| EndUser

    %% Apply Styles
    class DB,RawCSV,ProcessedData,ModelFile,ScalerFile storage;
    class Scraper,CleanScript,Trainer,App process;
    class User,EndUser user;