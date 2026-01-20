from collections import defaultdict,Counter
from nltk.corpus import stopwords
import re
def group_by_labels(labels:list[int],chunks:list[str])->dict[int,list[str]]:
    if len(chunks)!=len(labels):
        raise ValueError("Chunks and labels must be of same length.")
    my_dict=defaultdict(list)
    for label,chunk in zip(labels,chunks):
        my_dict[label].append(chunk)
    return my_dict

def extract(my_dict:dict[int,list[str]],top_k:int=5)->dict[int,list[str]]:
    if not my_dict:
        raise ValueError("Chunks have not been grouped properly")
    final_dict=defaultdict(list)
    stop_words = set(stopwords.words("english"))
    for label,chunks in my_dict.items():
        text=" ".join(chunks).lower()
        text=re.sub(r"[^a-z\s]",' ',text)
        words=text.split()
        words=[word for word in words if word not in stop_words and len(word)>2]
        word_counts=Counter(words)
        top_words=[word for word,_ in word_counts.most_common(top_k)]
        final_dict[label]=top_words
    return final_dict
def keyword_extractor(labels:list[int],chunks:list[str],top_k:int=5)->dict[int,list[str]]:
    grouped_dict=group_by_labels(labels,chunks)
    final_dict=extract(grouped_dict,top_k)
    return final_dict