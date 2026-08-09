#!/bin/bash

echo "=== TEST 1: 'Bad' habits (expecting a LOW score) ==="
curl -s -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ac5cab875f862b7574e791586ebe8fef1de083f18e399eaca5782db7d312cdd1" \
  -d '{
    "Age": 20,
    "Gender": "Male",
    "Country": "India",
    "Academic_Level": "Undergraduate",
    "Most_Used_Platform": "TikTok",
    "Purpose_Of_Use": "Entertainment",
    "Avg_Daily_Usage_Hours": 12,
    "Daily_Unlocks": 200,
    "Study_Hours": 1,
    "Physical_Activity_Hours": 0,
    "Sleep_Hours_Per_Night": 3,
    "Stress_Level": "Very High"
  }'

echo ""
echo "=== TEST 2: 'Good' habits (expecting a HIGH score) ==="
curl -s -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ac5cab875f862b7574e791586ebe8fef1de083f18e399eaca5782db7d312cdd1" \
  -d '{
    "Age": 20,
    "Gender": "Male",
    "Country": "India",
    "Academic_Level": "Undergraduate",
    "Most_Used_Platform": "LinkedIn",
    "Purpose_Of_Use": "Education",
    "Avg_Daily_Usage_Hours": 1,
    "Daily_Unlocks": 10,
    "Study_Hours": 6,
    "Physical_Activity_Hours": 2,
    "Sleep_Hours_Per_Night": 8,
    "Stress_Level": "Low"
  }'
echo ""