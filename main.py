from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import pandas as pd
from typing import Literal, Optional
import joblib
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import re
import uuid
import secrets
import bcrypt
from datetime import datetime, timedelta

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load('Mental_Health_Model.pkl')

# =========================================================
# AUTH SETUP
# =========================================================
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
SESSION_LIFETIME_DAYS = 7

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    # bcrypt only uses the first 72 bytes of the input
    pw_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    pw_bytes = password.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(pw_bytes, password_hash.encode("utf-8"))
    except ValueError:
        return False


def _ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "w") as f:
            json.dump({}, f)


def _load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def _save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


_ensure_data_files()


def get_user_by_email(email: str):
    users = _load_json(USERS_FILE)
    email_lower = email.strip().lower()
    for u in users:
        if u["email"].lower() == email_lower:
            return u
    return None


def create_session(email: str) -> str:
    sessions = _load_json(SESSIONS_FILE)
    token = secrets.token_hex(32)
    sessions[token] = {
        "email": email.strip().lower(),
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=SESSION_LIFETIME_DAYS)).isoformat(),
    }
    _save_json(SESSIONS_FILE, sessions)
    return token


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ", 1)[1]
    sessions = _load_json(SESSIONS_FILE)
    session = sessions.get(token)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    if datetime.fromisoformat(session["expires_at"]) < datetime.utcnow():
        del sessions[token]
        _save_json(SESSIONS_FILE, sessions)
        raise HTTPException(status_code=401, detail="Session expired, please log in again")

    user = get_user_by_email(session["email"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def public_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
    }


# ---------- request models ----------
class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def validate_register(data: RegisterRequest) -> dict:
    errors = {}

    if not data.first_name or not data.first_name.strip():
        errors["first_name"] = "First name is required."
    elif len(data.first_name.strip()) > 50:
        errors["first_name"] = "First name is too long."

    if not data.last_name or not data.last_name.strip():
        errors["last_name"] = "Last name is required."
    elif len(data.last_name.strip()) > 50:
        errors["last_name"] = "Last name is too long."

    if not data.email or not data.email.strip():
        errors["email"] = "Email is required."
    elif not EMAIL_REGEX.match(data.email.strip()):
        errors["email"] = "Enter a valid email address."
    elif get_user_by_email(data.email):
        errors["email"] = "An account with this email already exists."

    if not data.password:
        errors["password"] = "Password is required."
    elif len(data.password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    elif not re.search(r"[A-Za-z]", data.password) or not re.search(r"[0-9]", data.password):
        errors["password"] = "Password must include both letters and numbers."

    if not data.confirm_password:
        errors["confirm_password"] = "Please confirm your password."
    elif data.confirm_password != data.password:
        errors["confirm_password"] = "Passwords don't match."

    return errors


def validate_login(data: LoginRequest) -> dict:
    errors = {}

    if not data.email or not data.email.strip():
        errors["email"] = "Email is required."
    elif not EMAIL_REGEX.match(data.email.strip()):
        errors["email"] = "Enter a valid email address."

    if not data.password:
        errors["password"] = "Password is required."

    return errors


@app.post("/register")
def register(data: RegisterRequest):
    errors = validate_register(data)
    if errors:
        return JSONResponse(status_code=400, content={"errors": errors})

    users = _load_json(USERS_FILE)
    new_user = {
        "id": str(uuid.uuid4()),
        "first_name": data.first_name.strip(),
        "last_name": data.last_name.strip(),
        "email": data.email.strip().lower(),
        "password_hash": hash_password(data.password),
        "created_at": datetime.utcnow().isoformat(),
    }
    users.append(new_user)
    _save_json(USERS_FILE, users)

    token = create_session(new_user["email"])
    return {
        "message": "Account created successfully.",
        "token": token,
        "user": public_user(new_user),
    }


@app.post("/login")
def login(data: LoginRequest):
    errors = validate_login(data)
    if errors:
        return JSONResponse(status_code=400, content={"errors": errors})

    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password_hash"]):
        return JSONResponse(
            status_code=401,
            content={"errors": {"password": "Incorrect email or password."}},
        )

    token = create_session(user["email"])
    return {
        "message": "Logged in successfully.",
        "token": token,
        "user": public_user(user),
    }


@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return public_user(current_user)


@app.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        sessions = _load_json(SESSIONS_FILE)
        if token in sessions:
            del sessions[token]
            _save_json(SESSIONS_FILE, sessions)
    return {"message": "Logged out."}


#first pydantic model
class student_data(BaseModel):
    Age: int = Field(..., gt=0, le=120)

    Gender: Literal["Male", "Female"]

    Country: Literal[
        "India", "USA", "Canada", "Australia",
        "UK", "Germany", "Turkey", "Mexico", "France"
    ]

    Academic_Level: Literal[
        "Undergraduate", "Graduate", "High School"
    ]

    Most_Used_Platform: Literal[
        "Facebook", "LinkedIn", "Instagram", "Snapchat",
        "Twitter", "YouTube", "TikTok", "LINE",
        "KakaoTalk", "VKontakte", "WhatsApp", "WeChat"
    ]

    Purpose_Of_Use: Literal[
        "Networking", "Education", "Entertainment", "News"
    ]

    Avg_Daily_Usage_Hours: float = Field(..., ge=0, le=24)
    Daily_Unlocks: int = Field(..., ge=0)
    Study_Hours: int = Field(..., ge=0, le=24)
    Physical_Activity_Hours: int = Field(..., ge=0, le=24)
    Sleep_Hours_Per_Night: int = Field(..., ge=0, le=24)

    Stress_Level: Literal[
        "Low", "Medium", "High", "Very High"
    ]


# Describe what we send back to the user
class prediction_response(BaseModel):
    predicted_mental_health_score: float


@app.get("/")
def home_page():
    return {"message": "Welcome to the Mental Health Prediction API!"}


top_countries = ['Other', 'India', 'USA', 'Canada', 'Australia', 'UK', 'Germany', 'Turkey', 'Mexico', 'France']

@app.post("/predict", response_model=prediction_response)
def predict_mental_health(data: student_data, current_user: dict = Depends(get_current_user)):

    country_group = data.Country if data.Country in top_countries else 'Other'

    input_row = pd.DataFrame([
        {
            'Age': data.Age,
            'Gender': data.Gender,
            'Country': data.Country,
            'Academic_Level': data.Academic_Level,
            'Most_Used_Platform': data.Most_Used_Platform,
            'Purpose_Of_Use': data.Purpose_Of_Use,
            'Avg_Daily_Usage_Hours': data.Avg_Daily_Usage_Hours,
            'Daily_Unlocks': data.Daily_Unlocks,
            'Study_Hours': data.Study_Hours,
            'Physical_Activity_Hours': data.Physical_Activity_Hours,
            'Sleep_Hours_Per_Night': data.Sleep_Hours_Per_Night,
            'Stress_Level': data.Stress_Level,
            'grouped_country': country_group
        }
    ])

    prediction = model.predict(input_row)[0]

    return prediction_response(predicted_mental_health_score=round(prediction, 2))