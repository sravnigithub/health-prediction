# Health Prediction App

A modern, full-stack web application designed to manage patient health records and predict whether a patient requires medical attention based on key blood metrics: glucose, haemoglobin, and cholesterol.

The application leverages a fast and robust **FastAPI** backend, a persistent **SQLite** database managed with **SQLAlchemy**, a **Random Forest Classifier** trained on realistic synthetic medical data, and a sleek, interactive **Glassmorphism UI** for seamless user interaction.

---

## 🌟 Key Features

*   **Complete CRUD Capabilities**: Create, read, update, and delete patient records dynamically without full page reloads.
*   **Hybrid Predictor Logic**:
    1.  **Clinical Reference Ranges**: Immediate clinical boundary validation (fast-gate rule check) for out-of-range metrics.
    2.  **Machine Learning Classifier**: A trained Random Forest Classifier predicts status with confidence levels when blood metrics are within borderline levels.
*   **Robust Data Validation**: Form inputs are validated on the client and server side. For example, Date of Birth (DOB) is strictly restricted to the present or past.
*   **Modern Glassmorphism UI**: Beautiful, interactive interface featuring subtle micro-animations, glass containers, responsive design, and status toast notifications.
*   **Automatic Model Training**: The machine learning model is trained automatically on startup if a pre-trained model file (`model.pkl`) is not found.

---

## 📁 Project Structure

```text
HealthPrediction/
├── database.py          # SQLAlchemy engine, session maker, and DB dependency
├── models.py            # SQLite schemas (SQLAlchemy) & validation schemas (Pydantic)
├── main.py              # FastAPI app setup, lifespan events, and REST API endpoints
├── ml_predictor.py      # Random Forest model, dataset generator, and rule logic
├── model.pkl            # Persisted machine learning model (generated after first run)
├── requirements.txt     # Python package dependencies
├── templates/
│   └── index.html       # Single-page dashboard UI (HTML5 semantic layout)
└── static/
    ├── style.css        # Premium styling with glassmorphism, CSS variables, and layout rules
    └── script.js        # Client-side API integration, form handling, and interactive DOM logic
```

---

## 🔬 Clinical Reference Ranges & ML Predictor

The prediction pipeline combines clinical guidelines with a classifier:

### 1. Clinical Hard Rules (Fast-Gate)
If any patient measurement lies outside normal medical reference ranges, they are immediately flagged as **"Requires Medical Attention"**:
*   **Glucose**: Normal range is `60.0 – 149.9 mg/dL`. (Values $\ge 150.0$ represent diabetic range, and $< 60.0$ represent hypoglycemia).
*   **Cholesterol**: Normal range is `60.0 – 199.9 mg/dL`. (Values $\ge 200.0$ indicate hypercholesterolemia, and $< 60.0$ indicate critical low cholesterol).
*   **Haemoglobin**: Normal range is `12.0 – 17.5 g/dL`. (Values $< 12.0$ indicate anemia, and $> 17.5$ indicate erythrocytosis).

### 2. Machine Learning Model
If all parameters fall within their normal boundaries, the values are fed into a **Random Forest Classifier** (trained on 1,000 synthetic patient records using a 5-fold cross-validation strategy) to analyze multi-variable risks and output either:
*   `Normal`
*   `Requires Medical Attention`

---

## 🚀 Setup & Running Locally

### Prerequisites
Make sure you have **Python 3.10+** installed on your system.

### 1. Clone & Navigate
```bash
git clone <your-repository-url>
cd HealthPrediction
```

### 2. Create and Activate a Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Application
Run the dev server using Uvicorn:
```bash
uvicorn main:app --reload
```
On startup, `ml_predictor.py` will generate the training dataset, fit the Random Forest model, output accuracy metrics, and persist it to `model.pkl` if not already present.

### 5. Access the Web Dashboard
Open your browser and navigate to:
```text
http://127.0.0.1:8000
```

---

## 📡 REST API Reference

### Patient Endpoints

#### 1. Get All Patients
*   **Method**: `GET`
*   **Route**: `/api/patients`
*   **Query Parameters**:
    *   `skip` (default: 0)
    *   `limit` (default: 100)
*   **Response**: `200 OK` (list of patients)

#### 2. Create a Patient
*   **Method**: `POST`
*   **Route**: `/api/patients`
*   **Request Body**:
    ```json
    {
      "full_name": "Jane Doe",
      "dob": "1995-08-25",
      "email": "jane.doe@example.com",
      "glucose": 95.5,
      "haemoglobin": 14.2,
      "cholesterol": 180.0
    }
    ```
*   **Response**: `200 OK` (includes generated `id` and prediction `remarks`)

#### 3. Update Patient Records
*   **Method**: `PUT`
*   **Route**: `/api/patients/{patient_id}`
*   **Request Body**: Same structure as create.
*   **Response**: `200 OK` (re-calculates status remarks and returns updated patient record)

#### 4. Delete Patient
*   **Method**: `DELETE`
*   **Route**: `/api/patients/{patient_id}`
*   **Response**: `200 OK` -> `{"message": "Patient deleted successfully"}`

---

## 🛠️ Built With

*   **FastAPI**: Modern, fast web framework for building APIs.
*   **SQLAlchemy**: Object-Relational Mapper (ORM) for Python.
*   **SQLite**: Lightweight disk-based database.
*   **Scikit-Learn**: Machine learning library used for training the Random Forest classifier.
*   **Pandas & NumPy**: Data structures and numerical computation.
*   **Jinja2**: HTML templating engine.
*   **Vanilla CSS & JS**: Modern design with glassmorphism effects and modular client-side logic.
