# AI Agents Hub - Streamlit Chat Interface

A modern, ChatGPT-like interface for interacting with AI agents, starting with the Scientific Research Agent.

## Features

- **Multi-Agent Support**: Left sidebar for selecting different AI agents (extensible for future agents)
- **ChatGPT-like Interface**: Clean, modern chat interface with message history
- **Template Queries**: Pre-built queries for immediate testing of the Scientific Research Agent
- **Real-time Chat**: Interactive chat with typing indicators and proper message formatting
- **Session Management**: Persistent chat history during the session
- **Responsive Design**: Modern UI with custom CSS styling

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**:
   Create a `.env` file in the project root with your API keys:
   ```
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

3. **Run the Application**:
   ```bash
   streamlit run src/streamlit_main.py
   ```

4. **Access the Interface**:
   Open your browser to `http://localhost:8501`

## Available Agents

### Scientific Research Agent 🔬
- **Status**: Online
- **Capabilities**:
  - Search and analyze research papers
  - Extract key insights from academic documents
  - Provide detailed research summaries
  - Answer scientific questions with citations

### Future Agents (Coming Soon)
- **Data Analysis Agent** 📊
- **Code Review Agent** 💻

## Template Queries

The Scientific Research Agent comes with pre-built template queries for immediate testing:

- "What are the latest developments in machine learning for drug discovery?"
- "Find recent papers on quantum computing applications in cryptography"
- "Analyze the impact of climate change on marine ecosystems"
- "What are the current trends in renewable energy research?"
- "Search for papers on CRISPR gene editing techniques"
- "What are the latest findings in neuroscience and brain-computer interfaces?"
- "Find research on sustainable agriculture practices"
- "What are the recent advances in artificial intelligence ethics?"

## Usage

1. **Select an Agent**: Use the left sidebar to choose your preferred AI agent
2. **Start Chatting**: Type your query in the chat input or click on a template query
3. **View History**: All conversation history is maintained during your session
4. **Clear Chat**: Use the "Clear Chat History" button to start fresh

## Architecture

The application is built with:
- **Streamlit**: Web interface framework
- **LangGraph**: Agent workflow orchestration
- **Google Gemini**: Large language model
- **Custom CSS**: Modern, responsive styling

## Extending with New Agents

To add new agents:

1. Create your agent workflow in a new module
2. Add agent configuration to `AGENTS_CONFIG` in `streamlit_main.py`
3. Add template queries to `TEMPLATE_QUERIES`
4. Update the query processing logic in `process_research_query()`

## Troubleshooting

- **Import Errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
- **API Errors**: Verify your Google API key is correctly set in the `.env` file
- **Agent Offline**: Only the Scientific Research Agent is currently implemented

## Future Enhancements

- [ ] Add more AI agents (Data Analysis, Code Review, etc.)
- [ ] Implement conversation export functionality
- [ ] Add agent performance metrics
- [ ] Implement user authentication
- [ ] Add conversation search functionality
- [ ] Implement conversation sharing
