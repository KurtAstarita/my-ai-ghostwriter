def get_gemini_flash_output(backstory, samples, prompt, model):
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

_nlp = None  # Initialize nlp as None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading en_core_web_sm model for spaCy...")
            spacy.cli.download("en_core_web_sm")
            _nlp = spacy.load("en_core_web_sm")
    return _nlp

def analyze_sentence_length(writing_samples):
    """Analyzes the average sentence length from writing samples."""
    nlp = get_nlp()
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
    nlp = get_nlp()
    avg_sentence_length = analyze_sentence_length(writing_samples)
    print(f"Average sentence length in samples: {avg_sentence_length:.2f} words")

    transformed_blocks = []
    insertion_probability = 0.3  # Reduced probability
    split_probability = 0.15 # Reduced probability
    long_sentence_threshold = 25 # Slightly higher threshold
    synonym_replacement_probability = 0.1
    transition_probability = 0.2

    script_dir = os.path.dirname(os.path.abspath(__file__))
    phrases_file = os.path.join(script_dir, "human_phrases.txt")
    phrase_categories = load_human_phrases(phrases_file) # Using a helper function

    blocks = re.split(r'(?m)^##|^(\*\*\s.*?:\s\*\*)', ai_text) # Split by markdown headings and bolded points
    blocks = [block.strip() for block in blocks if block and block.strip()]

    for block in blocks:
        if block.startswith("#") or block.startswith("**"):
            transformed_blocks.append(block)
            continue

        doc = nlp(block)
        processed_sentences = []
        last_phrase_inserted = False

        for sent in doc.sents:
            sentence_text = "".join(token.text_with_ws for token in sent)
            sentence_doc = nlp(sentence_text)

            # Apply transformations with adjusted probabilities
            if random.random() < transition_probability and not processed_sentences and len(sentence_doc) > 3:
                transition_phrase = random.choice(phrase_categories.get("transition") or transition_words)
                sentence_text = transition_phrase + ", " + sentence_text.lstrip()

            if random.random() < insertion_probability and len(sentence_doc) > 2 and not last_phrase_inserted:
                chosen_phrase = get_random_phrase(phrase_categories, len(transformed_blocks) == 0)
                if chosen_phrase:
                    sentence_text = insert_phrase(sentence_text, chosen_phrase)
                    last_phrase_inserted = True
                else:
                    last_phrase_inserted = False

            if len(sentence_doc) > long_sentence_threshold and random.random() < split_probability:
                first_part, second_part = split_sentence(sentence_doc)
                processed_sentences.extend([first_part, second_part])
            else:
                processed_sentences.append(sentence_text)
                last_phrase_inserted = False

        transformed_blocks.append(" ".join(processed_sentences))

    return "\n\n".join(transformed_blocks)

def load_human_phrases(file_path):
    phrase_categories = {
        "opening": [], "transition": [], "opinion": [],
        "casual": [], "emphasis": [], "closing": [],
        "question": [], "explanation": []
    }
    loaded_phrases = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "[" in line and "]" in line:
                    match = re.match(r"\[(.*?)\]\s*(.*)", line)
                    if match:
                        category = match.group(1).lower()
                        phrase = match.group(2).strip()
                        loaded_phrases.setdefault(category, []).append(phrase)
                elif line:
                    loaded_phrases.setdefault("general", []).append(line)

        for category, phrases in loaded_phrases.items():
            if category in phrase_categories:
                phrase_categories[category].extend(phrases)
            elif category == "general":
                for cat in ["casual", "opinion", "transition"]:
                    if cat in phrase_categories:
                        phrase_categories[cat].extend(phrases)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    return phrase_categories

def get_random_phrase(phrase_categories, is_opening):
    if is_opening and phrase_categories.get("opening"):
        return random.choice(phrase_categories["opening"])
    elif random.random() < 0.3 and phrase_categories.get("transition"):
        return random.choice(phrase_categories["transition"])
    else:
        general_phrases = []
        for cat in ["casual", "opinion", "emphasis", "question", "explanation"]:
            if phrase_categories.get(cat):
                general_phrases.extend(phrase_categories[cat])
        return random.choice(general_phrases) if general_phrases else None

def insert_phrase(sentence_text, phrase):
    insert_point = 0
    possible_points = [m.start() for m in re.finditer(r'[,;]', sentence_text)]
    if possible_points and random.random() < 0.3:
        insert_point = random.choice(possible_points) + 1
        return f"{sentence_text[:insert_point].strip()}, {phrase}{sentence_text[insert_point:]}"
    else:
        return f"{phrase}, {sentence_text.lstrip()}"

def split_sentence(sentence_doc):
    nlp = get_nlp()
    split_candidates = [i for i, token in enumerate(sentence_doc) if token.text in [",", ";", "and", "but", "or", "because"]]
    if split_candidates and len(sentence_doc) > 5:
        split_index = random.choice(split_candidates)
        first_part = "".join(token.text_with_ws for token in sentence_doc[:split_index+1]).strip()
        second_part = "".join(token.text_with_ws for token in sentence_doc[split_index+1:]).strip()
        return first_part, second_part
    else:
        return "".join(token.text_with_ws for token in sentence_doc).strip(), ""

transition_words = ["Furthermore", "However", "In addition", "On the other hand", "Moreover", "Consequently", "Therefore", "Meanwhile", "Nevertheless", "Despite that", "Although", "Yet", "Still", "So", "Then"]
# nlp = spacy.load("en_core_web_sm") # Removed this direct initialization
