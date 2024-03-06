import random

features_okra = {
    'stem': ['red green', 'red', 'green'],
    'flowering': ['not flowering', 'one pod']
}

features_citrus = {
    'health': ['good', 'poor', 'very good'],
    'yield': ['heavy', 'moderate', 'light'],
    'size': ['large', 'medium', 'small'],
    'shape': ['oblate', 'elongated', 'necked', 'spheroid'],
    'color': ['green', 'color break', 'orange'],
    'harvest': ['plugged', 'clean'],
    'peel': ['easy to peel', 'not peelable'],
    'peel thickness': ['thick peel', 'thick flavedo', 'thick albedo'],
    'fruit flesh': ['juicy', 'dry', 'segments separate easily'],
    'seed number': ['high', 'moderate', 'low', 'none'],
    'brix': ['high', 'moderate', 'low'],
    'acid': ['high', 'moderate', 'low'],
    'fruit flavor': ['best', 'above average', 'average', 'below average'],
    'trifoliate aftertaste': ['trifoliate aftertaste', 'trifolate aftertaste', 'present', 'not present'],
    'market class': ['grapefruit like', 'orange like', 'mandarin like'],
    'recheck': ['recheck', 'yes', 'no']
}

def create_transcript(num_lines: int, features: dict):
    transcript = ""
    traits = list(features.keys())
    for _ in range(num_lines):
        random.shuffle(traits)
        transcript += f"New plant "
        for trait in traits:
            if random.random() > 0.5:
                continue
            characteristic = random.choice(features[trait])
            transcript += f"{characteristic} "
        transcript += f"\n"
    return transcript

print(create_transcript(5, features_okra))
print(create_transcript(5, features_citrus))

