from transformers import AutoTokenizer, AutoModel
import torch
from src.config import TOKENIZER_NAME, DEVICE

_tokenizer = None
_model = None


def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
    return _tokenizer


def get_model():
    global _model
    if _model is None:
        _model = AutoModel.from_pretrained(TOKENIZER_NAME)
        _model.to(DEVICE)
        _model.eval()
    return _model