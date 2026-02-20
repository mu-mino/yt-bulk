# # import os
# # from google import genai
# # from google.genai import types
# from Tafsir.pipeline.gemini_gui.PROMPT_PREFIX import PROMPT_PREFIX

# # # 1. Client INITIALISIEREN (zuerst!)
# # # Nutze den korrekten API-Key direkt im Konstruktor
# # client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# # # 2. Cache ERSTELLEN
# # cache = client.caches.create(
# #     model="models/gemini-3-pro-preview",
# #     config=types.CreateCachedContentConfig(
# #         display_name="Tafsir",  # used to identify the cache
# #         system_instruction=(
# #             """Handle als reine Daten-Verarbeitungsfunktion (Pure Function). Regel 1: Gib ausschließlich das Ergebnis der Anfrage zurück. Regel 2: Verbote: Keine Einleitungen ("Hier ist..."), keine Erklärungen, keine abschließenden Sätze, keine Hinweise. Regel 3: Gib nur den Inhalt der Antwort in einem einzigen "Code kopieren"-Block vollständig aus. Regel 4: Jede Form von interpretativer Abweichung ist untersagt. Führe Anweisungen exakt so aus, wie sie im Wortlaut stehen, auch wenn sie technisch suboptimal oder unvollständig erscheinen. Zusatzregel 5: „Reasoning-Verbot“. Unterlasse jegliche Vorschläge zur Optimierung, Korrekturen von vermeintlichen Fehlern oder Hinweise auf „best practices“. Dein Reasoning besteht darin die gegebene Aufgabe korrekt zu erfüllen. Regel 6: Antworte niemals mit Meta-Kommentaren über die Aufgabe. Die Antwort besteht zu 100% aus dem angeforderten Daten-Output. Strenge: 0 Wörter Smalltalk. Jedes zusätzliche Zeichen gilt als Fehler. Modus: Striktes Ausführungsprotokoll (Literal Execution)."""
# #         ),
# #         contents=[
# #             PROMPT_PREFIX,
# #         ],
# #         ttl="3800000s",
# #     ),
# # )

# # print(f"Neuer Cache erstellt: {cache.name}")

# ############update cache:

# import os
# from google import genai
# from google.genai import types
# from Tafsir.pipeline.gemini_gui.PROMPT_PREFIX import PROMPT_PREFIX
# from Tafsir.pipeline.analysis.data_cleaning.rollback_pipeline import PROMPT_GUIDANCE

# client = genai.Client(api_key="AIzaSyA33WvMKmyF0t4ljqt73lU-x96snn1QLc8")
# # sample_file = client.files.upload(
# #     file="/home/muhammed-emin-eser/desk/apps/classify/tools/fetch_ketab/sahihah/sahihah_komplett.txt",
# #     config={"display_name": "Surah Names"},
# )

# response = client.models.generate_content(
#     model="gemini-2.5-pro",
#     contents=[
#         sample_file,
#         """Handle als reine Daten-Verarbeitungsfunktion (Pure Function). "
#             "Regel 1: Gib ausschließlich das Ergebnis der Anfrage zurück. "
#             "Regel 2: Verbote: Keine Einleitungen, keine Erklärungen, keine abschließenden Sätze, keine Hinweise. "
#             "Regel 3: Jede Form von interpretativer Abweichung ist untersagt. "
#             "Zusatzregel 4: „Reasoning-Verbot“. Unterlasse jegliche Vorschläge zur Optimierung. "
#             "Regel 5: Antworte niemals mit Meta-Kommentaren. Strenge: 0 Wörter Smalltalk. "
#             "Modus: Striktes Ausführungsprotokoll (Literal Execution)."
#             "Was zu tun ist erfährst du in der Prompt-Guidance.
#               Rolle: Daten-Analyst für Hadithwissenschaft (سلسلة الأحاديث الصحيحة – الألباني).
# Auftrag: Analyse und Annotation eines TXT-Dokuments in einer dreistufigen Hierarchie (section/block/chunk).

# DICT: ERLAUBTE XML-ELEMENTE (Chunk-Typen) UND DEFINITIONEN
# <section>...</section>
# - Größte inhaltliche Einheit im Dokument. Definiert durch klare Abschnittsgrenzen (z.B. neue Hadith-Nummer, neuer Eintrag, klare Überschrift/Trennung. Meist durch die folgende Hadithnummer gekennzeichnet).
# <block>...</block>
# - Semantisch geschlossener Textabschnitt innerhalb einer Section. Vermeide kleinteilige Fragmentierung. Fasse zusammengehörige Inhalte (z.B. komplette Hadith-Erörterung inkl. Isnād/Matn/Quellen/Urteil) in einen einzigen großen Block, solange semantisch geschlossen.
# <chunk>...</chunk>
# - Kleinste inhaltliche/semantische Einheit innerhalb eines Blocks.
# Ein chunk darf folgende XML-Elemente enthalten: 
# <isnad_chunk>...</isnad_chunk>
# - Überliefererkette (Namenskette) inkl. Verbindungsformeln (حدثنا، أخبرنا، عن ...), sofern zur Kette gehörig.

