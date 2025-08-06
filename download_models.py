import ollama

models_to_pull = ['gemma2:2b', 'llama3.2:3b']  # 'llama3.2:1b' commented out


for model in models_to_pull:
    try:
        print(f"📥 Pulling {model}...")
        status = ollama.pull(model)
        if status.get('status') == 'success':
            print(f"✅ Successfully pulled {model}")
        else:
            print(f"⚠️  Pulled {model} with status: {status.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Failed to pull {model}: {str(e)}")

print("🎉 Download process completed!")
