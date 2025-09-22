import unittest
from unittest.mock import patch, MagicMock
from utils.tools import WebSearchTool, WeatherTool

class TestTools(unittest.TestCase):
    @patch('utils.tools.requests.get')
    def test_web_search(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Mock search results</body></html>"
        mock_get.return_value = mock_response

        # Call the search method
        results = WebSearchTool.search("test query")

        # Assert that the results are what we expect
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'Result 1 for: test query')

    @patch('utils.tools.requests.get')
    def test_weather_tool(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "city": {"name": "Test City"},
            "list": [
                {
                    "main": {"temp": 25, "humidity": 50},
                    "weather": [{"description": "clear sky"}]
                }
            ]
        }
        mock_get.return_value = mock_response

        # Call the get_forecast method
        weather_tool = WeatherTool(api_key="test_key")
        forecast = weather_tool.get_forecast("Test City")

        # Assert that the forecast is what we expect
        self.assertEqual(forecast['location'], 'Test City')
        self.assertEqual(forecast['forecast'][0]['temp'], 25)

if __name__ == '__main__':
    unittest.main()
