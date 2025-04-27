from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Load everything once when the app starts
print("Loading model...")
##model_id = "mistralai/Mistral-7B-v0.1"  Swap back to this after testing, issues with debugging
model_id = "microsoft/phi-2" 

tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)

rewrite_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=100,
    do_sample=True,
    temperature=0.7,
)
print("Model loaded!")

def rewrite_text(text, tone="confident"):
    prompt = f"You are a communication coach. Rewrite the following text to sound more {tone}:\n\n{text}"
    result = rewrite_pipeline(prompt)
    return result[0]["generated_text"].strip()
