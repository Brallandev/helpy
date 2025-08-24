# Diagnose-Bot

Diagnose-Bot is a subproject designed to facilitate automated pre-diagnosis and triage tasks using AI-powered agents and a modular API structure. This project is part of a larger auto-triage system and is focused on streamlining the initial stages of medical or technical diagnosis by leveraging intelligent automation.

## Project Structure

- **app.py**: Main entry point for running the Diagnose-Bot service.
- **requirements.txt**: Lists all Python dependencies required to run the project.
- **Dockerfile**: Containerization setup for easy deployment.
- **.env / .env.example**: Environment variable configuration files.
- **src/**: Source code directory containing all modules and logic.
  - **config.py**: General configuration for the application.
  - **api/**: Contains API endpoints and schemas.
    - **answers.py**: Handles answer-related API logic.
    - **config.py**: API-specific configuration.
    - **questions.py**: Handles question-related API logic.
    - **schemas.py**: Pydantic schemas for request/response validation.
  - **model/**: AI agent logic and prompt management.
    - **agents.py**: Defines and manages AI agents.
    - **prompts.py**: Stores and manages prompt templates for agents.
    - **schemas.py**: Data models for agent interactions.
  - **utils/**: Utility modules for configuration, agent registry, and string parsing.
    - **agent_registry.py**: Registers and manages available agents.
    - **config_manager.py**: Handles configuration loading and management.
    - **str_parsing.py**: String parsing utilities.

## API Usage and Flow

1. **Calling the APIs**:
   - The main API endpoints are defined in `src/api/` (e.g., `questions.py`, `answers.py`).
   - These endpoints are typically called via HTTP requests (e.g., using `requests` in Python or any HTTP client).
   - Example (Python):
     ```python
     import requests
     response = requests.post("http://localhost:8000/your-endpoint", json={"key": "value"})
     print(response.json())
     ```
   - The APIs expect JSON payloads that conform to the schemas defined in `schemas.py`.

2. **Expected Flow**:
   - A user or system submits a question or case to the API (e.g., symptoms, technical issue).
   - The API validates the input and forwards it to the appropriate AI agent.
   - The agent processes the input using prompt templates and AI models, generating a pre-diagnosis or triage suggestion.
   - The API returns the agent's response, which can be used for further action or escalation.


## AI Model, OpenRouter, and Their Role

- **Model Used:**
  - Diagnose-Bot leverages advanced Large Language Models (LLMs) to interpret and process user input. The specific model used can be configured, but the system is designed to work seamlessly with state-of-the-art models accessible via OpenRouter.
  - These models are responsible for understanding context, generating relevant questions, and providing pre-diagnosis suggestions based on the input data.

- **Importance of OpenRouter:**
  - OpenRouter acts as a gateway to a variety of powerful AI models, enabling Diagnose-Bot to access the latest advancements in natural language processing without being tied to a single provider.
  - By integrating with OpenRouter, the system benefits from:
    - Flexible model selection and easy upgrades as new models become available.
    - Enhanced reliability and scalability for production use.
    - Simplified API management and authentication for secure, compliant deployments.

- **AI Tools and Their Role:**
  - The AI agents in `model/agents.py` are responsible for interpreting input data and generating intelligent responses using the selected LLM via OpenRouter.
  - Prompt templates in `model/prompts.py` ensure that the agents provide contextually relevant and accurate suggestions.
  - The agent registry and configuration utilities allow for easy extension and management of different AI tools.
  - These AI tools are crucial for pre-diagnosis tasks, as they:
    - Automate the initial assessment, reducing manual workload.
    - Provide consistent and rapid triage decisions.
    - Help prioritize cases based on urgency or complexity.

## Importance in Pre-Diagnose Tasks

Diagnose-Bot's AI-driven approach enables organizations to:
- Quickly filter and prioritize incoming cases.
- Offer preliminary guidance before human intervention.
- Improve efficiency and accuracy in the triage process.

---

For setup instructions, environment configuration, and deployment, refer to the `Dockerfile`, `.env.example`, and `requirements.txt` files. For further customization, explore the modular codebase in the `src/` directory.
