import streamlit as st
import sqlite3
import random
from PIL import Image
import requests
from io import BytesIO

DB_PATH = "pokemon_cards_all_eu.db"

st.set_page_config(page_title="Pokémon Card Guessing Game (MC)", layout="centered")
st.title("Pokémon Card Guessing Game (Multiple Choice)")

# Get all valid cards (lowest_near_mint > 0.50)
def get_valid_cards():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.card_number, c.set_name, c.image, p.lowest_near_mint
        FROM cards c
        JOIN prices p ON c.id = p.card_id
        WHERE c.image IS NOT NULL AND p.lowest_near_mint IS NOT NULL AND p.lowest_near_mint > 2.50
    """)
    cards = cursor.fetchall()
    conn.close()
    return cards

# Get a random card and 3 random wrong answers for each field
def get_question(cards):
    correct = random.choice(cards)
    # For price, get 3 other random prices
    prices = [c[5] for c in cards if c != correct]
    price_choices = random.sample(prices, 3) + [correct[5]]
    random.shuffle(price_choices)
    # For name, get 3 other random names
    names = [c[1] for c in cards if c != correct]
    name_choices = random.sample(names, 3) + [correct[1]]
    random.shuffle(name_choices)
    # For set, get 3 other random sets
    sets = [c[3] for c in cards if c != correct]
    set_choices = random.sample(sets, 3) + [correct[3]]
    random.shuffle(set_choices)
    return {
        "card": correct,
        "price_choices": price_choices,
        "name_choices": name_choices,
        "set_choices": set_choices
    }

if "score" not in st.session_state:
    st.session_state.score = 0
if "rounds" not in st.session_state:
    st.session_state.rounds = 0
if "cards" not in st.session_state:
    st.session_state.cards = get_valid_cards()
if "question" not in st.session_state or st.button("Next Card"):
    st.session_state.question = get_question(st.session_state.cards)
    st.session_state.guessed = False

q = st.session_state.question
card = q["card"]
if card:
    st.image(requests.get(card[4]).content, width=250)
    st.write("### Guess the card's details!")
    price_guess = st.radio("What is the lowest near mint price? (€)", q["price_choices"], format_func=lambda x: f"€{x:.2f}")
    name_guess = st.radio("What is the card name?", q["name_choices"])
    set_guess = st.radio("What is the set name?", q["set_choices"])
    if st.button("Submit Guess") and not st.session_state.get("guessed", False):
        st.session_state.rounds += 1
        price_correct = price_guess == card[5]
        name_correct = name_guess == card[1]
        set_correct = set_guess == card[3]
        st.write(f"Actual price: €{card[5]:.2f}")
        st.write(f"Actual name: {card[1]}")
        st.write(f"Actual set: {card[3]}")
        score = 0
        if price_correct:
            st.success("Price guess is correct!")
            score += 1
        else:
            st.error("Price guess is incorrect.")
        if name_correct:
            st.success("Name guess is correct!")
            score += 1
        else:
            st.error("Name guess is incorrect.")
        if set_correct:
            st.success("Set guess is correct!")
            score += 1
        else:
            st.error("Set guess is incorrect.")
        st.session_state.score += score
        st.session_state.guessed = True
    st.write(f"Score: {st.session_state.score} / {st.session_state.rounds * 3 if st.session_state.rounds else 1}")
else:
    st.warning("No valid card found in the database.")

