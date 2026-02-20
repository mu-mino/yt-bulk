from google import genai


client = genai.Client(api_key="AIzaSyAMdfO8kbV58JsMIGAZbyo7hnsMjGxguys")
langs = [
    "ar",
    "en",
    "id",
    "ur",
    "bn",
    "tr",
    "fr",
    "fa",
    "ms",
    "de",
    "ru"
]

for lang in langs:
    prompt = (
        f"Handle als reine Daten-Verarbeitungsfunktion (Literal Translation Protocol). "
        f"Regel 1: Gib ausschließlich die Übersetzung des Zieltextes zurück. "
        f"Regel 2: Kein Smalltalk, keine Einleitung ('Hier ist...'), keine Metadaten. "
        f"Regel 3: Behalte Eigennamen wie 'The Highest Speech', 'Maher Al-Muaiqly', 'Al-Hilali' und 'Muhsin Khan' bei. "
        f"Aufgabe: Übersetze den folgenden Text vollständig in die Sprache {lang}: "
        "\n---\n"
        "The Highest Speech (كلمة العليا)\n\n"
        "Welcome to your sanctuary for the Holy Qur'an. This channel is dedicated to providing high-quality, calm, and contemplative recitations of the 114 Surahs, featuring the world-renowned voice of Sheikh Maher Al-Muaiqly (Imam of Masjid al-Haram).\n\n"
        "Our mission is to bridge the gap between recitation and understanding. Each video is meticulously crafted with:\n\n"
        "Precise English Translation: Based on the 'Interpretation of the Meanings of the Noble Qur'an' by Dr. Muhammad Taqi-ud-Din Al-Hilali and Dr. Muhammad Muhsin Khan.\n\n"
        "Visual Clarity: Word-by-word Arabic text synchronized with the recitation for a meditative experience.\n\n"
        "Global Access: Multilingual titles and descriptions to serve the global Ummah.\n\n"
        "Whether you are seeking peace of mind, memorizing the Qur'an, or studying its profound meanings, we invite you to subscribe and join us on this spiritual journey.\n\n"
        "May Allah (SWT) make this a source of guidance and reward for us all."
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    print(response.text)