# FoodSafe AI (Biryani AI Focus)

FoodSafe AI is an intelligent visual food-safety and quality assessment platform, primarily focused on **Biryani**.

---

## Biryani AI Architecture & Pipeline

```
User uploads image
        ↓
Image validation (file format, size, decoding)
        ↓
Image quality check (blur, Laplacian variance, brightness, resolution)
        ↓
Biryani identification (Is it Biryani vs other dishes/non-food)
        ↓
Biryani visual analysis (rice grain separation, saffron/golden color palette, garnish, charring/scorching)
        ↓
Food safety / visible quality analysis (visual freshness score, defect score, presentation indicators)
        ↓
Result & Serving Guidelines
```

### Scientific Safety Notice
Standard RGB photographs cannot directly detect invisible microorganisms (such as *Bacillus cereus*, *Salmonella*), toxins, or chemical residues. The Biryani AI system focuses strictly on scientifically sound optical indicators:
- Dish and food identification (Biryani classifier)
- Visible appearance and coloration (saffron, turmeric, multi-tone dum grains)
- Visible defect and anomaly detection (scorching, discoloration, excessive charring)
- Fresh garnish and presentation indicators (fried onions/birista, fresh mint/coriander leaves)
- Serving guidelines and hot-holding temperature recommendations

---

## Directory Structure

```
foodsafe-ai/
├── biryani/                      # Core Biryani AI module
│   ├── config/                  # Configuration & hyperparameters
│   ├── dataset/                 # Dataset manifests & loaders
│   ├── evaluation/              # Model evaluation scripts & metrics
│   ├── inference/               # Isolated Biryani inference engine
│   ├── models/                  # Architecture builders & weights
│   ├── preprocessing/           # Preprocessing & image quality checks
│   └── training/                # Training pipelines
├── ai-service/                  # Python Flask AI microservice
│   ├── food_analyzers/          # Biryani analyzer & adapters
│   ├── microbial/               # Microscopic microbial detector
│   └── app.py                   # Main Flask API service (port 8000)
├── backend/                     # Node.js / Express API server (port 5000)
│   ├── controllers/             # Auth, Scans, Biryani Food ID, Microbial
│   ├── models/                  # MongoDB Mongoose schemas
│   ├── routes/                  # Express API routes
│   └── server.js                # Express entrypoint
└── frontend/                    # Vite + React web interface (port 5173)
    └── src/                     # React components, pages, context
```

---

## Requirements
- Node.js (v18+)
- MongoDB running locally or MongoDB Atlas (configured in `backend/.env`)
- Python 3.10+

---

## Getting Started

### 1. Start the AI Service
Open a terminal in `ai-service`:
```bash
cd ai-service
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
*(Runs on http://localhost:8000)*

### 2. Start the Backend Server
Open a terminal in `backend`:
```bash
cd backend
npm install
npm run dev
```
*(Runs on http://localhost:5000)*

### 3. Start the Frontend
Open a terminal in `frontend`:
```bash
cd frontend
npm install
npm run dev
```
*(Runs on http://localhost:5173)*

---

## Verification & Testing
1. Navigate to `http://localhost:5173`.
2. Register an account and login.
3. Use **Scan Food** or **Biryani Identifier** to upload a Biryani image.
4. Verify the Biryani identification and visible quality assessment result.
