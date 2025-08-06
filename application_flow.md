# Application Flow

## Overview
This application is an AI Assistant web app built with Flask (Python backend) and a modern HTML/CSS/JS frontend. It allows users to interact with locally hosted LLMs (Large Language Models) via a chat interface, select different models, and receive structured AI responses.

---

## 1. Application Startup
- **Flask app** (`app.py`) starts and initializes all supported models using `initialize_models()` from `model.py`.
- Models are loaded and checked for availability. Any issues are printed to the console.

---

## 2. User Interface (Frontend)
- The main page (`index.html`) provides:
  - A chat window for conversation.
  - A dropdown to select the AI model.
  - A button to clear chat history.
- **CSS** (`styles.css`) ensures a modern, responsive look.
- **JavaScript** (`script.js`) handles:
  - Sending user messages to the backend.
  - Displaying AI and user messages.
  - Managing chat history in localStorage.
  - Showing loading/typing indicators.
  - Handling model selection and chat clearing.

---

## 3. Backend API Endpoints
- `/` (GET): Renders the chat UI and provides available models.
- `/generate` (POST):
  - Receives JSON: `{ "message": <user_message>, "model": <model_key> }`
  - Validates input and model selection.
  - Calls `get_model_response()` in `model.py` to generate a response.
  - Returns a JSON object: `{ "summary": ..., "response": ..., "duration": ... }` or an error.

---

## 4. Model Logic (`model.py`)
- **Model Initialization:** Loads and tests all models at startup.
- **Prompt Formatting:** Ensures the LLM receives a strict prompt to return only valid JSON with `summary` and `response` fields.
- **Response Parsing:** Handles various output formats, cleans and extracts the required fields, and ensures robust error handling.
- **Model Inference:** Uses the `ollama` library to interact with local models.

---

## 5. Configuration (`config.py`)
- Lists supported models and their friendly names.
- Sets max token limits and default model.

---

## 6. Model Checking Utility (`check_local_models.py`)
- Script to scan the `models/` directory for available models.
- Can be run standalone to verify/download models before starting the app.

---

## 7. User Flow
1. User opens the web app.
2. User selects a model and types a message.
3. Message is sent to `/generate` via AJAX.
4. Backend validates and processes the request, queries the selected model, and returns a structured response.
5. Frontend displays the summary and AI response in the chat window.
6. User can clear chat history or switch models at any time.

---

## 8. Error Handling
- Input validation on both frontend and backend.
- Graceful error messages for missing/invalid input or model errors.
- Robust JSON parsing and fallback strategies for model output.

---

## 9. Dependencies
- Flask, transformers, torch, pydantic, ollama (see `requirements.txt`).

---

## 10. Extensibility
- Add new models by updating `config.py` and ensuring they are available locally.
- UI and backend are modular for easy extension.