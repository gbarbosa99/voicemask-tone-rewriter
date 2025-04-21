from transformers import pipeline

# Load the text2text model once when the script is imported
rewrite_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

def rewrite_text(text, tone="confident"):
    prompt = f"You are a communication coach. Your job is to improve people's speech. Rewrite this to sound more {tone} and direct:\n\n{text}"
    
    result = rewrite_pipeline(prompt, max_new_tokens=100)

    # Return the rewritten text
    return result[0]["generated_text"].strip()
