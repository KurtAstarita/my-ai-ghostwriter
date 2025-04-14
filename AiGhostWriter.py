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

nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

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

import os

import os
import re  # Import the regular expression module

import os
import re

def transform_to_human_like(ai_text, writing_samples):
    avg_sentence_length = analyze_sentence_length(writing_samples)
    print(f"Average sentence length in samples: {avg_sentence_length:.2f} words")

    transformed_text = []
    human_like_phrases = []
    insertion_probability = 0.7   # Keeping this high for now
    split_probability = 0.2   # 20% chance of splitting a long sentence
    long_sentence_threshold = 20   # Sentences longer than this will be considered for splitting

    # Use absolute path to human_phrases.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))   # Directory of the script
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
            "You know?",
            "Well,",
            "Anyway,",
            "Look,",
            "I think...",
            "It seems...",
            "Actually,",
            "To be honest,",
            "So,",
            "Right?",
            "Um,",
        ]

    lines = ai_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            transformed_text.append("")
            i += 1
            continue

        if line.startswith("##"):
            transformed_text.append(line)
            i += 1
        elif line.startswith("**") and not re.match(r"^\*\s*\*\*", line):
            transformed_text.append(line)
            i += 1
        elif re.match(r"^\*\s*\*\*", line):
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
                    if random.random() < insertion_probability and human_like_phrases:
                        phrase_to_add = random.choice(human_like_phrases)
                        sentence_text = phrase_to_add + " " + sentence_text

                    sentence_doc = nlp(sentence_text) # Re-parse the sentence to work with tokens

                    if len(sentence_doc) > long_sentence_threshold and random.random() < split_probability:
                        split_point = -1
                        for j in range(len(sentence_doc) // 2, len(sentence_doc)):
                            if sentence_doc[j].text in [",", ";", "and", "but", "or", "because"]:
                                split_point = j
                                break

                        if split_point != -1 and split_point < len(sentence_doc) - 1:
                            first_part = "".join(token.text_with_ws for token in sentence_doc[:split_point+1])
                            second_part = "".join(token.text_with_ws for token in sentence_doc[split_point+1:])
                            processed_paragraph.append(first_part.strip())
                            processed_paragraph.append(second_part.strip())
                        else:
                            processed_paragraph.append(sentence_text)
                    else:
                        processed_paragraph.append(sentence_text)
                transformed_text.extend(processed_paragraph)

    return "\n\n".join(transformed_text)

def get_synonyms(word, pos=None): # Keep the default pos=None
    synonyms = set()
    for syn in wordnet.synsets(word, pos=pos):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
    if word in synonyms:
        synonyms.remove(word)
    return list(synonyms)

# --- Example Usage ---
if __name__ == "__main__":
    backstory_input = "Grew up in a small town, always loved adventure..."
    samples_input = """If you're looking for some unorthodox training methods, check out these park workout ideas I came up with. I still do them from time to time and never get tired of them.

think outside the box and get creative with your training, look at everyday objects in a new light. Think of ways you could train with it!

Anyways…

You know, we see kids every day playing at the parks, but we're too self-conscious to do it ourselves. Kids call it playing, adults call it working out, wink!

Well guess what? Us adults can play or whatever with the kiddos.

Here are my park workout methods that will definitely get you some amazing results outside and under the sun, the best part is its free, do-it!

1. Monkey Bars

Ha, there are a number of ways you can utilize monkey bars. Look at the straight bar, which you’ll see most commonly at just about every children’s park.


These are great for pull ups, bar dips, and core exercises.

You can even perform the most advanced calisthenics movements like the Muscle-up, L-sit, and front levers.

2. The Rings

Rings can be in a fixed position, or swivel, it all depends where you go. You’ll find them at local, state, and calisthenics parks (but those kinds of parks are much much less common).


Rings are great for chin-ups, and hanging core exercises. You can also perform the same advanced calisthenics exercise with a slight change in grip variation.

3. The Pole

You can even equip the side of the pole with an assortment of bands, for pulling or pushing exercises.


Believe it or not, bands are my specialty. I use resistance bands with handles, and Pull-up bands with you can purchase online. You may be able to find crappy ones in Walmart, and a decent pair at Dicks sporting goods.

Attach your bands to the side of the pole for…
Hey, bros Kurt here, and I’m thrilled to share some stimulating facts about me. So if you are curious about this dude, here is my tune.

First off I’m not here to impress you, I’m here to impress upon you that I’m here to build a sick brand, “embraced in value.”

Something juicy to help you get more gains…

I’m here to help you understand your true potential and how to unlock it through fitness, nutrition and dedication.

I may flaunt my muscles, but I’m not Showing off, hahah!

I’m proving a point. That hard work and dedication combined with some constancy - throw in a heaping handful of discipline, a pinch of blood sweat and tears — boom, it is the recipe for gains!


My body is a result of an unrelenting desire to be the strongest in the universe like Goku.

I remember aspirating to be more like Goku, “a fictional character” in Anime. But Goku represents more than that. It's his archetype that later on in my life I realized I wanted to be like.

Goku always fought for his friends and loved ones and protected them in times of pearl. He fought to be the strongest so that he could protect them and the rest of the world.


We all have someone we are fighting for, never give up!

Rocky was another one of my childhood inspirations, for the simple fact that he never gave up no matter what, and no matter how hard he got hit or how many times he got knocked down he always got back up!

I decided to pursue my love and passion of becoming the strongest, and I want to see how far I can take you there with me.

What does It Take To Be The Strongest?

Physical Training

I am talking intense physical training such as calisthenics, powerlifting, gymnastics, bodybuilding, and military, are all games. There is even sports specific training to strengthen skills. If you are in this game for only health reasons then sports specific training really isn't necessary.

Mental Conditioning

Combine your physical training with feats of intense mental discipline. When you have a craving, refuse it. When you are thirsty, hold out longer than normal. Train in the extreme cold. Train in the extreme hot. Train when you don't want to. Then get an ice bath or cold shower!

Listen to Tony Robbins, Eric Thomas, and David Goggins audios for inspiration and new ideas.

Spiritual awakening

Connect with your creator, I worship God, and Jesus is my lord and savior. However many great spiritual teachers like Budda were connected to source and have received their teachings from the divine. Ask for help, prey, and meditate often.

Now I’m not claiming to be a freak of nature, far from it. Those massive freaks you see on the internet are jacked up on so many roids, it will give you an unrealistic expectation

I'm not even taking supplements, nothing outside of healthy food and water.

That said, for someone who weighs 184-ish pounds I can tell you I have some HUGE forearms! And I will tell you this… they are crazy strong too!

Here are the exceptional forearm training tactics that I unlocked over years of trial and error.


For insane forearms, you have to make them a focus. Take a different approach than the rest of your body. Your forearms are stabilizer muscles that can receive stimuli from most pulling exercises like rows, pull-ups, and pull-downs.

“Pretty much any pulling exercise”

Forearms are also hit during bicep exercises to some degree. The problem is that most people don’t maximize the tension on the forearms while doing these exercises.

Medical Disclaimer and Results Not Guaranteed

The information provided in this program is for informational purposes only and is not a substitute for professional medical advice. Participation in physical activities and exercise routines carries inherent risks, and individual results may vary. Before starting any new exercise or nutrition program, consult with a qualified medical professional. Read the full disclaimer here.

Remember, your health and safety are a priority. Consult with a medical professional before making any changes to your lifestyle.

1. How To Maximize Forearm Tension

The key is wrist “flexion”, since most of us grab a bar with a neutral grip, this is the grip you can maintain the strongest squeeze utilizing finger strength.

This is the ideal position that the hand naturally falls into when performing a heavy pull exercise like a deadlift.

It's where the wrist is bent slightly back, and you can squeeze a tight fist with the most force.

This is NOT what we want with wrist flexion. For forearm size, you want to curl your wrist inward like you are flexing your forearms.

Think wrist curls. Now when you grab the bar grab it in this wrist-curl flexed position and perform your pull exercise.
"""
    prompt_input = "Write a blog post about the benefits of park workouts."

    GOOGLE_API_KEY = "AIzaSyA__63BnzDRK0vQqcuJkN5MHpgIlQ6WF8A" # Replace with your actual key
    genai.configure(api_key=GOOGLE_API_KEY)
    output = get_gemini_flash_output(backstory_input, samples_input, prompt_input)
    print("\nInitial AI Output:")
    print(output)

    human_like_output = transform_to_human_like(output, samples_input)
    print("\nTransformed Output:")
    print(human_like_output)