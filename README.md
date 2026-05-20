ai_module/
- Chatbot.py -> conversational AI logic
- recommendation_agent.py -> personalized recommendations
- checkin_agent.py -> daily analysis/trend analysis
- user_memory_db.py -> Supabase persistence
- product_db.py -> product/offers retrieval

backend/
- FastAPI endpoints

app_ui.py
- Streamlit orchestration/UI
- connects all agents together

User profile
→ recommendation agent
→ check-in analysis
→ memory update
→ trend analysis
→ adaptive recommendations

Supabase tables:
- products
- bundle_offers
- user_memory
- daily_checkins
- daily_meal_logs
- daily_activity_logs
- user_profiles
