import re
from collections import defaultdict
import json
def parse_key_file(filepath):
    """
    Parse the key file to get correct values for dev data
    """
    key_dict = {}
    with open(filepath, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                key_dict[parts[0]] = int(parts[1])
    return key_dict
def parse_english_file(filepath, key_dict=None):
    """
    Parse English train or dev files and build a dictionary structure:
    dict -> users -> words -> different times the word is used

    Each word usage includes: session_data, line_id, days, word features, etc.
    Now also includes the full phrase the word was part of.
    
    Args:
        filepath: Path to the English train or dev file
        key_dict: Dictionary of line_id -> correct_value for dev files
    """
    from collections import defaultdict
    import re

    users_dict = defaultdict(lambda: defaultdict(list))

    current_user = None
    current_session_data = {}
    current_phrase_words = []  # list of (line_id, word, pos, features, full line parts)

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            if line.startswith("# user:"):
                # Before switching users, assign phrase to existing entries
                for word_entry in current_phrase_words:
                    line_id, word_text, pos, features, parts = word_entry
                    correct = None
                    if len(parts) > 6:
                        correct = int(parts[6])
                    elif key_dict and line_id in key_dict:
                        correct = key_dict[line_id]

                    word_usage = {
                        "line_id": line_id,
                        "word": word_text,
                        "pos": pos,
                        "features": features,
                        "correct": correct,
                        "days": current_session_data.get("days"),
                        "session": current_session_data.get("session"),
                        "format": current_session_data.get("format"),
                        "time": current_session_data.get("time"),
                        "phrase": [entry[1] for entry in current_phrase_words]  # just the word_texts
                    }

                    if current_user:
                        users_dict[current_user][word_text].append(word_usage)

                current_phrase_words = []

                # New user line
                user_match = re.search(r"user:(\S+)", line)
                if user_match:
                    current_user = user_match.group(1)

                    days_match = re.search(r"days:(\S+)", line)
                    session_match = re.search(r"session:(\S+)", line)
                    format_match = re.search(r"format:(\S+)", line)
                    time_match = re.search(r"time:(\S+)", line)

                    current_session_data = {
                        "days": float(days_match.group(1)) if days_match else None,
                        "session": session_match.group(1) if session_match else None,
                        "format": format_match.group(1) if format_match else None,
                        "time": time_match.group(1) if time_match else None
                    }

            elif not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 4:
                    line_id = parts[0]
                    word_text = parts[1].lower()
                    pos = parts[2]
                    features_str = parts[3]

                    features = {}
                    if features_str:
                        for kv in features_str.split("|"):
                            if "=" in kv:
                                k, v = kv.split("=", 1)
                                features[k] = v

                    current_phrase_words.append((line_id, word_text, pos, features, parts))

        # Handle any remaining words after the last user
        for word_entry in current_phrase_words:
            line_id, word_text, pos, features, parts = word_entry
            correct = None
            if len(parts) > 6:
                correct = int(parts[6])
            elif key_dict and line_id in key_dict:
                correct = key_dict[line_id]

            word_usage = {
                "line_id": line_id,
                "word": word_text,
                "pos": pos,
                "features": features,
                "correct": correct,
                "session_data": current_session_data.copy(),
                "days": current_session_data.get("days"),
                "session": current_session_data.get("session"),
                "format": current_session_data.get("format"),
                "time": current_session_data.get("time"),
                "phrase": [entry[1] for entry in current_phrase_words]
            }

            if current_user:
                users_dict[current_user][word_text].append(word_usage)

    return users_dict
def analyze_word_until_line_id(users_dict, user_id, word, target_line_id):
    if user_id not in users_dict or word not in users_dict[user_id]:
        raise ValueError("User or word not found in data.")

    uses = users_dict[user_id][word]
    index = next((i for i, u in enumerate(uses) if u["line_id"] == target_line_id), None)
    if index is None:
        raise ValueError("line_id not found for this user and word.")
    trimmed_uses = uses[:index + 1]

    # Extract days and corrects
    used_days = [u["days"] for u in trimmed_uses if u["days"] is not None]
    intervals = [
        used_days[i] - used_days[i - 1]
        for i in range(1, len(used_days))
    ]
    dev_data[user_id][word][index]["interval"]=intervals
    dev_data[user_id][word][index]["user"]=user_id

    output_line = dev_data[user_id][word][index]
    with open("output.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(output_line, ensure_ascii=False) + "\n")
def merge_train_and_dev(train_data, dev_data):
    merged = defaultdict(lambda: defaultdict(list))
    for user, words in train_data.items():
        for word, uses in words.items():
            merged[user][word].extend(uses)
    for user, words in dev_data.items():
        for word, uses in words.items():
            merged[user][word].extend(uses)
    return merged
def com(dev_data,users_dict):
    for users in dev_data.keys():
        for words in dev_data[users].keys():
            for i in range(len(dev_data[users][words])):
                identification=dev_data[users][words][i]["line_id"]
                analyze_word_until_line_id(users_dict, users, words, identification)
            




train_data = parse_english_file("EnglishTrain.txt")
key_dict = parse_key_file("EnglishDevKey.txt")
dev_data = parse_english_file("EnglishDev.txt", key_dict)
users_dict = merge_train_and_dev(train_data, dev_data)
result = analyze_word_until_line_id(users_dict, user_id="3+LbHrV9", word="work", target_line_id="6Qul1Xig0302")
com(dev_data,users_dict)
print(users_dict["3+LbHrV9"]["work"])


   
    




