import unittest
from unittest.mock import MagicMock
from utils.planner import TaskPlanner
from utils.llm_manager import LLMManager
from utils.tools import WebSearchTool, WeatherTool

class TestTaskPlanner(unittest.TestCase):
    def test_plan(self):
        # Create mock tools and LLM manager
        llm_manager = MagicMock(spec=LLMManager)
        web_tool = MagicMock(spec=WebSearchTool)
        weather_tool = MagicMock(spec=WeatherTool)

        # Set up the mock responses
        llm_manager.generate.return_value = '{"duration_days": 1, "location": "Test City", "key_themes": ["testing"]}'
        web_tool.search.return_value = [{"title": "Test Search Result"}]
        weather_tool.get_forecast.return_value = {"location": "Test City", "forecast": [{"temp": 25}]}

        # Create a TaskPlanner with the mock tools
        planner = TaskPlanner(llm_manager, web_tool, weather_tool)

        # Call the plan method
        plan = planner.plan("test goal")

        # Assert that the plan is created as expected
        self.assertEqual(plan.goal, "test goal")
        self.assertEqual(plan.total_days, 1)
        self.assertEqual(plan.days[0].theme, "Day 1: Main Plan")

if __name__ == '__main__':
    unittest.main()
