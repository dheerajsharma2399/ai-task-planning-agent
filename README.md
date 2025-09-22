# AI Task Planning Agent 🤖📋

An intelligent task planning assistant that transforms natural language goals into actionable, enriched plans with external data integration.

## 🌟 Features

- **Multi-LLM Support**: Switch between OpenRouter, Gemini, ChatGPT, DeepSeek, and Ollama
- **Smart Planning**: Breaks down goals into day-by-day actionable steps
- **External Enrichment**: Integrates web search and weather data
- **Persistent Storage**: SQLite database for plan history
- **Clean Web Interface**: Streamlit-based UI for easy interaction
- **Production Ready**: Best practices, error handling, and modular design

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface (Streamlit)             │
├─────────────────────────────────────────────────────────┤
│                      Task Planner Core                   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Goal Parser │→ │ Info Gatherer │→ │Plan Generator│  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│                        Services Layer                    │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │
│  │LLM Manager │  │Web Search  │  │Weather Service  │  │
│  └────────────┘  └────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    Data Persistence                      │
│                    SQLite Database                       │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API keys for your chosen LLM provider (optional for Ollama/DeepSeek free)
- OpenWeather API key (optional, for real weather data)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-task-planner.git
cd ai-task-planner
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables (optional)**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **For Ollama users: Install and start Ollama**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Mistral model
ollama pull mistral:7b

# Start Ollama server (if not auto-started)
ollama serve
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Configure LLM Provider

1. Open the sidebar
2. Select your preferred LLM provider
3. Enter API key (if required)
4. Click "Initialize LLM"

### 2. Create a Plan

1. Go to the "Create Plan" tab
2. Enter your goal in natural language
3. Click "Generate Plan"
4. View your structured plan with enriched information

### 3. View Plan History

1. Navigate to "Plan History" tab
2. Browse all previously created plans
3. Click on any plan to view full details

### 4. Export and Share

Plans are automatically saved and can be accessed anytime through the web interface.

## 🎯 Example Goals

### Travel Planning
```
"Plan a 3-day trip to Jaipur with cultural highlights and good food"
```
**Generated Plan:**
- Day 1: Heritage Walk
  - 9:00 AM - Visit Amber Fort
  - 12:00 PM - Lunch at LMB (Laxmi Misthan Bhandar)
  - 2:00 PM - City Palace exploration
  - 5:00 PM - Jantar Mantar observatory
  - 7:00 PM - Dinner at Chokhi Dhani village

- Day 2: Cultural Immersion
  - 9:00 AM - Hawa Mahal photo session
  - 11:00 AM - Albert Hall Museum
  - 1:00 PM - Traditional Rajasthani thali
  - 3:00 PM - Johari Bazaar shopping
  - 6:00 PM - Sunset at Nahargarh Fort

- Day 3: Art & Crafts
  - 9:00 AM - Block printing workshop
  - 12:00 PM - Anokhi Museum
  - 2:00 PM - Lunch at Tapri Central
  - 4:00 PM - Gem cutting demonstration
  - 7:00 PM - Farewell dinner at 1135 AD

### Study Routine
```
"Organize a 5-step daily study routine for learning Python"
```
**Generated Plan:**
- Step 1: Morning Review (30 min)
  - Review yesterday's concepts
  - Quick quiz on fundamentals
  
- Step 2: New Concept Learning (1 hour)
  - Video tutorials or documentation
  - Take structured notes
  
- Step 3: Hands-on Coding (1.5 hours)
  - Practice exercises
  - Work on mini-projects
  
- Step 4: Problem Solving (45 min)
  - LeetCode/HackerRank challenges
  - Debug previous code
  
- Step 5: Community & Reflection (30 min)
  - Engage in Python forums
  - Document learnings in blog/journal

