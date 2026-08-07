from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
from typing import Literal
import joblib
from fastapi.middleware.cors import CORSMiddleware

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

    Avg_Daily_Usage_Hours: float = Field(..., gt=0, le=24)
    Daily_Unlocks: int = Field(..., gt=0)
    Study_Hours: int = Field(..., gt=0, le=24)
    Physical_Activity_Hours: int = Field(..., ge=0, le=24)
    Sleep_Hours_Per_Night: int = Field(..., gt=0, le=24)

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
def predict_mental_health(data: student_data):

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