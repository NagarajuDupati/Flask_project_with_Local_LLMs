import os
import json
from pathlib import Path

def check_local_models():
    """Check which models are available locally"""
    models_dir = Path("models")
    
    if not models_dir.exists():
        print("❌ No 'models' directory found!")
        return []
    
    # Check for Hugging Face cache structure
    cache_dir = models_dir / "hub"
    if cache_dir.exists():
        print("🔍 Checking Hugging Face cache directory...")
        return check_hf_cache(cache_dir)
    
    # Check for direct model directories
    print("🔍 Checking for model directories...")
    return check_direct_models(models_dir)

def check_hf_cache(cache_dir):
    """Check Hugging Face cache structure"""
    models = []
    
    # Look for model directories in the cache
    for item in cache_dir.iterdir():
        if item.is_dir():
            # Check if it contains model files
            model_files = list(item.rglob("*.bin")) + list(item.rglob("*.safetensors"))
            if model_files:
                model_name = str(item.name)
                models.append(model_name)
                print(f"  ✅ Found: {model_name}")
    
    return models

def check_direct_models(models_dir):
    """Check for direct model directories"""
    models = []
    
    for item in models_dir.iterdir():
        if item.is_dir():
            # Check if it contains model files
            model_files = list(item.rglob("*.bin")) + list(item.rglob("*.safetensors"))
            if model_files:
                model_name = str(item.name)
                models.append(model_name)
                print(f"  ✅ Found: {model_name}")
    
    return models

def main():
    print("🔍 Scanning for locally available models...")
    print(f"📁 Looking in: {os.path.abspath('models')}")
    
    local_models = check_local_models()
    
    if not local_models:
        print("\n❌ No models found locally!")
        print("💡 Run 'python download_models.py' to download models first")
        return
    
    print(f"\n📊 Found {len(local_models)} models locally:")
    for i, model in enumerate(local_models, 1):
        print(f"  {i}. {model}")
    
    # Save to a file for easy access
    with open("local_models.json", "w") as f:
        json.dump(local_models, f, indent=2)
    
    print(f"\n💾 Model list saved to: local_models.json")
    
    return local_models

if __name__ == "__main__":
    main() 