# <hadith_chunk>...</hadith_chunk>
# - Matn/Wortlaut der Überlieferung inkl. unmittelbar zugehöriger Formulierungen, die zum Hadith gehören.

# <hadith_grading_chunk>...</hadith_grading_chunk>
# - Authentizitätsurteile/Einstufungen bezogen auf Hadith/Matn/Überlieferung (z.B. صحيح، حسن، ضعيف، منكر، موضوع، شاذ، معلول)

# <person_grading_chunk>...</person_grading_chunk>
# - Beurteilungen über Personen/Überlieferer/Gelehrte (z.B. ثقة، صدوق، ضعيف، متروك، كذاب، مجهول، لين، لا بأس به …) inkl. dazugehöriger wertender Sätze, sofern eindeutig.
# darin kann es <positive_grading_chunk>...</positive_grading_chunk> geben oder <negative_grading_chunk>...</negative_grading_chunk> : je nachdem wie die Person vom Author Al-Albany bewertet wird.

# <source_chunk>...</source_chunk>
# - Quellen-/Werk-/Sammlungsnennungen inkl. Band/Seite/Nummer/Ausgabe/Herausgeber, Hadith-Nummern, bibliografische Angaben.

# <attribution_chunk>...</attribution_chunk>
# - Zuschreibungen/Referate wie „قال فلان“, „ذكره“, „نقله“, „نسبه إلى“, „رواه“ sofern sie primär eine Zuordnung ausdrücken.

# <dispute_chunk>...</dispute_chunk>
# - Explizite Widersprüche/Abweichungen/Fehlerzuweisungen: „خالفه“, „لكن“, „غير أن“, „الصواب“, „أخطأ“, „وهم“ usw., sofern eindeutig.

# <reasoning_chunk>...</reasoning_chunk>
# - Explizite Begründungen/Argumentationsketten (z.B. „لأنه...“, „وذلك بسبب...“, „ومن ثم...“) sofern nicht dominierend als grading_* oder dispute_* erfasst.

# <meta_chunk>...</meta_chunk>
# - Rest: Einleitungen, Übergänge, Gliederungen, Zählungen, redaktionelle Hinweise, nicht eindeutig klassifizierbare Passagen.

# HIERARCHIE & LOGIK (section/block/chunk)
# 1) Segmentiere den gesamten Input in <section>-Elemente nach klaren, sichtbaren Abschnittsgrenzen im TXT (z.B. neue Hadith-Nummer, neuer Eintrag, klare Überschrift/Trennung).
# 2) Segmentiere jede <section> in <block>-Elemente basierend auf strikter semantischer Geschlossenheit. Vermeide kleinteilige Fragmentierung. Fasse zusammengehörige Inhalte (z.B. komplette Hadith-Erörterung inkl. Isnād/Matn/Quellen/Urteil) in einen einzigen großen <block>, solange semantisch geschlossen.
# 4) Unterteile jeden <block> in <chunk>-Elemente. Ein <chunk> ist die kleinste semantische Einheit und zeigt welche Elemente zusammengehören bzw. einen Eigenständigen Satz bilden.
# 5) Vollständige Abdeckung: Jeder Charakter des Inputs muss in einem <chunk> innerhalb eines <block> innerhalb einer <section> enthalten sein.

# KONSERVATIVE TAG-STRATEGIE (False-Positive-Minimierung)
# - Grundregel: Im Zweifel KEIN Tag setzen. Untagged Text bleibt als reiner Text im <chunk>.
# - Setze ein XML-Tag nur, wenn der Treffer eindeutig ist.
# - Keine erzwungene Extraktion: Wenn eine Stelle zwischen zwei Typen schwankt (z.B. Quelle vs. Zuschreibung), recherschiere und entscheide dich für das wahrscheinlichere.

# STRIKTE REGELN FÜR DIE AUSGABE
# - Format: Gib die komplette Antwort ausschließlich innerhalb eines ```xml``` Codeblocks zurück.
# - Literal Execution: Entferne, verändere oder kürze niemals den Originalinhalt.
# - Keine Einleitungen, Erklärungen oder Meta-Texte außerhalb des XML.
# - Ausgabe muss wohlgeformtes, syntaktisch korrektes XML sein.
# - Exklusivität: <section>, <block>, <chunk> und die DICT-Chunk-Elemente sind erlaubt.
# - Es wird nichts verändert/verbessert/optimiert oder der gleichen, sondern nur XML Tags hinzugefügt.