### Food Tour
```
"Plan a 2-day vegetarian food tour in Hyderabad"
```
**Generated Plan:**
- Day 1: Traditional Treats
  - 8:00 AM - Idli & Dosa at Ram ki Bandi
  - 11:00 AM - Street food walk in Charminar area
  - 1:00 PM - Vegetarian Biryani at Bawarchi
  - 4:00 PM - Irani chai & Osmania biscuits
  - 7:00 PM - South Indian thali at Chutneys

- Day 2: Modern & Classic Mix
  - 9:00 AM - Breakfast at Minerva Coffee Shop
  - 12:00 PM - Lunch at Rajdhani (Gujarati thali)
  - 3:00 PM - Sweets at Agrawala Sweets
  - 6:00 PM - Evening snacks at Gokul Chat
  - 8:00 PM - Dinner at Simply South

## 🔧 Configuration

### LLM Providers

| Provider | Model | API Key Required | Notes |
|----------|-------|------------------|-------|
| OpenRouter | Mistral-7B | Yes | Good balance of cost/performance |
| Gemini | Gemini Pro | Yes | Google's latest model |
| ChatGPT | GPT-3.5 Turbo | Yes | OpenAI's reliable model |
| DeepSeek | DeepSeek Chat | Optional | Free tier available |
| Ollama | Mistral:7B | No | Local, privacy-focused |

### Environment Variables

Create a `.env` file:
```env
# LLM API Keys
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here

# Optional Services
OPENWEATHER_API_KEY=your_key_here
```

## 📁 Project Structure

```
ai-task-planner/
├── main.py                # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── task_plans.db         # SQLite database (auto-created)
├── README.md            # Documentation
├── utils/
│   ├── llm_manager.py   # LLM provider management
│   ├── tools.py         # Web search and weather tools
│   ├── planner.py       # Task planning logic
│   └── database.py      # Database operations
└── tests/
    ├── test_planner.py
    └── test_tools.py
```

## 🛡️ Best Practices Implemented

1. **Modular Architecture**: Separated concerns with dedicated managers
2. **Error Handling**: Graceful fallbacks and user-friendly error messages
3. **Type Hints**: Using dataclasses and type annotations
4. **Database Persistence**: SQLite for reliable storage
5. **API Abstraction**: Easy switching between LLM providers
6. **Mock Data**: Demo mode when API keys unavailable
7. **Security**: API keys handled securely through environment variables
8. **Responsive UI**: Clean Streamlit interface with tabs and expandable sections

## 🤖 AI Assistance Disclosure

This project was developed with assistance from AI tools for:
- Code structure recommendations
- Error handling patterns
- Documentation formatting
- Testing strategies

All core logic, architecture decisions, and implementation were human-designed and verified.

## 🚀 Deployment

### Deploy on Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add API keys in Streamlit secrets management
5. Deploy!

### Deploy on Heroku

1. Create `Procfile`:
```
web: sh setup.sh && streamlit run main.py
```

2. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

3. Deploy:
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main.py"]
```

Build and run:
```bash
docker build -t ai-task-planner .
docker run -p 8501:8501 ai-task-planner
```

## 📊 Performance Considerations

- **Caching**: Implement caching for repeated API calls
- **Rate Limiting**: Respect API rate limits
- **Async Operations**: Consider async for multiple API calls
- **Database Indexing**: Add indexes for large plan histories

## 🔮 Future Enhancements

- [ ] Multi-user support with authentication
- [ ] Plan collaboration and sharing
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Mobile app version
- [ ] Voice input for goals
- [ ] Plan templates library
- [ ] Advanced analytics dashboard
- [ ] Export to PDF/Markdown
- [ ] Integration with task management tools (Notion, Trello)
- [ ] Real-time collaboration

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Streamlit for the excellent web framework
- OpenAI, Google, and other LLM providers
- DuckDuckGo for search API
- OpenWeather for weather data
- The open-source community

## 📧 Contact

For questions or support, please open an issue on GitHub or contact [your-email@example.com]

---

**Made with ❤️ for the AI Agent Intern Challenge**