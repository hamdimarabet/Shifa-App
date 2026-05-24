from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from ai_module.Chatbot import chatbot_response
from ai_module.checkin_agent import build_daily_checkin_output
from ai_module.recommendation_agent import build_recommendation_agent_output
from ai_module.user_memory_db import (
    create_daily_checkin,
    log_daily_meal,
    log_daily_activity,
    get_recent_checkins,
    update_user_memory
)
from ai_module.checkin_agent import (
    analyze_recent_trends,
    compute_consistency_from_recent_checkins
)

app = FastAPI()

class ChatRequest(BaseModel):
    question: str
    age: int | None = None
    user_id: str | None = None
    height: float | None = None
    weight: float | None = None
    goals: list[str] | None = None
    preferences: str | None = None
    activity_info: str | None = None
    history: str | None = None
    chat_history: Optional[List[Dict[str, str]]] = None

class CheckinRequest(BaseModel):
    user_id: str
    meals_today: str
    activity_today: str
    mood: str | None = None
    age: int | None = None
    weight: float | None = None
    height: float | None = None
    sex: str | None = None
    goals: list[str] | None = None
    language: str | None = 'ar'

class RecommendRequest(BaseModel):
    user_id: str
    age: int | None = None
    weight: float | None = None
    height: float | None = None
    sex: str | None = None
    goals: list[str] | None = None
    language: str | None = 'ar'
    activity_info: str | None = None

@app.get("/")
def root():
    return {"message": "ShifaChatbot API is running"}

@app.post("/chat")
def chat(req: ChatRequest):
    user_profile = {
        "age": req.age,
        "user_id": req.user_id or "demo_user",
        "weight": req.weight,
        "goals": req.goals,
        "height": req.height,
        "preferences": req.preferences,
        "activity_info": req.activity_info,
        "history": req.history,
    }

    result = chatbot_response(
        question=req.question,
        user_profile=user_profile,
        chat_history=req.chat_history or []
    )

    return {
        "response": result["answer"],
        "intent": result["intent"],
        "detected_product": result["detected_product"],
        "recommended_product": result["recommended_product"],
        "recommendation_reason": result["recommendation_reason"],
        "meal_suggestion": result["meal_suggestion"],
        "calorie_info": result["calorie_info"],
        "usage_info": result["usage_info"],
        "benefits_info": result["benefits_info"],
        "precautions": result["precautions"],
        "lifestyle_suggestion": result["lifestyle_suggestion"],
        "follow_up_question": result["follow_up_question"],
        "price_info": result["price_info"],
        "offer_info": result["offer_info"],
    }

@app.post("/checkin")
def checkin(req: CheckinRequest):
    user_profile = {
        "user_id": req.user_id,
        "age": req.age,
        "weight": req.weight,
        "height": req.height,
        "sex": req.sex,
        "goals": req.goals or [],
        "language": req.language or "ar",
    }

    result = build_daily_checkin_output(
        user_profile=user_profile,
        meals_today=req.meals_today,
        activity_today=req.activity_today,
        mood=req.mood or ""
    )

    checkin_record = create_daily_checkin(
        req.user_id,
        {
            "mood": req.mood,
            "notes": f"Consistency score: {result['consistency_score']}"
        }
    )

    energy = result.get("energy_estimation", {})

    log_daily_meal(checkin_record["id"], {
        "meal_type": "general",
        "description": req.meals_today,
        "estimated_calories": energy.get("estimated_calories_in"),
        "estimated_protein": None,
    })

    log_daily_activity(checkin_record["id"], {
        "activity_type": "general",
        "description": req.activity_today,
        "intensity": result["activity_level_today"],
        "estimated_calories_burned": energy.get("estimated_calories_burned"),
    })

    recent_checkins = get_recent_checkins(req.user_id, limit=7)
    consistency_result = compute_consistency_from_recent_checkins(recent_checkins)
    trend_analysis = analyze_recent_trends(recent_checkins)

    result["memory_updates"]["consistency_score"] = consistency_result["score"]
    result["memory_updates"]["trend_analysis"] = trend_analysis

    update_user_memory(req.user_id, result["memory_updates"])

    return {
        "consistency_score": result["consistency_score"],
        "activity_level_today": result["activity_level_today"],
        "meal_feedback": result["meal_feedback"],
        "activity_feedback": result["activity_feedback"],
        "product_hint": result["product_hint"],
        "energy_estimation": result.get("energy_estimation", {}),
        "trend_direction": trend_analysis["trend_direction"],
        "trend_insight": trend_analysis["insight"],
    }

@app.post("/recommend")
def recommend(req: RecommendRequest):
    user_profile = {
        "user_id": req.user_id,
        "age": req.age,
        "weight": req.weight,
        "height": req.height,
        "sex": req.sex,
        "goals": req.goals or [],
        "language": req.language or "ar",
        "activity_info": req.activity_info,
    }

    result = build_recommendation_agent_output(user_profile)

    return {
        "recommended_products": result.get("recommended_products", []),
        "meal_recommendations": result.get("meal_recommendations", []),
        "exercise_recommendations": result.get("exercise_recommendations", []),
        "behavioral_insight": result.get("behavioral_insight", ""),
        "motivation_message": result.get("motivation_message", ""),
        "priority_focus": result.get("priority_focus", ""),
    }
