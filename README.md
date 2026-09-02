# FoodSafe AI - Complete Setup

## Requirements
- Node.js (v18+)
- MongoDB running locally on port 27017 (mongodb://localhost:27017/foodsafe-ai)
- Python 3

## 1. Start the AI Service
Open a terminal in the `ai-service` folder.
```bash
cd ai-service
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
*(Runs on http://localhost:8000)*

## 2. Start the Backend Server
Open a new terminal in the `backend` folder.
```bash
cd backend
npm install
npm run dev
```
*(Runs on http://localhost:5000)*

## 3. Start the Frontend
Open a new terminal in the `frontend` folder.
```bash
cd frontend
npm install
npm run dev
```
*(Runs on http://localhost:5173)*

## Verification
- Navigate to http://localhost:5173
- Register a user account and login.
- Go to "Scan Food" and upload an image (or use the camera).
- View the mock AI visual safety assessment result.
- Check out your Scan history!