# INPUT TXT-DOKUMENT ZUR ANNOTATION habe ich dir in meiner Nachricht angehängt.""",
#     ],
# )

# print(f"response: {response.text}")

# ##init new client

import os
from google import genai
from google.genai import types

# --- KONFIGURATION ---

# 1. Client INITIALISIEREN
# Der API-Key sollte in der Umgebungsvariable GEMINI_API_KEY liegen
client = genai.Client(api_key="AIzaSyAMdfO8kbV58JsMIGAZbyo7hnsMjGxguys")


langs = [
    "ar"
    "en"
    "id"
    "ur"
    "bn"
    "tr"
    "fr"
    "fa"
    "ms"
    "de"
    "ru"
]
START_SURA = 48
PROCESS_SINGLE = False
SINGLE_SURA = 15
import os
import sqlite3
import time
from google import genai
import json

def get_surah_metadata_batch():
    db_path = '/home/muhammed-emin-eser/desk/apps/classify/tools/ML/quran.db'
    start_sura = START_SURA
    # Zuordnung: Sprache -> Variable im Dictionary
    langs_map = {
        "Arabic": "ar", "English": "en", "Indonesian": "id", "Urdu": "ur",
        "Bengali": "bn", "Turkish": "tr", "French": "fr", "Persian": "fa",
        "Malay": "ms", "German": "de", "Russian": "ru"
    }
    
    while True:
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT sura_number, sura_name FROM sura ORDER BY sura_number ASC")
            surahs = cursor.fetchall()

            for sura_num, sura_name_ar in surahs:
                if sura_num < start_sura:
                    continue
                if PROCESS_SINGLE and sura_num != SINGLE_SURA:
                    continue
                print(f"Erstelle Metadaten für Sure {sura_num}...")
                
                # Temporäres Dictionary für die Namen dieser einen Sure
                trans_names = {"ar": sura_name_ar} 

                for full_lang, short_lang in langs_map.items():
                    if short_lang == "ar": continue # Arabisch haben wir schon aus der DB
                    
                    prompt = (
                        f"Handle als reine Daten-Verarbeitungsfunktion. Gib nur das Ergebnis zurück. "
                        f"Aufgabe: Wie heißt die Sure '{sura_name_ar}' auf {full_lang}? (Nur den Namen)"
                    )

                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt,
                    )
                    trans_names[short_lang] = response.text.strip()
                    time.sleep(0.5) # Vermeidung von Rate-Limits

                # Jetzt das finale Metadaten-Objekt mit deinen f-Strings bauen
                meta_data_for_different_languages = {
                    "localizations": {
                        lang_code: {
                            "title": get_title(lang_code, trans_names[lang_code]),
                            "description": get_description(lang_code, trans_names[lang_code], sura_name_ar)
                        } for lang_code in langs_map.values()
                    }
                }
                # Ordner für Metadaten erstellen, falls nicht vorhanden
                os.makedirs('metadata_output', exist_ok=True)

                # Als JSON Datei speichern
                file_name = f"metadata_output/sura_{sura_num:03d}.json"
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(meta_data_for_different_languages, f, ensure_ascii=False, indent=4)

                print(f"Datei gespeichert: {file_name}")
                            
                # Hier kannst du das Objekt nun an deine Upload-Funktion übergeben
                print(f"Metadaten für Sure {sura_num} fertiggestellt.")
                # upload_to_youtube(meta_data_for_different_languages)
                if PROCESS_SINGLE:
                    return

            return
        except Exception:
            output_dir = '/home/muhammed-emin-eser/desk/apps/yt-bulk/metadata_output'
            if os.path.isdir(output_dir):
                file_count = len([
                    name for name in os.listdir(output_dir)
                    if os.path.isfile(os.path.join(output_dir, name))
                ])
            else:
                file_count = 0
            start_sura = file_count + 1
            time.sleep(15)
        finally:
            if conn: conn.close()

def get_title(lang, name):
    titles = {
        "ar": f"سورة {name} | تلاوة هادئة خاشعة | ماهر المعيقلي",
        "en": f"Surah {name} | Emotional & Calm Recitation | Maher Al-Muaiqly",
        "id": f"Surah {name} | Lantunan Merdu & Tenang | Maher Al-Muaiqly",
        "ur": f"سورہ {name} | پرسکون تلاوت | شیخ ماہر المعيقلی",
        "bn": f"সূরা {name} | আবেগপূর্ণ ও শান্ত তেلاওয়াত | মাহের আল-মুয়াইকলি",
        "tr": f"{name} Suresi | Huzur Veren Tilavet | Mahir el-Muaykili",
        "fr": f"Sourate {name} | Récitation Calme & Émouvante | Maher Al-Muaiqly",
        "fa": f"سوره {name} | تلاوت آرام و دلنشین | ماهر المعیقلی",
        "ms": f"Surah {name} | Bacaan Tenang & Syahdu | Maher Al-Muaiqly",
        "de": f"Sure {name} | Emotionale Rezitation | Maher Al-Muaiqly",
        "ru": f"Сура {name} | Красивое и спокойное чтение | Махер аль-Муайкли"
    }
    return titles.get(lang, "")

