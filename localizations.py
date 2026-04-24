"""
Localization template — adapt for your content.

`name_<lang>` = the content title in that language.
Return value feeds directly into metadata_output/item_NNN.json["localizations"].
"""


def localizations(
    name_en,
    name_de="",
    name_fr="",
    name_es="",
    name_ar="",
    name_tr="",
    name_id="",
    name_ur="",
    name_bn="",
    name_fa="",
    name_ms="",
    name_ru="",
):
    locs = {
        "en": {
            "title": f"{name_en} | Your Subtitle | Creator Name",
            "description": (
                f"Watch {name_en}. Add your description here.\n\n"
                "#YourTag #AnotherTag"
            ),
        },
    }

    if name_de:
        locs["de"] = {
            "title": f"{name_de} | Untertitel | Ersteller",
            "description": f"Beschreibung für {name_de}.\n\n#DeinTag",
        }
    if name_fr:
        locs["fr"] = {
            "title": f"{name_fr} | Sous-titre | Créateur",
            "description": f"Description pour {name_fr}.\n\n#VotreTag",
        }
    if name_es:
        locs["es"] = {
            "title": f"{name_es} | Subtítulo | Creador",
            "description": f"Descripción de {name_es}.\n\n#TuEtiqueta",
        }
    if name_ar:
        locs["ar"] = {
            "title": f"{name_ar} | العنوان الفرعي",
            "description": f"وصف {name_ar}.\n\n#وسم",
        }
    if name_tr:
        locs["tr"] = {
            "title": f"{name_tr} | Alt Başlık | Oluşturan",
            "description": f"{name_tr} açıklaması.\n\n#Etiket",
        }
    if name_id:
        locs["id"] = {
            "title": f"{name_id} | Subjudul | Pembuat",
            "description": f"Deskripsi {name_id}.\n\n#Tagar",
        }
    if name_ur:
        locs["ur"] = {
            "title": f"{name_ur} | ذیلی عنوان | خالق",
            "description": f"{name_ur} کی تفصیل۔\n\n#ٹیگ",
        }
    if name_bn:
        locs["bn"] = {
            "title": f"{name_bn} | সাবটাইটেল | নির্মাতা",
            "description": f"{name_bn} বিবরণ।\n\n#ট্যাগ",
        }
    if name_fa:
        locs["fa"] = {
            "title": f"{name_fa} | زیرعنوان | سازنده",
            "description": f"توضیحات {name_fa}.\n\n#برچسب",
        }
    if name_ms:
        locs["ms"] = {
            "title": f"{name_ms} | Subtajuk | Pencipta",
            "description": f"Penerangan {name_ms}.\n\n#Teg",
        }
    if name_ru:
        locs["ru"] = {
            "title": f"{name_ru} | Подзаголовок | Автор",
            "description": f"Описание {name_ru}.\n\n#Тег",
        }

    return {"localizations": locs}
