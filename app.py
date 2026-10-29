import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import emoji
import re

st.set_page_config(
    page_title="Text + Emoji Sentiment Analyzer",
    page_icon="😊",
    layout="centered",
)

@st.cache_resource
def load_analyzer():
    return SentimentIntensityAnalyzer()

analyzer = load_analyzer()

st.title("😊 Text + Emoji Sentiment Analyzer")
st.write(
    "Enter a message to estimate its sentiment. The analyzer considers both "
    "the words and common emojis in the text."
)

st.caption(
    "Examples: “I love this! ❤️😍” · “That was awful 😡” · "
    "“The service was okay 🙂”"
)

text = st.text_area(
    "Enter your text",
    placeholder="Type a message with words, emojis, or both…",
    height=140,
    max_chars=5000,
)

def sentiment_label(compound_score):
    if compound_score >= 0.05:
        return "Positive", "😊"
    if compound_score <= -0.05:
        return "Negative", "😞"
    return "Neutral", "😐"

def extract_emojis(message):
    # emoji.emoji_list returns each emoji and its character position.
    return [item["emoji"] for item in emoji.emoji_list(message)]

def emoji_description(symbol):
    # Convert emoji to a readable name when the installed emoji package supports it.
    try:
        name = emoji.demojize(symbol, language="en")
        return name.strip(":").replace("_", " ")
    except Exception:
        return "emoji"

if st.button("Analyze sentiment", type="primary", use_container_width=True):
    cleaned_text = text.strip()

    if not cleaned_text:
        st.warning("Please enter some text or emojis first.")
    else:
        scores = analyzer.polarity_scores(cleaned_text)
        label, face = sentiment_label(scores["compound"])

        st.subheader("Result")
        st.metric("Overall sentiment", f"{face} {label}")
        st.progress(min(1.0, max(0.0, (scores["compound"] + 1) / 2)))
        st.write(f"**Compound score:** `{scores['compound']:.3f}`")
        st.caption(
            "The compound score ranges from -1 (most negative) to +1 "
            "(most positive). The progress bar maps this range from left to right."
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Positive", f"{scores['pos'] * 100:.1f}%")
        col2.metric("Neutral", f"{scores['neu'] * 100:.1f}%")
        col3.metric("Negative", f"{scores['neg'] * 100:.1f}%")

        found_emojis = extract_emojis(cleaned_text)
        st.subheader("Emoji check")
        if found_emojis:
            unique_emojis = list(dict.fromkeys(found_emojis))
            st.write("Emojis found:", " ".join(unique_emojis))
            st.write(
                "Readable names:",
                ", ".join(
                    f"{symbol} = {emoji_description(symbol)}"
                    for symbol in unique_emojis
                ),
            )
            st.caption(
                "Emoji sentiment is assessed as part of the full message. "
                "An emoji's meaning can change with context, sarcasm, or how it is used."
            )
        else:
            st.write("No emojis detected. The result is based on the text.")

        with st.expander("How to read this result"):
            st.write(
                "- **Positive:** compound score ≥ 0.05\n"
                "- **Neutral:** compound score between -0.05 and 0.05\n"
                "- **Negative:** compound score ≤ -0.05\n\n"
                "This app uses VADER, a lightweight rule-based sentiment analyzer "
                "that is designed for short social-media-style text and recognizes "
                "many common emoji symbols. It is an estimate, not a perfect "
                "understanding of sarcasm, slang, or every language."
            )

st.divider()
st.caption("Built with Streamlit + VADER Sentiment + emoji.")
