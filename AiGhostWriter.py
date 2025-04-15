import spacy
import nltk
from nltk.corpus import wordnet
import random
import os
import re

nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model for spaCy...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def analyze_sentence_length(writing_samples):
    """Analyzes the average sentence length from writing samples."""
    sample_docs = [nlp(sample) for sample in writing_samples.split('\n') if sample.strip()]
    total_sentences = 0
    total_tokens = 0
    for doc in sample_docs:
        for sent in doc.sents:
            total_sentences += 1
            total_tokens += len(sent)
    if total_sentences > 0:
        return total_tokens / total_sentences
    return 0

def get_synonyms(word, pos=None):
    synonyms = set()
    for syn in wordnet.synsets(word, pos=pos):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
    if word in synonyms:
        synonyms.remove(word)
    return list(synonyms)

def transform_to_human_like(ai_text, writing_samples):
    avg_sentence_length = analyze_sentence_length(writing_samples)
    print(f"Average sentence length in samples: {avg_sentence_length:.2f} words")

    transformed_text = []
    human_like_phrases = []
    insertion_probability = 0.6  # Adjusted probability
    split_probability = 0.2
    long_sentence_threshold = 20
    synonym_replacement_probability = 0.15 # Probability of replacing a word with a synonym

    script_dir = os.path.dirname(os.path.abspath(__file__))
    phrases_file = os.path.join(script_dir, "human_phrases.txt")

    try:
        with open(phrases_file, "r", encoding="utf-8") as f:
            for line in f:
                phrase = line.strip()
                if phrase:
                    human_like_phrases.append(phrase)
    except FileNotFoundError:
        print(f"Error: {phrases_file} not found. Using default phrases.")
        human_like_phrases = [
            "You know?", "Well,", "Anyway,", "Look,", "I think...", "It seems...",
            "Actually,", "To be honest,", "So,", "Right?", "Um,", "Uh,", "Like,",
            "Basically,", "Essentially,", "In fact,", "As a matter of fact,",
            "The thing is,", "The point is,", "The truth is,", "Furthermore,",
            "Moreover,", "In addition,", "On the other hand,", "However,",
            "Nevertheless,", "Despite that,", "Although,", "Yet,", "Still,",
            "Meanwhile,", "In the meantime,", "By the way,", "Speaking of which,",
            "Regarding that,", "As for,", "Then,", "Next,", "After that,",
            "Before that,", "I believe...", "I feel...", "In my opinion,",
            "From my perspective,", "As far as I can tell,", "It appears...",
            "It looks like...", "I suppose...", "I guess...", "Maybe...",
            "Perhaps...", "Possibly...", "So yeah,", "Anyway, yeah,",
            "That's about it,", "In conclusion,", "To summarize,", "Ultimately,",
            "At the end of the day,", "I'm thinking...", "It's like...",
            "We're going to...", "They're saying...", "He's like...", "She's like...",
            "Listen,", "Honestly,", "Frankly,", "Seriously,", "Believe it or not,",
            "Guess what?", "You see,", "I mean,",
        ]

    lines = ai_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            transformed_text.append("")
            i += 1
            continue

        if line.startswith("##") or (line.startswith("**") and not re.match(r"^\*\s*\*\*", line)) or re.match(r"^\*\s*\*\*", line):
            transformed_text.append(line)
            i += 1
        else:
            paragraph = ""
            while i < len(lines) and not lines[i].strip().startswith("##") and not lines[i].strip().startswith("**") and not re.match(r"^\*\s*\*\*", lines[i].strip()):
                if paragraph:
                    paragraph += "\n" + lines[i]
                else:
                    paragraph = lines[i]
                i += 1

            if paragraph:
                doc = nlp(paragraph)
                processed_paragraph = []
                for sent in doc.sents:
                    sentence_text = "".join(token.text_with_ws for token in sent)
                    sentence_doc = nlp(sentence_text) # Re-parse for token-level operations

                    # Insert human-like phrases at the beginning of sentences
                    if random.random() < insertion_probability and human_like_phrases and len(sentence_doc) > 2: # Avoid adding to very short sentences
                        phrase_to_add = random.choice(human_like_phrases)
                        sentence_text = phrase_to_add + ", " + sentence_text.lstrip() # Add a comma for better flow

                    # Split long sentences
                    if len(sentence_doc) > long_sentence_threshold and random.random() < split_probability:
                        split_point = -1
                        for j in range(len(sentence_doc) // 2, len(sentence_doc) - 1): # Adjusted range
                            if sentence_doc[j].text in [",", ";", "and", "but", "or", "because"]:
                                split_point = j
                                break
                        if split_point != -1:
                            first_part = "".join(token.text_with_ws for token in sentence_doc[:split_point+1]).strip()
                            second_part = "".join(token.text_with_ws for token in sentence_doc[split_point+1:]).strip()
                            processed_paragraph.append(first_part)
                            processed_paragraph.append(second_part)
                        else:
                            processed_paragraph.append(sentence_text)
                    else:
                        processed_paragraph.append(sentence_text)

                transformed_text.extend(processed_paragraph)

    return "\n\n".join(transformed_text)
