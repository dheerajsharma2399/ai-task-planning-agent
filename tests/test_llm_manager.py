import unittest
from unittest.mock import MagicMock
from utils.llm_manager import LLMManager, LLMProvider

class TestLLMManager(unittest.TestCase):
    def test_generate_with_mock(self):
        # Create a mock LLMManager
        llm_manager = LLMManager()
        llm_manager.provider = LLMProvider.OPENROUTER
        llm_manager.client = MagicMock()

        # Set up the mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a mock response."
        llm_manager.client.chat.completions.create.return_value = mock_response

        # Call the generate method
        response = llm_manager.generate("test prompt")

        # Assert that the response is what we expect
        self.assertEqual(response, "This is a mock response.")

if __name__ == '__main__':
    unittest.main()
