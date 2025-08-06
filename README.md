# AI Assistant (Flask + Local LLM)

## Overview
A modern web-based AI assistant that lets you chat with locally hosted Large Language Models (LLMs) using a beautiful, responsive interface. Built with Flask (Python), HTML/CSS/JS, and supports multiple models via Ollama.

---

## Features
- Chat with local LLMs (Gemma, Llama3, etc.)
- Model selection dropdown
- Clear chat history button
- Fast, responsive UI with local chat history
- Robust backend validation and error handling
- Easy extensibility for new models

---

## Application Flow
See [`application_flow.md`](application_flow.md) for a detailed flow diagram and explanation.

---

## Setup & Installation

### 1. Clone the Repository
```bash
# Clone this repo
$ git clone <your-repo-url>
$ cd first_flask
```

### 2. Install Python Dependencies
It is recommended to use a virtual environment.
```bash
# (Optional) Create and activate a virtual environment
python -m venv flask_environment
flask_environment\Scripts\activate  # On Windows
# Or: source flask_environment/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Download/Check Local Models
Ensure you have the required models downloaded locally.
```bash
# Check which models are available
python check_local_models.py
# (If needed) Download models as instructed in the console output
```

---

## Running the Application
```bash
python app.py
```
- The app will be available at: [http://localhost:5000](http://localhost:5000)

---

## Configuration
- **Supported models:** See `config.py` to add/remove models.
- **Default model:** Set in `config.py` (`DEFAULT_MODEL`).
- **Max tokens:** Set in `config.py` (`MAX_NEW_TOKENS`).

---

## Usage
1. Open the app in your browser.
2. Select a model from the dropdown.
3. Type your message and press Send (or Enter).
4. View the summary and AI response in the chat window.
5. Use the Clear Chat button to reset the conversation.

---

## Troubleshooting
- **No models found:** Run `python check_local_models.py` and follow instructions to download models.
- **Model loading errors:** Ensure models are downloaded and available in the `models/` directory.
- **Dependency issues:** Double-check your Python environment and `requirements.txt`.
- **Port in use:** Change the port in `app.py` if 5000 is occupied.

---

## Project Structure
```
first_flask/
├── app.py                  # Main Flask app
├── model.py                # Model logic and inference
├── config.py               # Model configuration
├── check_local_models.py   # Utility to check/download models
├── requirements.txt        # Python dependencies
├── static/
│   ├── script.js           # Frontend JS
│   └── styles.css          # Frontend CSS
├── templates/
│   └── index.html          # Main UI template
└── ...
```

---

## Dependencies
- Flask==3.0.3
- transformers==4.41.1
- torch (version depends on your system)
- pydantic==2.7.1
- ollama (Python package)

---

## Credits
- Built by [Your Name/Team]
- Uses [Ollama](https://ollama.com/) for local LLM inference
- UI inspired by modern chat apps

---

## License
[MIT License](LICENSE) (or your preferred license)
# NagarajuDupatiFlask_project_with_Local_LLMs
An AI chatbot flask application with local LLMs
