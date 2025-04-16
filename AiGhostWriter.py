import google.generativeai as genai

# Replace with your actual API key
GOOGLE_API_KEY = "AIzaSyA__63BnzDRK0vQqcuJkN5MHpgIlQ6WF8A"

# Configure the API key
genai.configure(api_key=GOOGLE_API_KEY)

# For text-only input, use the gemini-2.0-flash model
model = genai.GenerativeModel('gemini-2.0-flash')
def get_gemini_flash_output(backstory, samples, prompt):
    """
    Interacts with the Gemini 2.0 Flash model to get the initial output,
    with a refined prompt for better stylistic imitation.
    """
    combined_context = f"Personal Backstory: {backstory}\n\nWriting Samples:\n{samples}"
    final_prompt = f"""You are an AI assistant whose primary goal is to write in the style of the user provided in the "Personal Backstory" and "Writing Samples" below. Pay close attention to their tone, vocabulary, sentence structure, and overall writing personality.

Personal Backstory:
{backstory}

Writing Samples:
{samples}

Now, write a response to the following prompt, ensuring it strongly reflects the user's writing style:

Prompt:
{prompt}

Write a response in a similar style, as if it were written by the user themselves."""

    try:
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        return f"Error generating content: {e}"

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
    insertion_probability = 0.5  # Slightly reduced
    split_probability = 0.2
    long_sentence_threshold = 20
    synonym_replacement_probability = 0.15
    transition_probability = 0.15
    transition_words = ["Furthermore", "However", "In addition", "On the other hand", "Moreover", "Consequently", "Therefore", "Meanwhile", "Nevertheless", "Despite that", "Although", "Yet", "Still", "So", "Then"]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    phrases_file = os.path.join(script_dir, "human_phrases.txt")

    phrase_categories = {
        "opening": [],
        "transition": [],
        "opinion": [],
        "casual": [],
        "emphasis": [],
        "closing": [],
        "question": [],
        "explanation": [],
    }

    loaded_phrases = {}
    try:
        with open(phrases_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "[" in line and "]" in line:
                    match = re.match(r"\[(.*?)\]\s*(.*)", line)
                    if match:
                        category = match.group(1).lower()
                        phrase = match.group(2).strip()
                        if category in loaded_phrases:
                            loaded_phrases[category].append(phrase)
                        else:
                            loaded_phrases[category] = [phrase]
                elif line: # If no category label, add to a default list
                    if "general" not in loaded_phrases:
                        loaded_phrases["general"] = []
                    loaded_phrases["general"].append(line)

        # Update default categories with loaded phrases if available
        for category, phrases in loaded_phrases.items():
            if category in phrase_categories:
                phrase_categories[category].extend(phrases)
            elif category == "general":
                # Add general phrases to a few common categories to make them more likely to be used
                for cat in ["casual", "opinion", "transition"]:
                    if cat in phrase_categories:
                        phrase_categories[cat].extend(phrases)

    except FileNotFoundError:
        print(f"Error: {phrases_file} not found. Using default phrases.")

    lines = ai_text.splitlines()
    i = 0
    last_phrase_inserted = False # Track if a phrase was inserted in the last sentence
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            transformed_text.append("")
            i += 1
            continue

        if line.startswith("##") or (line.startswith("**") and not re.match(r"^\*\s*\*\*", line)) or re.match(r"^\*\s*\*\*", line):
            transformed_text.append(line)
            i += 1
            last_phrase_inserted = False # Reset flag for headings
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
                    sentence_doc = nlp(sentence_text)

                    # Insert transition words
                    if random.random() < transition_probability and not processed_paragraph and len(sentence_doc) > 3:
                        transition_options = phrase_categories.get("transition") or transition_words
                        if transition_options:
                            transition_phrase = random.choice(transition_options)
                            sentence_text = transition_phrase + ", " + sentence_text.lstrip()

                    # Insert human-like phrases based on context
                    if random.random() < insertion_probability and len(sentence_doc) > 2 and not last_phrase_inserted:
                        chosen_phrase = None
                        if i == 0 and random.random() < 0.5: # Beginning of the output
                            opening_phrases = phrase_categories.get("opening")
                            if opening_phrases:
                                chosen_phrase = random.choice(opening_phrases)
                        elif len(transformed_text) > 0 and random.random() < 0.3: # Between paragraphs
                            transition_phrases = phrase_categories.get("transition")
                            if transition_phrases:
                                chosen_phrase = random.choice(transition_phrases)
                        elif random.random() < 0.4: # General casual insertion
                            possible_categories = ["casual", "opinion", "emphasis", "question", "explanation"]
                            chosen_category = random.choice(possible_categories)
                            category_phrases = phrase_categories.get(chosen_category)
                            if category_phrases:
                                chosen_phrase = random.choice(category_phrases)

                        if chosen_phrase:
                            insert_point = 0
                            possible_points = [m.start() for m in re.finditer(r'[,;]', sentence_text)]
                            if possible_points and random.random() < 0.3:
                                insert_point = random.choice(possible_points) + 1 # Insert after the punctuation

                            punctuation_chars = ['.', '?', '!']
                            ends_with_punctuation = chosen_phrase.endswith(tuple(punctuation_chars))

                            if insert_point > 0:
                                prefix = sentence_text[:insert_point].strip()
                                suffix = sentence_text[insert_point:]
                                if suffix.strip() and not ends_with_punctuation:
                                    sentence_text = f"{prefix}, {chosen_phrase}{suffix}"
                                else:
                                    sentence_text = f"{prefix} {chosen_phrase}{suffix}"
                            else:
                                suffix = sentence_text.lstrip()
                                if suffix and not ends_with_punctuation:
                                    sentence_text = f"{chosen_phrase}, {suffix}"
                                else:
                                    sentence_text = f"{chosen_phrase} {suffix}"
                            last_phrase_inserted = True
                        else:
                            last_phrase_inserted = False # Don't set if we didn't insert

                    # Split long sentences
                    if len(sentence_doc) > long_sentence_threshold and random.random() < split_probability:
                        split_point = -1
                        split_candidates = [i for i, token in enumerate(sentence_doc) if token.text in [",", ";", "and", "but", "or", "because"]]
                        if split_candidates and len(sentence_doc) > 5: # Ensure there's enough on both sides
                            split_index = random.choice(split_candidates)
                            first_part = "".join(token.text_with_ws for token in sentence_doc[:split_index+1]).strip()
                            second_part = "".join(token.text_with_ws for token in sentence_doc[split_index+1:]).strip()
                            processed_paragraph.append(first_part)
                            processed_paragraph.append(second_part)
                        else:
                            processed_paragraph.append(sentence_text)
                    else:
                        processed_paragraph.append(sentence_text)
                        last_phrase_inserted = False # Reset if not split

                transformed_text.extend(processed_paragraph)

    return "\n\n".join(transformed_text)
