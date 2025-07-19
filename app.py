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


from collections import defaultdict

def get_all_word_review_days(dev_data, train_data, key):
    # Structure to store results
    results_by_word = defaultdict(dict)  # word -> dev_id -> result dict

    # Prebuild a mapping from dev_id to (user, word, phrase, day)
    dev_id_map = {}
    for user_id, user_info in dev_data.items():
        for phrase, phrase_events in user_info["phrases"].items():
            for event in phrase_events:
                session_day = event["session_data"]["days"]
                for word, instances in event["words"].items():
                    for instance in instances:
                        line_id = instance["line_id"]
                        dev_id_map[line_id] = {
                            "user": user_id,
                            "word": word,
                            "phrase": phrase,
                            "day": session_day,
                            "event": event,
                        }

    # For each dev_id in key, compute retention info
    for dev_id in key.keys():
        if dev_id not in dev_id_map:
            print(f"Dev ID {dev_id} not found in dev data.")
            continue

        info = dev_id_map[dev_id]
        target_user = info["user"]
        target_word = info["word"]
        target_phrase = info["phrase"]
        target_day = info["day"]

        # Collect dev days before current dev_id
        dev_days = []
        early_dev_flag = True
        for phrase, phrase_events in dev_data[target_user]["phrases"].items():
            for event in phrase_events:
                if not early_dev_flag:
                    break
                for word, instances in event["words"].items():
                    for instance in instances:
                        if instance["line_id"] == dev_id:
                            early_dev_flag = False
                            break
                        if word == target_word:
                            dev_days.append(event["session_data"]["days"])
                    if not early_dev_flag:
                        break
                if not early_dev_flag:
                    break
            if not early_dev_flag:
                break

        # Collect all train days for the target user-word
        train_days = []
        if target_user in train_data:
            for phrase, phrase_events in train_data[target_user]["phrases"].items():
                for event in phrase_events:
                    for word, instances in event["words"].items():
                        if word == target_word:
                            train_days.extend([event["session_data"]["days"]] * len(instances))

        # Combine train days and dev days before current, plus current day
        combined_days = train_days + dev_days + [target_day]
        combined_days = sorted(combined_days)

        # Calculate intervals
        intervals = []
        for i in range(len(combined_days) - 1):
            diff = round(combined_days[i+1] - combined_days[i], 2)
            intervals.append(diff)

        # Prepare result dict
        result = {
            "user": target_user,
            "word": target_word,
            "dev_day_for_id": target_day,
            "dev_days_before_id": sorted(dev_days),
            "train_days": sorted(train_days),
            "combined_days": combined_days,
            "interval": intervals,
            "retention": key.get(dev_id, None),
        }

        # Store result keyed by word and dev_id
        results_by_word[target_word][dev_id] = result

    return results_by_word








def theExperiment(train, dev,minRecalls, maxRecalls):
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

                

results = get_all_word_review_days(dev, train, key)

#word = "books"
#dev_id = "7DRdO0Iq0404"  # 
#if word in results and dev_id in results[word]:
    #print(results[word][dev_id])


def analyze_retention_accuracy(results_by_word):
    num = 0
    dem = 0

    for word, dev_results in results_by_word.items():
        for dev_id, result in dev_results.items():
            retention_val = result.get("retention")
            if retention_val is None:
                continue  # skip if no retention info

            if int(retention_val) == 0:
                num += 1
            dem += 1

    accuracy = num / dem if dem > 0 else 0
    return accuracy, num, dem

accuracy, num_correct, total = analyze_retention_accuracy(results)
print(f"Accuracy: {accuracy:.4f} ({num_correct} out of {total})")

