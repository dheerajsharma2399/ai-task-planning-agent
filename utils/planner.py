import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from utils.llm_manager import LLMManager
from utils.tools import WebSearchTool, WeatherTool

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
        
        # Parse JSON from response
        import re
        json_match = re.search(r'{{.*}}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        # Fallback if JSON parsing fails or no match
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
