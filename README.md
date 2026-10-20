# 🫁 COVID-19 Chest X-Ray Diagnostic Portal

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103.0-009688.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.27.0-FF4B4B.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-1.7.6-F37626.svg)
![Three.js](https://img.shields.io/badge/Three.js-WebGL-black.svg)

## 📌 Overview
This project is an end-to-end machine learning web application designed to classify COVID-19 infections from chest X-ray images. It transitions a standard tabular classification task into a modern, production-ready application using a decoupled backend/frontend architecture. 

The system features a **FastAPI REST API** serving an optimized **XGBoost** model, paired with a custom-styled **Streamlit & Three.js** frontend that visualizes the predictions using a dynamic, interactive 3D anatomical lung model.

## 🏗️ System Architecture
1. **Machine Learning Model:** XGBoost classifier trained on 4,096 flattened pixel features (64x64 grayscale).
2. **Backend (FastAPI):** Handles image uploads, applies `StandardScaler` transformations, and returns JSON predictions.
3. **Frontend (Streamlit + JS/CSS):** A glassmorphism-styled UI with an embedded `Three.js` canvas. The 3D lung model dynamically changes color (Neon Green = Normal, Red = COVID-19) based on the API response.
4. **Deployment:** Dockerized and hosted on an Ubuntu Linux Virtual Private Server.

## 🧰 Tech Stack
* **Data Science & ML:** Python, Pandas, OpenCV, Scikit-Learn, XGBoost, Joblib
* **Backend:** FastAPI, Uvicorn, Pydantic
* **Frontend:** Streamlit, HTML/CSS, Three.js (WebGL)
* **Infrastructure:** Docker, Docker Compose, Linux VPS (Oracle Cloud)

## 📊 Model Performance
Multiple algorithms were benchmarked on the Kaggle COVID-19 Radiography Database. **XGBoost** was selected for production due to its optimal balance of high recall and overall accuracy.

| Model | Accuracy | COVID Recall | COVID Precision | COVID F1-Score |
| :--- | :--- | :--- | :--- | :--- |
| **XGBoost (Deployed)** | **94.75%** | **89.49%** | **90.36%** | **89.92%** |
| Gradient Boosting (Hist) | 94.06% | 84.51% | 92.16% | 88.17% |
| Random Forest | 91.96% | 83.54% | 85.43% | 84.48% |
| Support Vector Machine | 91.60% | 90.73% | 79.90% | 84.97% |
| Logistic Regression | 79.51% | 69.71% | 59.22% | 64.04% |

## 💻 Local Development Setup

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/covid-diagnostic-portal.git](https://github.com/yourusername/covid-diagnostic-portal.git)
cd covid-diagnostic-portal
```

**2. Create a virtual environment & install dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Run the FastAPI Backend (Port 8000)**
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**4. Run the Streamlit Frontend (Port 8501)**
Open a new terminal window and run:
```bash
streamlit run app_3.py
```

## 🐳 Docker Deployment (Linux VPS)
For production deployment on an Ubuntu server, use Docker Compose to spin up both the frontend and backend simultaneously.

**1. Build and run the containers in detached mode:**
```bash
docker-compose up -d --build
```

**2. Check container logs:**
```bash
docker-compose logs -f
```

## ⚠️ Disclaimer
This application is a research prototype and portfolio project built for educational purposes. It is **not** intended for use in actual clinical diagnosis. All medical imaging predictions should be verified by a certified healthcare professional.