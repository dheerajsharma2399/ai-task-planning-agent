from enum import Enum
import streamlit as st
import logging

# Import LLM providers
import google.generativeai as genai
import openai
from openai import OpenAI
import ollama

# Configuration
class LLMProvider(Enum):
    OPENROUTER = "openrouter"
    GEMINI = "gemini"
    OLLAMA = "ollama"

class LLMManager:
    """Manages different LLM providers"""
    
    def __init__(self):
        self.provider = None
        self.client = None
        self.model_name = None # Added to store the specific model name for OpenRouter

    def initialize(self, provider: LLMProvider, api_key: str = None, model_name: str = None):
        """Initialize the selected LLM provider and verify its functionality"""
        self.provider = provider
        self.model_name = model_name # Store the model name

        try:
            if provider == LLMProvider.OPENROUTER:
                if not api_key:
                    raise ValueError("OpenRouter API Key is required.")
                if not model_name:
                    raise ValueError("OpenRouter model name is required.")
                
                logging.info(f"Initializing OpenRouter with model: {model_name}, API Key (masked): {api_key[:5]}...{api_key[-5:]}")
                
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                # Verify OpenRouter client by making a small test call
                self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": "hi"}],
                    max_tokens=1
                )
            elif provider == LLMProvider.GEMINI:
                if not api_key:
                    raise ValueError("Gemini API Key is required.")
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel('gemini-2.0-flash')
                # Verify Gemini client by making a small test call
                self.client.generate_content("hi", stream=True).resolve()
            elif provider == LLMProvider.OLLAMA:
                self.client = ollama.Client(host='http://localhost:11434')
                # Verify Ollama client by listing local models
                ollama.list()
            
            st.session_state.llm_initialized = True

        except Exception as e:
            self.client = None
            st.session_state.llm_initialized = False
            raise Exception(f"Failed to initialize {provider.value.upper()}: {str(e)}")
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from the selected LLM"""
        import logging
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Generating LLM response for prompt: {prompt}")
        try:
            if self.provider == LLMProvider.GEMINI:
                response = self.client.generate_content(
                    f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                )
                logging.info(f"LLM response: {response.text}")
                return response.text
            
            elif self.provider == LLMProvider.OLLAMA:
                response = self.client.chat(
                    model='mistral:7b',
                    messages=[
                        {'role': 'system', 'content': system_prompt or ''},
                        {'role': 'user', 'content': prompt}
                    ]
                )
                logging.info(f"LLM response: {response['message']['content']}")
                return response['message']['content']
            
            elif self.provider == LLMProvider.OPENROUTER:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                model = self.model_name # Directly use the stored model name
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                logging.info(f"LLM response: {response.choices[0].message.content}")
                return response.choices[0].message.content
                
        except Exception as e:
            logging.error(f"LLM Error: {str(e)}")
            st.error(f"LLM Error: {str(e)}")
            raise # Re-raise the exception instead of returning None

