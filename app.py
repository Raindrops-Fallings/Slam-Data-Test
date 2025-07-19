import pandas as pd              
import numpy as np               
from collections import defaultdict
import re

import re
from collections import defaultdict
def parse_key(filepath):
    dictionarial={}
    with open(filepath, "r") as inFile:
        for line in inFile:
            parts=line.split()
            dictionarial[parts[0]]=parts[1]
    return dictionarial



key=parse_key("EnglishDevKey.txt")


def store_phrase(user_data, user_id, phrase_words, session_data):
    phrase_key = " ".join(w["text"] for w in phrase_words)
    phrase_dict = {
        "session_data": session_data.copy(),
        "words": defaultdict(list)
    }
    for w in phrase_words:
        phrase_dict["words"][w["text"]].append({
            "line_id": w["line_id"],
            "correct": w["correct"],
            "pos": w["pos"],
            "features": w["features"]
        })
    user_data[user_id]["phrases"].setdefault(phrase_key, []).append(phrase_dict)
def count_user_id_lines(filepath):
    count = 0
    # Regex pattern matching your line IDs:  
    # Starts with alphanumeric string with letters + numbers, no spaces, followed by space
    pattern = re.compile(r"^[A-Za-z0-9]+")  

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line=="" and not line.startswith("#"):
                count+=1  
    #print("COUNT", count)
    return count

def parse_file(filepath):
  
    user_data = defaultdict(lambda: {"phrases": defaultdict(list)})
    current_user = None
    session_data = {}
    phrase_lines = []


    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("# user:"):
                current_user = re.search(r"user:(\S+)", line).group(1)
                session_data = {
                    "days": float(re.search(r"days:(\S+)", line).group(1)),
                    "session": re.search(r"session:(\S+)", line).group(1),
                    "format": re.search(r"format:(\S+)", line).group(1),
                    "time": (re.search(r"time:(\S+)", line).group(1))
                }
                phrase_lines = []

            elif line =="" or (line.startswith("#") and not line.startswith("# prompt:")):

                if phrase_lines:
                    phrase_words = []
                    if filepath=="EnglishTrain.txt":
                        correct_index=6
                    else:
                        correct_index=None

                    for l in phrase_lines:
                        parts = l.split()
                        line_id = parts[0]
                        word_text = parts[1].lower()
                        pos = parts[2]
                        features_str = parts[3]

                        if correct_index is not None and len(parts) > correct_index:
                            correct = int(parts[correct_index])
                        elif filepath=="EnglishDev.txt":
                            correct=key[line_id]
                            
                     

                        features = {k: v for kv in features_str.split("|") if "=" in kv for k, v in [kv.split("=", 1)]}

                        phrase_words.append({
                            "line_id": line_id,
                            "text": word_text,
                            "correct": correct,
                            "pos": pos,
                            "features": features
                        })

                    if current_user and phrase_words:
                        store_phrase(user_data, current_user, phrase_words, session_data)
                    phrase_lines = []

            else:
                phrase_lines.append(line)

    return user_data


def parse_key(filepath):
    dictionarial={}
    with open(filepath, "r") as inFile:
        for line in inFile:
            parts=line.split()
            dictionarial[parts[0]]=parts[1]
    return dictionarial

                
            



def count_unique_and_duplicate_user_phrases(data):
    unique_user_phrases = set()  # (user, phrase) pairs we've seen
    duplicate_count = 0
    unique_count = 0
    unique_word_count = 0
    duplicate_word_count = 0

    for user_id, user_info in data.items():
        for phrase, phrase_events in user_info["phrases"].items():
            # Check if this user-phrase combo seen before
            user_phrase_key = (user_id, phrase)
            # Count total occurrences of this phrase for user
            occurrences = len(phrase_events)
            # Count words in phrase (phrase is a string of words separated by spaces)
            word_count = len(phrase.split())

            if user_phrase_key not in unique_user_phrases:
                unique_user_phrases.add(user_phrase_key)
                unique_count += 1
                unique_word_count += word_count
                # duplicates are any additional occurrences beyond the first
                duplicate_count += (occurrences - 1) if occurrences > 1 else 0
                duplicate_word_count += word_count * (occurrences - 1) if occurrences > 1 else 0
            else:
                # If this pair was somehow encountered again outside the above logic (rare)
                duplicate_count += occurrences
                duplicate_word_count += word_count * occurrences

    print(f"Unique (user, phrase) pairs: {unique_count}")
    print(f"Duplicate (user, phrase) pairs: {duplicate_count}")
    print(f"Total words in unique phrases: {unique_word_count}")
    print(f"Total words in duplicate phrases: {duplicate_word_count}")

    return {
        "unique_pairs": unique_count,
        "duplicate_pairs": duplicate_count,
        "unique_word_count": unique_word_count,
        "duplicate_word_count": duplicate_word_count
    }

def retention_interval(user,word):
    for phrase in train[str(user)]["phrases"].keys():
        for i in range(len(dev[str(users)]["phrases"][str(phrase)])):
            for words in dev[str(users)]["phrases"][str(phrase)][i]["words"].keys():





def theExperiment(train, dev, minRecalls, maxRecalls):
    ratioNumerator=0
    ratioDenominator=0
    for users in dev.keys():
        for phrase in dev[str(users)]["phrases"].keys():
            for i in range(len(dev[str(users)]["phrases"][str(phrase)])):
                for words in dev[str(users)]["phrases"][str(phrase)][i]["words"].keys():
                    for j in range(len(dev[str(users)]["phrases"][str(phrase)][i]["words"][str(words)])):
                        if int(dev[str(users)]["phrases"][str(phrase)][i]["words"][str(words)][j]["correct"])==0:
                            ratioNumerator+=1
                            ratioDenominator+=1
                        
                        else:
                            ratioDenominator+=1

    ratio=ratioNumerator/ratioDenominator
    print(ratio, ratioNumerator,ratioDenominator)    


    

train=parse_file("EnglishTrain.txt")
dev=parse_file("EnglishDev.txt")
theExperiment(train,dev,0,0)
n=0
d=0
for i in key.values():
    if int(i)==0:
        n+=1
        d+=1
    else:
        d+=1
print(n/d,n,d)
#print(len(key.values()))
doop=0
#print(dev["0hfSZZPH"]["phrases"]["i have a radio and a computer"])
for users in dev.keys():
        for phrase in dev[str(users)]["phrases"].keys():
            for i in range (len((dev[str(users)]["phrases"][str(phrase)]))):
                doop+=len(phrase.split())
                
#print("doop",doop)

empty_word_entries = 0
for users in dev.keys():
    for phrase in dev[str(users)]["phrases"].keys():
        for i in range (len(dev[str(users)]["phrases"][str(phrase)])):
            #print(dev[str(users)]["phrases"][str(phrase)][i]["words"])
            break

#count_unique_and_duplicate_user_phrases(dev)