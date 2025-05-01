# backend/rewrite.py

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

model_id = "sshleifer/tiny-gpt2"  # Super lightweight, loads in seconds

print("Loading rewrite model...")

tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(model_id)

rewrite_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=100,
    do_sample=True,
    temperature=0.7,
)
print("Rewrite model loaded.")

def rewrite_text(text: str, tone: str = "confident") -> str:
    prompt = f"Rewrite the following text to sound more {tone}:\n\n{text}"
    result = rewrite_pipeline(prompt)
    return result[0]["generated_text"].strip()