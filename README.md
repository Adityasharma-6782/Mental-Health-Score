# 🧠 Mental Health Score Predictor

A full-stack machine learning web application that predicts a mental health score based on student behavior, daily habits, and social media usage. The project pairs a responsive frontend form with a FastAPI backend and a trained scikit-learn model to return a real-time score for any given input.

**🔗 Live Demo:** [mental-health-score-1-e4ui.onrender.com](https://mental-health-score-1-e4ui.onrender.com)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> ⚠️ **Disclaimer:** This project is a data-science/portfolio demonstration only. It is **not** a validated clinical or diagnostic tool, and its output should never be used as a substitute for professional mental health assessment or advice. If you or someone you know is struggling, please reach out to a licensed mental health professional or a crisis helpline.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Model Details](#model-details)
- [Screenshots](#screenshots)
- [Roadmap](#roadmap)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project demonstrates an end-to-end machine learning deployment: from raw survey data to a trained model to a live, interactive web app. Users enter details such as age, gender, country, academic level, platform usage, study hours, sleep, physical activity, and stress level, and the backend returns a predicted mental health score based on patterns learned from a real dataset of student social media habits.

It's designed as a learning/portfolio project to showcase:
- Data cleaning and feature engineering with `pandas`
- Model training and evaluation with `scikit-learn`
- Serving predictions via a `FastAPI` REST endpoint
- Connecting a plain HTML/CSS/JS frontend to a live ML backend
- Deploying a full-stack ML app to the cloud (Render)

## Features

- 📋 Interactive prediction form with client-side input validation
- ⚡ Real-time score output with visual result feedback
- 🔌 FastAPI-based REST API backend with automatic OpenAPI docs (`/docs`)
- 🤖 Machine learning model integration using a trained scikit-learn pipeline
- 📱 Responsive UI that works across desktop and mobile screens
- ☁️ Live, publicly deployed instance for instant testing

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI, Uvicorn |
| Machine Learning | scikit-learn, pandas, joblib |
| Deployment | Render |

## Project Structure

```
Mental Health/
├── index.html                                     # Main frontend page with the prediction form and result UI
├── style.css                                       # Styles for layout, form elements, and result display
├── script.js                                       # Handles form submission, validation, and API communication
├── main.py                                         # FastAPI server and prediction endpoint
├── Mental_Health_Model.ipynb                       # Notebook used for model development and experimentation
├── Student Social Media And Mental Health Impact.csv  # Dataset used for training and evaluation
├── requirements.txt                                # Python dependencies required to run the app
└── Mental_Health_Model.pkl                         # Trained model file used by the backend
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip
- Git

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Mental Health"
   ```

2. **Create and activate a virtual environment**

   macOS/Linux:
   ```bash
   python -m venv myenv
   source myenv/bin/activate
   ```

   Windows:
   ```bash
   python -m venv myenv
   myenv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### 1. Start the backend

```bash
uvicorn main:app --reload
```

The API will be available at:
- Base URL: `http://127.0.0.1:8000`
- Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`
- Alternative docs (ReDoc): `http://127.0.0.1:8000/redoc`

### 2. Open the frontend

Open `index.html` directly in a browser, or serve it through a local web server (recommended, to avoid CORS/file-path issues):

```bash
python -m http.server 5500
```

Then visit `http://127.0.0.1:5500`.

> **Note:** Make sure `script.js` points to your running backend URL (`http://127.0.0.1:8000` for local development, or the deployed Render URL in production).

## API Reference

### `POST /predict`

Predicts a mental health score from the supplied user attributes.

**Request Headers**
```
Content-Type: application/json
```

**Request Body**

| Field | Type | Example | Description |
|---|---|---|---|
| `Age` | int | `21` | User's age |
| `Gender` | string | `"Female"` | User's gender |
| `Country` | string | `"India"` | User's country |
| `Academic_Level` | string | `"Undergraduate"` | Current level of study |
| `Most_Used_Platform` | string | `"Instagram"` | Primary social media platform |
| `Purpose_Of_Use` | string | `"Education"` | Main reason for social media use |
| `Avg_Daily_Usage_Hours` | float | `4.5` | Average daily social media usage (hours) |
| `Daily_Unlocks` | int | `60` | Average number of phone unlocks per day |
| `Study_Hours` | float | `3` | Average daily study time (hours) |
| `Physical_Activity_Hours` | float | `1.5` | Average daily physical activity (hours) |
| `Sleep_Hours_Per_Night` | float | `7` | Average nightly sleep (hours) |
| `Stress_Level` | string | `"Medium"` | Self-reported stress level (`Low` / `Medium` / `High`) |

**Example Request**
```json
{
  "Age": 21,
  "Gender": "Female",
  "Country": "India",
  "Academic_Level": "Undergraduate",
  "Most_Used_Platform": "Instagram",
  "Purpose_Of_Use": "Education",
  "Avg_Daily_Usage_Hours": 4.5,
  "Daily_Unlocks": 60,
  "Study_Hours": 3,
  "Physical_Activity_Hours": 1.5,
  "Sleep_Hours_Per_Night": 7,
  "Stress_Level": "Medium"
}
```

**Example Response**
```json
{
  "predicted_mental_health_score": 6.84
}
```

**Example cURL call**
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Age": 21,
    "Gender": "Female",
    "Country": "India",
    "Academic_Level": "Undergraduate",
    "Most_Used_Platform": "Instagram",
    "Purpose_Of_Use": "Education",
    "Avg_Daily_Usage_Hours": 4.5,
    "Daily_Unlocks": 60,
    "Study_Hours": 3,
    "Physical_Activity_Hours": 1.5,
    "Sleep_Hours_Per_Night": 7,
    "Stress_Level": "Medium"
  }'
```

**Error Responses**

| Status Code | Meaning |
|---|---|
| `422 Unprocessable Entity` | Missing or invalid field(s) in the request body |
| `500 Internal Server Error` | Model failed to load or generate a prediction |

## Model Details

- **Training data:** `Student Social Media And Mental Health Impact.csv` — survey data covering student demographics, social media habits, and self-reported mental health indicators.
- **Pipeline:** Preprocessing (encoding categorical features, scaling numeric features) + a scikit-learn regression model, serialized with `joblib` as `Mental_Health_Model.pkl`.
- **Development notebook:** `Mental_Health_Model.ipynb` contains the full data exploration, cleaning, feature engineering, training, and evaluation process.
- **Output:** A continuous `predicted_mental_health_score` value.

> 💡 **Suggestion:** Consider adding your model's evaluation metrics here (e.g., R², MAE, RMSE) once you have finalized numbers, so visitors can judge the model's real-world reliability at a glance.

## Screenshots

> <img width="887" height="1163" alt="image" src="https://github.com/user-attachments/assets/d82085d1-0a4b-4139-be31-e9c66a22fc45" />



## Roadmap

- [ ] Add model evaluation metrics (R², MAE) to this README
- [ ] Add unit tests for the FastAPI endpoint
- [ ] Add input sanitization/validation with Pydantic models on the backend
- [ ] Add a `/health` endpoint for uptime monitoring
- [ ] Containerize with Docker for easier local setup and deployment
- [ ] Add CI (GitHub Actions) to lint and test on every push

## Limitations

- The model is trained on a specific survey dataset and may not generalize well to populations outside that sample (e.g., different age groups, countries, or cultures).
- Self-reported survey data can carry inherent biases.
- The "mental health score" is a data-driven estimate, not a clinical measurement, and carries no diagnostic validity.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Please open an issue first for major changes to discuss what you'd like to change.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

**If you found this project helpful, consider giving it a ⭐ on GitHub!**
