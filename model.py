# model.py

import ollama
from pydantic import BaseModel, Field
import json
import os
from config import SUPPORTED_MODELS, MAX_NEW_TOKENS
import re # Added for regex parsing

# Define the output structure
class AIResponse(BaseModel):
    summary: str = Field(description="Summary of the user's message")
    sentiment: int = Field(description="Sentiment score from 0 (negative) to 100 (positive)")
    response: str = Field(description="Suggested response to the user")

# Cache loaded models for efficiency - will be populated on app startup
_loaded_models = {}

def initialize_models():
    """Initialize all models when Flask app starts"""
    print("🚀 Initializing Ollama models...")
    
    for model_key, model_name in SUPPORTED_MODELS.items():
        try:
            print(f"📥 Loading model: {model_name}")
            
            # Test if model is available by making a simple request
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": "Hello"}],
                options={
                    "num_predict": 1,
                    "temperature": 0.1
                }
            )
            
            _loaded_models[model_key] = model_name
            print(f"✅ Model loaded successfully: {model_name}")
            
        except Exception as e:
            print(f"❌ Error loading model {model_name}: {str(e)}")
            print(f"💡 Make sure the model is downloaded first using: python download_models.py")
    
    print(f"🎉 Model initialization complete. Loaded {len(_loaded_models)} models: {list(_loaded_models.keys())}")

def get_available_models():
    """Get list of successfully loaded models"""
    return list(_loaded_models.keys())

def format_prompt(model_key, system_prompt, user_prompt, format_instructions):
    """Format prompt based on Ollama model type"""
    # More explicit prompt format for better JSON generation
    return f"""System: {system_prompt}

User: {user_prompt}

CRITICAL: You must respond with ONLY valid JSON. Do not include any comments, extra text, or explanations outside the JSON.

Required JSON format (copy exactly):
{format_instructions}

Remember: No comments, no extra text, just pure JSON.

Assistant:"""

def get_format_instructions():
    """Get format instructions for JSON response"""
    return """{
  "summary": "brief summary of the question",
  "response": "detailed helpful answer with proper formatting"
}"""

def parse_ai_response(text, user_prompt=""):
    """Parse AI response and extract JSON"""
    try:
        # Look for JSON in the response
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start != -1 and end > start:
            json_text = text[start:end]
            
            # Try multiple parsing strategies
            parsed = None
            
            # Strategy 1: Try parsing as-is
            try:
                parsed = json.loads(json_text)
            except json.JSONDecodeError as e1:
                print(f"⚠️ First JSON parse attempt failed: {e1}")
                
                # Strategy 2: Try fixing common JSON issues
                try:
                    # Remove comments (// and /* */)
                    json_text = re.sub(r'//.*?$', '', json_text, flags=re.MULTILINE)
                    json_text = re.sub(r'/\*.*?\*/', '', json_text, flags=re.DOTALL)
                    
                    # Fix empty keys like {"key": "value",""}
                    json_text = json_text.replace(',""', '')
                    json_text = json_text.replace(',"",', ',')
                    json_text = json_text.replace(',""}', '}')
                    
                    # Fix missing quotes around keys
                    json_text = json_text.replace('"summary":', '"summary":')
                    json_text = json_text.replace('"response":', '"response":')
                    
                    # Replace literal \n with actual newlines
                    json_text = json_text.replace('\\n', '\n')
                    
                    # Remove any trailing commas
                    json_text = json_text.replace(',}', '}')
                    json_text = json_text.replace(',]', ']')
                    
                    # Remove null values and replace with default
                    json_text = json_text.replace('"sentiment": null', '"sentiment": 50')
                    json_text = json_text.replace('"sentiment":null', '"sentiment": 50')
                    
                    # Clean up extra whitespace
                    json_text = re.sub(r'\s+', ' ', json_text)
                    
                    parsed = json.loads(json_text)
                except json.JSONDecodeError as e2:
                    print(f"⚠️ Second JSON parse attempt failed: {e2}")
                    
                    # Strategy 3: Try to extract partial JSON
                    try:
                        # Look for individual fields with more flexible patterns
                        summary_match = re.search(r'"summary"\s*:\s*"([^"]*)"', json_text)
                        response_match = re.search(r'"response"\s*:\s*"([^"]*)"', json_text)
                        
                        if summary_match or response_match:
                            parsed = {
                                "summary": summary_match.group(1) if summary_match else f"User asked: {user_prompt}",
                                "response": response_match.group(1) if response_match else "I apologize, but I couldn't generate a complete response."
                            }
                        else:
                            raise Exception("No valid JSON fields found")
                            
                    except Exception as e3:
                        print(f"⚠️ Third JSON parse attempt failed: {e3}")
                        raise e3
            
            # Accept parsed if it has summary and response
            if parsed and all(key in parsed for key in ['summary', 'response']):
                response_text = str(parsed.get('response', ''))
                
                # If response contains JSON-like structure, try to extract readable text
                if response_text.startswith('{') and response_text.endswith('}'):
                    try:
                        # Try to parse the nested JSON and extract values
                        nested_json = json.loads(response_text)
                        if isinstance(nested_json, dict):
                            # Convert nested JSON to readable format
                            readable_response = ""
                            for key, value in nested_json.items():
                                readable_response += f"**{key}:** {value}\n\n"
                            response_text = readable_response.strip()
                    except:
                        # If nested JSON parsing fails, use the raw text
                        pass
                
                return {
                    "summary": str(parsed.get('summary', '')),
                    "response": response_text
                }
        
        # If no valid JSON found, create a structured response from the text
        lines = text.strip().split('\n')
        response_text = ""
        for line in lines:
            if line.strip() and not line.startswith('{') and not line.startswith('User:') and not line.startswith('Assistant:'):
                response_text += line.strip() + " "
        
        if not response_text.strip():
            response_text = "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
        
        return {
            "summary": f"User asked: {user_prompt}",
            "response": response_text.strip()
        }
        
    except Exception as e:
        print(f"⚠️ Error parsing response: {str(e)}")
        print(f"📝 Raw text: {text[:200]}...")
        
        # Return the raw text for frontend to handle markdown formatting
        return {
            "summary": "Response received",
            "response": text.strip()
        }

def get_model_response(model_key, system_prompt, user_prompt):
    """Get response from the specified Ollama model"""
    try:
        if model_key not in _loaded_models:
            raise Exception(f"Model {model_key} not loaded. Available models: {get_available_models()}")
        
        model_name = _loaded_models[model_key]
        prompt = format_prompt(model_key, system_prompt, user_prompt, get_format_instructions())
        
        print(f"📝 Using model: {model_name}")
        print(f"📝 Generated prompt: {prompt[:200]}...")
        
        # Use Ollama chat API for better response quality
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt + "\n\nPlease provide a helpful response in this exact JSON format:\n" + get_format_instructions()}
            ],
            options={
                "num_predict": MAX_NEW_TOKENS,
                "temperature": 0.7,
                "top_p": 0.9,
                "repeat_penalty": 1.2
            }
        )
        
        output = response['message']['content']
        print(f"🤖 Raw model output: {output[:200]}...")
        
        return parse_ai_response(output, user_prompt)
        
    except Exception as e:
        print(f"❌ Error generating response: {str(e)}")
        return {
            "summary": "Error occurred",
            "response": f"Sorry, an error occurred while generating the response: {str(e)}"
        }
