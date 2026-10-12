import torch
import faiss
import numpy as np
from src.embeddings.codebert import get_tokenizer, get_model
from src.config import *

def embed_functions(functions, batch_size=16, device=DEVICE):
    tokenizer = get_tokenizer()
    model = get_model()
    model.to(device)
    model.eval()

    for i in range(0, len(functions), batch_size):
        batch = functions[i:i+batch_size]

        codes = [f["code"] for f in batch]

        inputs = tokenizer(
            codes,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(device)

        with torch.inference_mode():
            outputs = model(**inputs)

        # CLS embedding
        embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()

        for f, emb in zip(batch, embeddings):
            yield f, emb.astype("float32")



def build_index(stream):
    dim = 768
    base = faiss.IndexFlatIP(dim)
    index = faiss.IndexIDMap2(base)

    id_map = {}

    for idx, (f, emb) in enumerate(stream):
        emb = emb.reshape(1, -1).astype("float32")
        faiss.normalize_L2(emb)

        index.add_with_ids(
            emb,
            np.array([idx], dtype=np.int64)
        )

        id_map[idx] = f

    return index, id_map