def get_description(lang, name, name_ar):
    descriptions = {
        "ar": f"استمع إلى تلاوة خاشعة من سورة {name} بصوت الشيخ ماهر المعيقلي. يتضمن الفيديو نص القرآن الكريم مع ترجمة معاني القرآن باللغة الإنجليزية (Dr. Al-Hilali & Dr. Muhsin Khan). \n\n#القرآن #سورة_{name.replace(' ', '_')} #ماهر_المعيقلي",
        "en": f"Experience the heart-touching recitation of Surah {name} by Sheikh Maher Al-Muaiqly. This video features a calm visual background with the English translation by Dr. Muhammad Taqi-ud-Din Al-Hilali & Dr. Muhammad Muhsin Khan. \n\n#Quran #Surah{name.replace(' ', '')} #MaherAlMuaiqly",
        "id": f"Dengarkan lantunan ayat suci Surah {name} yang sangat merdu oleh Syekh Maher Al-Muaiqly. Video ini menampilkan teks Al-Qur'an dengan terjemahan bahasa Inggris oleh Dr. Al-Hilali & Dr. Muhsin Khan. \n\n#AlQuran #Surah{name.replace(' ', '')} #MaherAlMuaiqly",
        "ur": f"شیخ ماہر المعیقلی کی آواز میں سورہ {name} کی خوبصورت تلاوت سماعت فرمائیں۔ اس ویڈیو میں قرآن پاک کے متن کے ساتھ ڈاکٹر الہالی اور ڈاکٹر محسن خان کا انگریزی ترجمہ شامل ہے۔ \n\n#قرآن #سورہ #ماہر_المعیقلی",
        "bn": f"শেখ মাহের আল-মুয়াইকলির কণ্ঠে সূরা {name}-এর হৃদয়স্পর্শী তেলাওয়াত শুনুন। এই ভিডিওতে ড. আল-হিলালি এবং ড. মহসিন খানের ইংরেজি অনুবাদসহ কুরআনের আয়াত রয়েছে। \n\n#কুরআন #সূরা #মাহেরআলমুয়াইকলি",
        "tr": f"Şeyh Mahir el-Muaykili'den {name} Suresi'nin kalbe dokunan kıraatini dinleyin. Bu video, Dr. Al-Hilali ve Dr. Muhsin Khan'ın İngilizce meali ile birlikte Kur'an metnini içermektedir. \n\n#Kuran #Sure #MahirElMuaykili",
        "fr": f"Découvrez la récitation émouvante de la Sourate {name} par le Cheikh Maher Al-Muaiqly. Cette vidéo présente le texte coranique avec la traduction anglaise du Dr Al-Hilali et du Dr Muhsin Khan. \n\n#Coran #Sourate #MaherAlMuaiqly",
        "fa": f"تلاوت دلنشین سوره {name} با صدای شیخ ماهر المعیقلی. این ویدیو شامل متن قرآن کریم همراه با ترجمه انگلیسی دکتر الهلالی و دکتر محسن خان است. \n\n#قرآن #سوره #ماهر_المعیقلی",
        "ms": f"Saksikan bacaan indah Surah {name} oleh Syeikh Maher Al-Muaiqly. Video ini memaparkan teks Al-Quran berserta terjemahan bahasa Inggeris oleh Dr. Al-Hilali & Dr. Muhsin Khan. \n\n#AlQuran #Surah #MaherAlMuaiqly",
        "de": f"Erlebe die herzberührende Rezitation von Sure {name} durch Sheikh Maher Al-Muaiqly. Dieses Video zeigt den Korantext mit der englischen Übersetzung von Dr. Al-Hilali & Dr. Muhsin Khan. \n\n#Koran #Sure #MaherAlMuaiqly",
        "ru": f"Слушайте трогательное чтение суры {name} шейхом Махером аль-Муайкли. Это видео содержит текст Корана с английским переводом доктора Аль-Хилали и доктора Мухсина Хана. \n\n#Коран #Сура #МахерАльМуайкли",
    }
    return descriptions.get(lang, "Description not available")

if __name__ == "__main__":
    get_surah_metadata_batch()
