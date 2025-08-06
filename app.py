# app.py

from flask import Flask, request, jsonify, render_template
from model import get_model_response, initialize_models, get_available_models
import time
from config import SUPPORTED_MODELS
import json

app = Flask(__name__)

# Initialize models when app starts
print("🚀 Starting Flask app and initializing models...")
initialize_models()

def flatten_json(obj):
    if isinstance(obj, dict):
        result = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                result.append(f"{k}:\n{flatten_json(v)}")
            else:
                result.append(f"{k}: {v}")
        return '\n'.join(result)
    elif isinstance(obj, list):
        return '\n'.join(flatten_json(item) for item in obj)
    else:
        return str(obj)

def try_parse_json(response):
    import json, re
    try:
        return json.loads(response.strip())
    except Exception as e:
        print(f"⚠️ JSON parse failed: {e} | Raw: {repr(response)}")
        
        # Try to clean the response first
        cleaned_response = response.strip()
        
        # Remove any leading/trailing non-JSON text
        start_idx = cleaned_response.find('{')
        end_idx = cleaned_response.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_part = cleaned_response[start_idx:end_idx + 1]
            try:
                # Try to parse the extracted JSON
                return json.loads(json_part)
            except Exception as e2:
                print(f"⚠️ Extracted JSON parse failed: {e2} | Extracted: {repr(json_part)}")
        
        # If all else fails, try to extract summary and response using regex
        summary_match = re.search(r'"summary"\s*:\s*"([^"]*)"', response, re.IGNORECASE)
        response_match = re.search(r'"response"\s*:\s*"([^"]*)"', response, re.IGNORECASE | re.DOTALL)
        
        summary = summary_match.group(1) if summary_match else "Could not parse summary."
        response_text = response_match.group(1) if response_match else response
        
        return {"summary": summary, "response": response_text}

def clean_model_response(parsed):
    def fix_quotes(text):
        if isinstance(text, str):
            return text.strip('"')
        return text
    
    summary = fix_quotes(parsed.get("summary", ""))
    response = parsed.get("response", "")
    
    # If response is a dict, convert to string
    if isinstance(response, dict):
        response = json.dumps(response, ensure_ascii=False)
    elif response is None:
        response = ""
    elif isinstance(response, str):
        # Clean up the response string
        response = response.strip()
        
        # Remove leading/trailing quotes if present
        response = response.strip('"')
        
        # Handle escaped characters
        response = response.replace('\\n', '\n')
        response = response.replace('\\"', '"')
        response = response.replace('\\t', '\t')
        
        # Try to unescape and parse if it looks like JSON
        if (response.startswith("{") and response.endswith("}")) or \
           (response.startswith("[") and response.endswith("]")):
            try:
                # Try to parse and pretty-print
                response_obj = json.loads(response)
                response = json.dumps(response_obj, ensure_ascii=False)
            except Exception:
                # If parsing fails, just use the cleaned string
                pass
        else:
            response = fix_quotes(response)
    
    return {
        "summary": summary,
        "response": response
    }

@app.route("/", methods=["GET"])
def index():
    available_models = get_available_models()
    return render_template("index.html", models=available_models)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    
    # Debug: Print received data
    print(f"🔍 Received data: {data}")
    
    user_message = data.get('message')
    model = data.get('model')
    
    # Debug: Print extracted values
    print(f"📝 User message: '{user_message}'")
    print(f"🤖 Selected model: '{model}'")
    available_models = get_available_models()
    print(f"📋 Available models: {available_models}")
    print(f"✅ Model in available models: {model in available_models}")
    
    if not user_message or not model or model not in available_models:
        error_msg = f"Missing or invalid message or model selection. Received: message='{user_message}', model='{model}'. Available models: {available_models}"
        print(f"❌ Validation failed: {error_msg}")
        return jsonify({"error": error_msg}), 400

    system_prompt = (
        "You are an AI assistant. Your ONLY response should be a single valid JSON object, with no extra text, no markdown, no comments, no explanations, and no additional fields. "
        "The JSON object must have exactly these two keys: \"summary\" and \"response\".\n"
        "Example:\n"
        "{\"summary\": \"A brief summary of the user's question\", \"response\": \"A detailed, helpful answer.\"}\n"
        "Do not include any other text, formatting, or fields. If you cannot answer, still return a valid JSON object with both keys, and leave the values empty."
    )
    start_time = time.time()
    try:
        result = get_model_response(model, system_prompt, user_message)
        # If result is a string (raw model output), parse and clean it:
        if isinstance(result, str):
            parsed = try_parse_json(result)
            cleaned = clean_model_response(parsed)
        else:
            cleaned = clean_model_response(result)
        print(f"🤖 Model response: {cleaned}")
        # Use cleaned for your API response as well
        cleaned['duration'] = time.time() - start_time
        return jsonify(cleaned)
    except Exception as e:
        return jsonify({"error": "Internal error: " + str(e)}), 500

if __name__ == "__main__":
    print("🌐 Starting Flask app...")
    print("📱 AI Assistant will be available at: http://localhost:5000")
    print("🔗 Local URL: http://127.0.0.1:5000")
    print("🌍 Network URL: http://[your-network-ip]:5000 (for other devices)")
    app.run(host='0.0.0.0', port=5000, debug=True)
