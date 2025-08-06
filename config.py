# config.py

# Local Ollama models available on the system
GEMMA2_2B = "gemma2:2b"                          # ~2B parameters
#LLAMA3_2_1B = "llama3.2:1b"                      # ~1B parameters  
LLAMA3_2_3B = "llama3.2:3b"                      # ~3B parameters
# QWEN2_5_1_5B = "qwen2.5:1.5b"                    # ~1.5B parameters

# Supported models dictionary with friendly names
SUPPORTED_MODELS = {
    "gemma2-2b": GEMMA2_2B,
    #"llama3.2-1b": LLAMA3_2_1B,
    "llama3.2-3b": LLAMA3_2_3B,
    # "qwen2.5-1.5b": QWEN2_5_1_5B,
}

# Model parameter counts for reference
MODEL_PARAMS = {
    "gemma2-2b": "2B",
    #"llama3.2-1b": "1B",
    "llama3.2-3b": "3B", 
    # "qwen2.5-1.5b": "1.5B",
}

# Max new tokens for local generation
MAX_NEW_TOKENS = 2048  # Increased from 256 to allow longer responses

# Default model to use (llama3.2:1b for good balance of speed and performance)
DEFAULT_MODEL = "llama3.2-3b"
