import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf
tf.get_logger().setLevel("ERROR")

from transformers import TFAutoModel,AutoTokenizer
from typing import List


MODEL_NAME='sentence-transformers/all-MiniLM-L6-v2'
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = TFAutoModel.from_pretrained(MODEL_NAME,from_pt=True)
def mean_pooling(model_op,attention_mask):
    token_embeddings=model_op.last_hidden_state
    attention_mask=tf.cast(attention_mask,tf.float32)
    mask_expanded=tf.expand_dims(attention_mask,-1)
    sum_embeddings=tf.reduce_sum(token_embeddings*mask_expanded,axis=1)
    sum_mask = tf.reduce_sum(mask_expanded, axis=1)
    return sum_embeddings / tf.maximum(sum_mask, 1e-9)

def embed_text(chunks: List[str]) -> List[tf.Tensor]:
    # One chunk -> one semantic vector.
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("Input must be a non-empty list of strings.")
    embeddings = []
    for chunk in chunks:
        if not isinstance(chunk, str) or not chunk.strip():
            raise ValueError("Each chunk must be a non-empty string.")

        encoded = tokenizer(chunk,padding=True,truncation=True,return_tensors="tf")
        with tf.device("/CPU:0"):
            model_output = model(**encoded)

        chunk_embedding = mean_pooling(model_output,encoded["attention_mask"])
        chunk_embedding = tf.math.l2_normalize(chunk_embedding, axis=1)
        embeddings.append(chunk_embedding[0])
    return embeddings


