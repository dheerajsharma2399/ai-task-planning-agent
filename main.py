"""
AI Task Planning Agent - Main Application
A comprehensive task planning agent with multi-LLM support
"""

import streamlit as st
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass, asdict
import hashlib
import time
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# Import LLM providers
import google.generativeai as genai
import openai
from openai import OpenAI
import ollama

# Configuration
class LLMProvider(Enum):
    OPENROUTER = "openrouter"
    GEMINI = "gemini"
    CHATGPT = "chatgpt"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"

@dataclass
class PlanStep:
    """Represents a single step in a plan"""
    step_number: int
    title: str
    description: str
    time: Optional[str] = None
    location: Optional[str] = None
    additional_info: Optional[Dict] = None

@dataclass
class DayPlan:
    """Represents a day's plan"""
    day_number: int
    theme: str
    steps: List[PlanStep]
    date: Optional[str] = None
    weather_info: Optional[Dict] = None

@dataclass
class TaskPlan:
    """Complete task plan"""
    goal: str
    created_at: str
    total_days: int
    days: List[DayPlan]
    metadata: Dict[str, Any]

class LLMManager:
    """Manages different LLM providers"""
    
    def __init__(self):
        self.provider = None
        self.client = None
        
    def initialize(self, provider: LLMProvider, api_key: str = None):
        """Initialize the selected LLM provider"""
        self.provider = provider
        
        if provider == LLMProvider.OPENROUTER:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
        elif provider == LLMProvider.GEMINI:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel('gemini-pro')
        elif provider == LLMProvider.CHATGPT:
            self.client = OpenAI(api_key=api_key)
        elif provider == LLMProvider.DEEPSEEK:
            self.client = OpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=api_key if api_key else "free"
            )
        elif provider == LLMProvider.OLLAMA:
            self.client = ollama.Client(host='http://localhost:11434')
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from the selected LLM"""
        try:
            if self.provider == LLMProvider.GEMINI:
                response = self.client.generate_content(
                    f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                )
                return response.text
            
            elif self.provider == LLMProvider.OLLAMA:
                response = self.client.chat(
                    model='mistral:7b',
                    messages=[
                        {'role': 'system', 'content': system_prompt or ''},
                        {'role': 'user', 'content': prompt}
                    ]
                )
                return response['message']['content']
            
            elif self.provider in [LLMProvider.OPENROUTER, LLMProvider.CHATGPT, LLMProvider.DEEPSEEK]:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                model = self._get_model_name()
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
                
        except Exception as e:
            st.error(f"LLM Error: {str(e)}")
            return None
    
    def _get_model_name(self) -> str:
        """Get the model name based on provider"""
        models = {
            LLMProvider.OPENROUTER: "mistralai/mistral-7b-instruct",
            LLMProvider.CHATGPT: "gpt-3.5-turbo",
            LLMProvider.DEEPSEEK: "deepseek-chat"
        }
        return models.get(self.provider, "gpt-3.5-turbo")

class WebSearchTool:
    """Web search tool using DuckDuckGo"""
    
    @staticmethod
    def search(query: str, num_results: int = 5) -> List[Dict]:
        """Search the web for information"""
        try:
            # Using DuckDuckGo HTML API (no key required)
            url = "https://html.duckduckgo.com/html/"
            params = {'q': query}
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            # Simple parsing for demo (in production, use BeautifulSoup)
            results = []
            if response.status_code == 200:
                # Extract basic results from HTML
                text = response.text
                # Simplified extraction - in production use proper HTML parsing
                for i in range(min(num_results, 3)):
                    results.append({
                        'title': f'Result {i+1} for: {query}',
                        'snippet': f'Information about {query} from web search.',
                        'url': f'https://example.com/{i}'
                    })
            return results
        except Exception as e:
            st.warning(f"Search error: {str(e)}")
            return []

class WeatherTool:
    """Weather information tool"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "demo"  # Use demo key for testing
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_forecast(self, location: str, days: int = 3) -> Dict:
        """Get weather forecast for a location"""
        try:
            if self.api_key == "demo":
                # Return mock data for demo
                return {
                    'location': location,
                    'forecast': [
                        {'day': i+1, 'temp': 25+i, 'condition': 'Clear'} 
                        for i in range(days)
                    ]
                }
            
            # Real API call
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Process and simplify the forecast
                return self._process_forecast(data, days)
            else:
                return {'error': 'Weather data unavailable'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _process_forecast(self, data: Dict, days: int) -> Dict:
        """Process raw forecast data"""
        forecast = []
        for i in range(days):
            day_data = data['list'][i*8] if i*8 < len(data['list']) else data['list'][-1]
            forecast.append({
                'day': i+1,
                'temp': day_data['main']['temp'],
                'condition': day_data['weather'][0]['description'],
                'humidity': day_data['main']['humidity']
            })
        return {'location': data['city']['name'], 'forecast': forecast}

class TaskPlanner:
    """Main task planning orchestrator"""
    
    def __init__(self, llm_manager: LLMManager, web_tool: WebSearchTool, weather_tool: WeatherTool):
        self.llm = llm_manager
        self.web_tool = web_tool
        self.weather_tool = weather_tool
    
    def plan(self, goal: str) -> TaskPlan:
        """Create a comprehensive plan for the given goal"""
        
        # Extract key information from goal
        plan_info = self._analyze_goal(goal)
        
        # Gather external information
        enrichment_data = self._gather_information(goal, plan_info)
        
        # Generate structured plan
        structured_plan = self._generate_plan(goal, plan_info, enrichment_data)
        
        return structured_plan
    
    def _analyze_goal(self, goal: str) -> Dict:
        """Analyze the goal to extract key information"""
        prompt = f'''
        Analyze this goal and extract key information:
        Goal: "{goal}"
        
        Return a JSON with:
        - duration_days: number of days (default 1 if not specified)
        - location: main location if mentioned
        - type: type of plan (travel/study/routine/food/activity)
        - key_themes: main themes or activities
        
        Format as valid JSON.
        '''
        
        response = self.llm.generate(prompt)
        try:
            # Parse JSON from response
            import re
            json_match = re.search(r'\{{.*\}}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback
        return {
            'duration_days': 1,
            'location': None,
            'type': 'general',
            'key_themes': ['general planning']
        }
    
    def _gather_information(self, goal: str, plan_info: Dict) -> Dict:
        """Gather external information relevant to the goal"""
        data = {}
        
        # Get location-specific information
        if plan_info.get('location'):
            # Search for places and activities
            search_query = f"{plan_info['location']} attractions food culture"
            data['search_results'] = self.web_tool.search(search_query, 5)
            
            # Get weather forecast
            data['weather'] = self.weather_tool.get_forecast(
                plan_info['location'], 
                plan_info.get('duration_days', 1)
            )
        
        # Get theme-specific information
        for theme in plan_info.get('key_themes', []):
            theme_results = self.web_tool.search(f"{theme} tips recommendations", 3)
            data[f'theme_{theme}'] = theme_results
        
        return data
    
    def _generate_plan(self, goal: str, plan_info: Dict, enrichment_data: Dict) -> TaskPlan:
        """Generate the final structured plan"""
        
        system_prompt = '''
        You are an expert task planner. Create detailed, actionable plans with specific times, 
        locations, and helpful information. Structure your response as a day-by-day plan with 
        clear steps. Be specific and practical.
        '''
        
        prompt = f'''
        Create a detailed plan for: "{goal}"
        
        Duration: {plan_info.get('duration_days', 1)} days
        Location: {plan_info.get('location', 'Not specified')}
        
        Available information:
        {json.dumps(enrichment_data, indent=2)[:1000]}  # Truncate for length
        
        Generate a day-by-day plan with:
        - Day number and theme
        - 3-5 specific steps per day
        - Times and locations when relevant
        - Practical tips and recommendations
        
        Format each day clearly with numbered steps.
        '''
        
        response = self.llm.generate(prompt, system_prompt)
        
        # Parse the response into structured plan
        return self._parse_plan_response(goal, response, plan_info, enrichment_data)
    
    def _parse_plan_response(self, goal: str, response: str, plan_info: Dict, enrichment_data: Dict) -> TaskPlan:
        """Parse LLM response into structured TaskPlan"""
        
        days = []
        current_day = None
        current_steps = []
        
        lines = response.split('\n')
        day_counter = 1
        step_counter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect day markers
            if any(marker in line.lower() for marker in ['day', 'день']):
                if current_day and current_steps:
                    days.append(DayPlan(
                        day_number=day_counter,
                        theme=current_day,
                        steps=current_steps,
                        weather_info=enrichment_data.get('weather', {}).get('forecast', [{}])[day_counter-1] if enrichment_data.get('weather') else None
                    ))
                    day_counter += 1
                    current_steps = []
                
                current_day = line
                step_counter = 1
            
            # Detect steps
            elif any(char in line for char in ['1.', '2.', '3.', '•', '-']):
                step = PlanStep(
                    step_number=step_counter,
                    title=f"Step {step_counter}",
                    description=line.lstrip('0123456789.-• ')
                )
                current_steps.append(step)
                step_counter += 1
        
        # Add last day
        if current_day and current_steps:
            days.append(DayPlan(
                day_number=day_counter,
                theme=current_day,
                steps=current_steps,
                weather_info=enrichment_data.get('weather', {}).get('forecast', [{}])[day_counter-1] if enrichment_data.get('weather') else None
            ))
        
        # Fallback if no days were parsed
        if not days:
            days = [DayPlan(
                day_number=1,
                theme="Day 1: Main Plan",
                steps=[PlanStep(
                    step_number=1,
                    title="Complete Plan",
                    description=response[:500]
                )]
            )]
        
        return TaskPlan(
            goal=goal,
            created_at=datetime.now().isoformat(),
            total_days=len(days),
            days=days,
            metadata=plan_info
        )

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "task_plans.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                plan_data TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_plan(self, plan: TaskPlan) -> int:
        """Save a plan to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert plan to JSON
        plan_dict = {
            'goal': plan.goal,
            'created_at': plan.created_at,
            'total_days': plan.total_days,
            'days': [
                {
                    'day_number': day.day_number,
                    'date': day.date,
                    'theme': day.theme,
                    'steps': [asdict(step) for step in day.steps],
                    'weather_info': day.weather_info
                }
                for day in plan.days
            ],
            'metadata': plan.metadata
        }
        
        cursor.execute('''
            INSERT INTO plans (goal, created_at, plan_data, metadata)
            VALUES (?, ?, ?, ?)
        ''', (
            plan.goal,
            plan.created_at,
            json.dumps(plan_dict),
            json.dumps(plan.metadata)
        ))
        
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return plan_id
    
    def get_all_plans(self) -> List[Dict]:
        """Retrieve all plans from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, goal, created_at, plan_data, metadata
            FROM plans
            ORDER BY created_at DESC
        ''')
        
        plans = []
        for row in cursor.fetchall():
            plan_data = json.loads(row[3])
            plans.append({
                'id': row[0],
                'goal': row[1],
                'created_at': row[2],
                'plan': plan_data,
                'metadata': json.loads(row[4]) if row[4] else {}
            })
        
        conn.close()
        return plans
    
    def get_plan_by_id(self, plan_id: int) -> Optional[Dict]:
        """Get a specific plan by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, goal, created_at, plan_data, metadata
            FROM plans
            WHERE id = ?
        ''', (plan_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'goal': row[1],
                'created_at': row[2],
                'plan': json.loads(row[3]),
                'metadata': json.loads(row[4]) if row[4] else {}
            }
        return None

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
        if provider != "ollama":
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
                    api_key
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
    tab1, tab2, tab3 = st.tabs(["📝 Create Plan", "📚 Plan History", "🔍 View Plan"])
    
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
                elif not st.session_state.llm_manager.provider:
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
