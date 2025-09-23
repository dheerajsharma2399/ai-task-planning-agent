"""
AI Task Planning Agent - Main Application
A comprehensive task planning agent with multi-LLM support
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import os

from utils.llm_manager import LLMManager, LLMProvider
from utils.tools import WebSearchTool, WeatherTool
from utils.planner import TaskPlanner, TaskPlan, DayPlan, PlanStep
from utils.database import DatabaseManager
from dotenv import load_dotenv

load_dotenv()

# Streamlit Application
def main():
    st.set_page_config(
        page_title="AI Task Planner",
        page_icon="📋",
        layout="wide"
    )
    
    # Initialize session state
    if 'llm_manager' not in st.session_state:
        st.session_state.llm_manager = LLMManager()
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = None
    if 'llm_initialized' not in st.session_state:
        st.session_state.llm_initialized = False
    
    # Sidebar for configuration
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # LLM Provider selection
        provider = st.selectbox(
            "Select LLM Provider",
            options=[p.value for p in LLMProvider],
            format_func=lambda x: x.upper()
        )
        
        # API Key input (if needed)
        api_key = None
        openrouter_model = None

        if provider == LLMProvider.OPENROUTER.value:
            openrouter_models = [
                "x-ai/grok-4-fast:free",
                "deepseek/deepseek-chat-v3.1:free",
                "deepseek/deepseek-r1-0528:free",
                "deepseek/deepseek-chat-v3-0324:free",
                "z-ai/glm-4.5-air:free",
                "deepseek/deepseek-r1:free",
                "tngtech/deepseek-r1t2-chimera:free",
                "qwen/qwen3-coder:free",
                "tngtech/deepseek-r1t-chimera:free",
                "qwen/qwen3-235b-a22b:free"
            ]
            openrouter_model = st.selectbox("Select OpenRouter Model", options=openrouter_models)
            api_key_input = st.text_input(
                f"{provider.upper()} API Key",
                type="password",
                help="Enter your API key or set it in the .env file."
            )
            env_var_name = f"{provider.upper()}_API_KEY"
            api_key_env = os.getenv(env_var_name)
            api_key = api_key_input if api_key_input else api_key_env
            st.write(f"Model used: {openrouter_model}")
            import logging
            logging.basicConfig(level=logging.INFO)
            masked_api_key = f"{api_key[:5]}...{api_key[-5:]}" if api_key else "<API Key not provided>"
            logging.info(f"OpenRouter API Key being used (masked): {masked_api_key}")
        elif provider != "ollama":
            api_key_input = st.text_input(
                f"{provider.upper()} API Key",
                type="password",
                help="Enter your API key or set it in the .env file."
            )
            env_var_name = f"{provider.upper()}_API_KEY"
            api_key_env = os.getenv(env_var_name)
            api_key = api_key_input if api_key_input else api_key_env
            st.write(f"API Key used: {api_key}")
        
        # Weather API Key
        weather_key = st.text_input(
            "OpenWeather API Key (Optional)",
            type="password",
            help="Optional: Add for real weather data"
        )
        
        if st.button("Initialize LLM"):
            try:
                st.session_state.llm_manager.initialize(
                    LLMProvider(provider),
                    api_key,
                    openrouter_model if provider == LLMProvider.OPENROUTER.value else None
                )
                st.success(f"✅ Initialized {provider.upper()}")
            except Exception as e:
                st.error(f"Failed to initialize: {str(e)}")
        
        st.divider()
        
        # Example goals
        st.subheader("📝 Example Goals")
        examples = [
            "Plan a 3-day trip to Jaipur with cultural highlights and good food",
            "Plan a 2-day vegetarian food tour in Hyderabad",
            "Organize a 5-step daily study routine for learning Python",
            "Create a weekend plan in Vizag with beach, hiking, and seafood"
        ]
        
        for example in examples:
            if st.button(example[:30] + "...", key=example):
                st.session_state.example_goal = example
    
    # Main area
    st.title("🤖 AI Task Planning Agent")
    st.markdown("*Transform your goals into actionable, enriched plans*")

    # Tabs for different views
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "📝 Create Plan"

    tabs = ["📝 Create Plan", "📚 Plan History", "🔍 View Plan"]
    tab1, tab2, tab3 = st.tabs(tabs)

    with tab1:
        st.header("Create New Plan")
        
        # Goal input
        goal = st.text_area(
            "Enter your goal",
            value=st.session_state.get('example_goal', ''),
            placeholder="e.g., Plan a 3-day trip to Jaipur with cultural highlights and good food",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🎯 Generate Plan", type="primary"):
                if not goal:
                    st.error("Please enter a goal")
                elif not st.session_state.llm_initialized:
                    st.error("Please initialize LLM provider first")
                else:
                    with st.spinner("Creating your personalized plan..."):
                        try:
                            # Initialize tools
                            web_tool = WebSearchTool()
                            weather_tool = WeatherTool(weather_key)
                            
                            # Create planner
                            planner = TaskPlanner(
                                st.session_state.llm_manager,
                                web_tool,
                                weather_tool
                            )
                            
                            # Generate plan
                            plan = planner.plan(goal)
                            
                            # Save to database
                            plan_id = st.session_state.db_manager.save_plan(plan)
                            
                            st.session_state.current_plan = plan
                            st.success(f"✅ Plan created successfully! (ID: {plan_id})")
                            
                        except Exception as e:
                            st.error(f"Error creating plan: {str(e)}")
        
        # Display current plan
        if st.session_state.current_plan:
            st.divider()
            display_plan(st.session_state.current_plan)
    
    with tab2:
        st.header("Plan History")
        
        plans = st.session_state.db_manager.get_all_plans()
        
        if not plans:
            st.info("No plans created yet. Create your first plan!")
        else:
            for plan in plans:
                with st.expander(f"📋 {plan['goal'][:60]}... | {plan['created_at'][:10]}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Goal:** {plan['goal']}")
                        st.write(f"**Created:** {plan['created_at']}")
                        st.write(f"**Days:** {plan['plan']['total_days']}")
                    with col2:
                        if st.button(f"View Plan #{plan['id']}", key=f"view_{plan['id']}"):
                            st.session_state.selected_plan_id = plan['id']
                            st.session_state.active_tab = "🔍 View Plan"
                            st.rerun()

    with tab3:
        st.header("Plan Details")
        
        if hasattr(st.session_state, 'selected_plan_id'):
            plan_data = st.session_state.db_manager.get_plan_by_id(
                st.session_state.selected_plan_id
            )
            
            if plan_data:
                st.subheader(f"Plan #{plan_data['id']}")
                st.write(f"**Goal:** {plan_data['goal']}")
                st.write(f"**Created:** {plan_data['created_at']}")
                
                st.divider()
                
                # Convert dict back to TaskPlan for display
                plan = TaskPlan(
                    goal=plan_data['plan']['goal'],
                    created_at=plan_data['plan']['created_at'],
                    total_days=plan_data['plan']['total_days'],
                    days=[
                        DayPlan(
                            day_number=day['day_number'],
                            date=day.get('date'),
                            theme=day['theme'],
                            steps=[
                                PlanStep(**step) for step in day['steps']
                            ],
                            weather_info=day.get('weather_info')
                        )
                        for day in plan_data['plan']['days']
                    ],
                    metadata=plan_data['plan']['metadata']
                )
                
                display_plan(plan)
        else:
            st.info("Select a plan from the History tab to view details")

def display_plan(plan: TaskPlan):
    """Display a plan in a formatted way"""
    
    st.markdown(f"### 📍 {plan.goal}")
    st.markdown(f"**Duration:** {plan.total_days} days")
    
    for day in plan.days:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"#### {day.theme}")
            
            with col2:
                if day.weather_info and 'temp' in day.weather_info:
                    st.metric("Temp", f"{day.weather_info['temp']}°C")
            
            for step in day.steps:
                with st.container():
                    st.markdown(f"**{step.step_number}.** {step.description}")
                    
                    if step.time:
                        st.caption(f"⏰ {step.time}")
                    if step.location:
                        st.caption(f"📍 {step.location}")
                    if step.additional_info:
                        with st.expander("Additional Info"):
                            st.json(step.additional_info)
            
            st.divider()

if __name__ == "__main__":
    main()