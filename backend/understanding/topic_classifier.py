from sklearn.cluster import KMeans
import numpy as np
def topic_classifer(chunk_embeddings:list[np.ndarray])->list[int]:
    if not isinstance(chunk_embeddings,list) or not chunk_embeddings:
        raise ValueError("Chunk_embeddings must be a non-empty list.")
    try:
        X=np.vstack(chunk_embeddings)
    except Exception:
        raise ValueError("Embeddings must be array-like with same dimensions.")
    emb_len=len(chunk_embeddings)
    if emb_len<=5:
        k=1
    elif emb_len<=12:
        k=2
    elif emb_len<=25:
        k=3
    else:
        k=5

    km=KMeans(n_clusters=k,init="k-means++",n_init=10,random_state=69)
    labels=km.fit_predict(X)

    return labels.tolist()