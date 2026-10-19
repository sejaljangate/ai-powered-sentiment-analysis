"""Small, explainable lexicon-based sentiment classifier (Python standard library)."""

from collections import Counter
import csv
import html
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent

# Compact teaching lexicon. Scores are intentionally transparent and editable.
LEXICON = {
    "amazing": 2, "awesome": 2, "best": 2, "brilliant": 2, "comfortable": 1,
    "delightful": 2, "efficient": 1, "enjoy": 1, "excellent": 2, "fantastic": 2,
    "fast": 1, "friendly": 1, "good": 1, "great": 2, "happy": 1, "helpful": 1,
    "love": 2, "perfect": 2, "recommend": 1, "reliable": 1, "smooth": 1,
    "superb": 2, "wonderful": 2, "worth": 1,
    "annoying": -1, "awful": -2, "bad": -1, "broken": -1, "disappointing": -2,
    "disappointed": -2, "dirty": -1, "hate": -2, "horrible": -2, "late": -1,
    "poor": -1, "refund": -1, " rude": -1, "slow": -1, "terrible": -2,
    "unhelpful": -1, "unreliable": -2, "waste": -2, "worst": -2,
}
NEGATORS = {"not", "no", "never", "hardly", "isn't", "wasn't", "don't", "didn't", "can't", "won't"}
BOOSTERS = {"very": 1.5, "really": 1.5, "extremely": 2.0, "so": 1.3, "too": 1.3}
TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?", re.I)

REVIEWS = [
    "The staff were friendly and the service was excellent.",
    "I love this phone; the camera is amazing.",
    "Great quality and very comfortable to use.",
    "Delivery was fast and the packaging was perfect.",
    "A wonderful experience, I highly recommend it.",
    "The app is smooth, helpful, and reliable.",
    "Fantastic value for money and brilliant support.",
    "It works as described.",
    "The color is blue and the box contains two pieces.",
    "I received the order on Tuesday afternoon.",
    "The product has a screen and a charging cable.",
    "The menu lists soup, rice, and tea.",
    "The delivery was late and the package was broken.",
    "Poor quality; I am disappointed with this purchase.",
    "The app is slow, annoying, and unhelpful.",
    "Terrible service. I want a refund.",
    "This was a waste of money and the worst experience.",
]

TESTS = [
    ("The headphones are fantastic and sound amazing.", "positive"),
    ("The order arrived late and the item was broken.", "negative"),
    ("The package contains a black notebook.", "neutral"),
]


def classify(text):
    tokens = TOKEN_RE.findall(text.lower())
    score = 0.0
    for i, token in enumerate(tokens):
        value = LEXICON.get(token, 0)
        if not value:
            continue
        # Negation within the previous two tokens reverses the sentiment.
        if any(t in NEGATORS for t in tokens[max(0, i - 2):i]):
            value *= -1
        # A nearby booster strengthens the sentiment.
        if i and tokens[i - 1] in BOOSTERS:
            value *= BOOSTERS[tokens[i - 1]]
        score += value
    label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return label, score


def write_chart(counts, path):
    colors = {"positive": "#16a34a", "negative": "#dc2626", "neutral": "#64748b"}
    labels = ["positive", "negative", "neutral"]
    max_count = max(counts.values(), default=1)
    width, height, left, row_h, bar_max = 640, 250, 140, 58, 390
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" rx="16" fill="#fff"/>',
             '<text x="28" y="35" font-family="Arial" font-size="20" font-weight="700" fill="#0f172a">Review sentiment counts</text>']
    for n, label in enumerate(labels):
        y = 64 + n * row_h
        bar_w = int(bar_max * counts[label] / max_count) if max_count else 0
        parts.extend([
            f'<text x="28" y="{y + 25}" font-family="Arial" font-size="15" fill="#334155">{label.title()}</text>',
            f'<rect x="{left}" y="{y}" width="{bar_max}" height="34" rx="7" fill="#f1f5f9"/>',
            f'<rect x="{left}" y="{y}" width="{bar_w}" height="34" rx="7" fill="{colors[label]}"/>',
            f'<text x="{left + bar_max + 14}" y="{y + 23}" font-family="Arial" font-size="16" font-weight="700" fill="#0f172a">{counts[label]}</text>',
        ])
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def main():
    rows = [(i, text, *classify(text)) for i, text in enumerate(REVIEWS, 1)]
    counts = Counter(label for _, _, label, _ in rows)
    csv_path = OUT / "classified_reviews.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "review", "predicted_sentiment", "score"])
        writer.writerows((i, text, label, f"{score:g}") for i, text, label, score in rows)
    write_chart(counts, OUT / "sentiment_counts.svg")

    print("SAMPLE REVIEW CLASSIFICATIONS")
    print(f"{'ID':>2}  {'SENTIMENT':<9} {'SCORE':>5}  REVIEW")
    for i, text, label, score in rows:
        print(f"{i:>2}  {label:<9} {score:>5g}  {text}")
    print("\nCATEGORY COUNTS")
    for label in ("positive", "negative", "neutral"):
        print(f"{label.title():<9} {counts[label]}")
    print("\nTHREE NEW STATEMENTS (expected labels are the manual check)")
    correct = 0
    for text, expected in TESTS:
        predicted, score = classify(text)
        ok = predicted == expected
        correct += ok
        print(f"{predicted:<9} score={score:g} expected={expected:<9} {'PASS' if ok else 'CHECK'}  {text}")
    print(f"Manual-check agreement: {correct}/{len(TESTS)}")
    print(f"\nWrote {csv_path.name} and sentiment_counts.svg")


if __name__ == "__main__":
    main()
