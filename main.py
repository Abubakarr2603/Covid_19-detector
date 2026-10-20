from fastapi import FastAPI, File, UploadFile
import uvicorn
import cv2
import numpy as np
import joblib

# 1. Initialize the FastAPI app
app = FastAPI(title="COVID-19 X-Ray Classifier API")

# 2. Load the trained XGBoost model and StandardScaler
model = joblib.load('covid_xgboost_model.joblib')
scaler = joblib.load('covid_scaler.joblib')

@app.post("/predict")
async def predict_xray(file: UploadFile = File(...)):
    # Read the raw image bytes sent from Streamlit
    contents = await file.read()
    
    # Convert raw bytes into a NumPy array, then decode into a grayscale OpenCV image
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        return {"error": "Invalid image file provided."}
    
    # Preprocess the image exactly like our Jupyter Notebook training loop
    img_resized = cv2.resize(img, (64, 64))
    
    # Flatten and reshape to (1, 4096) because Scikit-Learn/XGBoost expects a 2D array for predictions
    img_flattened = img_resized.flatten().reshape(1, -1) 
    
    # Scale the pixel values using our saved scaler
    img_scaled = scaler.transform(img_flattened)
    
    # Make the prediction (0 = Normal, 1 = COVID)
    prediction = model.predict(img_scaled)[0]
    
    # Map the numerical output to a human-readable string
    result = "COVID-19 Detected" if prediction == 1 else "Normal / Healthy"
    
    return {
        "filename": file.filename, 
        "prediction": result
    }

# For local testing
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)