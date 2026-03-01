import streamlit as st
import sqlite3
import random
from PIL import Image
import requests
from io import BytesIO

DB_PATH = "pokemon_cards_all_eu.db"

st.set_page_config(page_title="Pokémon Card Pairing Game", layout="centered")
st.title("Pokémon Card Pairing Game")

# Get all valid cards (lowest_near_mint > 0.50)
def get_valid_cards():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.card_number, c.set_name, c.image, p.lowest_near_mint
        FROM cards c
        JOIN prices p ON c.id = p.card_id
        WHERE c.image IS NOT NULL AND p.lowest_near_mint IS NOT NULL AND p.lowest_near_mint > 2
    """)
    cards = cursor.fetchall()
    conn.close()
    return cards

def get_pairing_question(cards):
    selected = random.sample(cards, 3)
    prices = [c[5] for c in selected]
    names = [c[1] for c in selected]
    sets = [c[3] for c in selected]
    # Shuffle each list for pairing
    shuffled_prices = random.sample(prices, len(prices))
    shuffled_names = random.sample(names, len(names))
    shuffled_sets = random.sample(sets, len(sets))
    return {
        "cards": selected,
        "prices": shuffled_prices,
        "names": shuffled_names,
        "sets": shuffled_sets
    }

if "score" not in st.session_state:
    st.session_state.score = 0
if "rounds" not in st.session_state:
    st.session_state.rounds = 0
if "cards" not in st.session_state:
    st.session_state.cards = get_valid_cards()
if "pairing_question" not in st.session_state or st.button("Next Round"):
    st.session_state.pairing_question = get_pairing_question(st.session_state.cards)
    st.session_state.guessed = False

q = st.session_state.pairing_question
cards = q["cards"]
if cards:
    st.write("### Match each card to its price, name, and set!")
    # Show cards in a single row, pairing interface only
    cols = st.columns(3)
    price_guesses = []
    name_guesses = []
    set_guesses = []
    for i, card in enumerate(cards):
        with cols[i]:
            st.image(requests.get(card[4]).content, width=180)
            price = st.selectbox(f"Price", q["prices"], key=f"price_{i}")
            name = st.selectbox(f"Name", q["names"], key=f"name_{i}")
            set_ = st.selectbox(f"Set", q["sets"], key=f"set_{i}")
            price_guesses.append(price)
            name_guesses.append(name)
            set_guesses.append(set_)

    if st.button("Submit Pairings") and not st.session_state.get("guessed", False):
        st.session_state.rounds += 1
        score = 0
        for i, card in enumerate(cards):
            st.write(f"---")
            st.write(f"#### Card #{i+1} Results:")
            correct_price = card[5]
            correct_name = card[1]
            correct_set = card[3]
            if price_guesses[i] == correct_price:
                st.success(f"Price match correct! (€{correct_price:.2f})")
                score += 1
            else:
                st.error(f"Price match incorrect. Actual: €{correct_price:.2f}")
            if name_guesses[i] == correct_name:
                st.success(f"Name match correct! ({correct_name})")
                score += 1
            else:
                st.error(f"Name match incorrect. Actual: {correct_name}")
            if set_guesses[i] == correct_set:
                st.success(f"Set match correct! ({correct_set})")
                score += 1
            else:
                st.error(f"Set match incorrect. Actual: {correct_set}")
        st.session_state.score += score
        st.session_state.guessed = True
    st.write(f"Score: {st.session_state.score} / {st.session_state.rounds * 9 if st.session_state.rounds else 1}")
else:
    st.warning("Not enough valid cards found in the database.")
