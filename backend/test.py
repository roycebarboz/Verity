import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

name = "../models/Qwen3-Reranker-0.6B"
tok = AutoTokenizer.from_pretrained(name, padding_side="left")
model = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float16).to("mps").eval()

yes, no = tok.convert_tokens_to_ids("yes"), tok.convert_tokens_to_ids("no")
prefix = '<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
inst = "Given a web search query, retrieve relevant passages that answer the query"

def rerank(query, docs):
    texts = [f"{prefix}<Instruct>: {inst}\n<Query>: {query}\n<Document>: {d}{suffix}" for d in docs]
    inp = tok(texts, padding=True, truncation=True, max_length=4096, return_tensors="pt").to("mps")
    with torch.no_grad():
        logits = model(**inp).logits[:, -1, :]
    return torch.softmax(torch.stack([logits[:, no], logits[:, yes]], 1), dim=1)[:, 1].tolist()

print(rerank("capital of France?", ["Paris is the capital of France.", "Bananas are yellow."]))