def localizations(suren_name_ar, suren_name_en, suren_name_id, suren_name_ur, suren_name_bn,
                  suren_name_tr, suren_name_fr, suren_name_fa,suren_name_ms, suren_name_de, suren_name_ru):
  localizations = {"localizations": {
    "ar": {
      "title": f"سورة {suren_name_ar} | تلاوة هادئة خاشعة | ماهر المعيقلي",
      "description": f"استمع إلى تلاوة خاشعة من سورة {suren_name_ar} بصوت الشيخ ماهر المعيقلي. يتضمن الفيديو نص القرآن الكريم مع ترجمة معاني القرآن باللغة الإنجليزية (Dr. Al-Hilali & Dr. Muhsin Khan). \n\n#القرآن #سورة_{suren_name_ar.replace(' ', '_')} #ماهر_المعيقلي"
    },
    "en": {
      "title": f"Surah {suren_name_en} | Emotional & Calm Recitation | Maher Al-Muaiqly",
      "description": f"Experience the heart-touching recitation of Surah {suren_name_en} by Sheikh Maher Al-Muaiqly. This video features a calm visual background with the English translation by Dr. Muhammad Taqi-ud-Din Al-Hilali & Dr. Muhammad Muhsin Khan. \n\n#Quran #Surah{suren_name_en.replace(' ', '')} #MaherAlMuaiqly"
    },
    "id": {
      "title": f"Surah {suren_name_id} | Lantunan Merdu & Tenang | Maher Al-Muaiqly",
      "description": f"Dengarkan lantunan ayat suci Surah {suren_name_id} yang sangat merdu oleh Syekh Maher Al-Muaiqly. Video ini menampilkan teks Al-Qur'an dengan terjemahan bahasa Inggris oleh Dr. Al-Hilali & Dr. Muhsin Khan. \n\n#AlQuran #Surah{suren_name_id.replace(' ', '')} #MaherAlMuaiqly"
    },
    "ur": {
      "title": f"سورہ {suren_name_ur} | پرسکون تلاوت | شیخ ماہر المعيقلی",
      "description": f"شیخ ماہر المعيقلی کی آواز میں سورہ {suren_name_ur} کی خوبصورت تلاوت سماعت فرمائیں۔ اس ویڈیو میں قرآن پاک کے متن کے ساتھ ڈاکٹر الہالی اور ڈاکٹر محسن خان کا انگریزی ترجمہ شامل ہے۔ \n\n#قرآن #سورہ #ماہر_المعیقلی"
    },
    "bn": {
      "title": f"সূরা {suren_name_bn} | আবেগপূর্ণ ও শান্ত তেলাওয়াত | মাহের আল-মুয়াইকলি",
      "description": f"শেখ মাহের আল-মুয়াইকলির কণ্ঠে সূরা {suren_name_bn}-এর হৃদয়স্পর্শী তেলাওয়াত শুনুন। এই ভিডিওতে ড. আল-হিলালি এবং ড. মহসিন খানের ইংরেজি অনুবাদসহ কুরআনের আয়াত রয়েছে। \n\n#কুরআন #সূরা #মাহেরআলমুয়াইকলি"
    },
    "tr": {
      "title": f"{suren_name_tr} Suresi | Huzur Veren Tilavet | Mahir el-Muaykili",
      "description": f"Şeyh Mahir el-Muaykili'den {suren_name_tr} Suresi'nin kalbe dokunan kıraatini dinleyin. Bu video, Dr. Al-Hilali ve Dr. Muhsin Khan'ın İngilizce meali ile birlikte Kur'an metnini içermektedir. \n\n#Kuran #Sure #MahirElMuaykili"
    },
    "fr": {
      "title": f"Sourate {suren_name_fr} | Récitation Calme & Émouvante | Maher Al-Muaiqly",
      "description": f"Découvrez la récitation émouvante de la Sourate {suren_name_fr} par le Cheikh Maher Al-Muaiqly. Cette vidéo présente le texte coranique avec la traduction anglaise du Dr Al-Hilali et du Dr Muhsin Khan. \n\n#Coran #Sourate #MaherAlMuaiqly"
    },
    "fa": {
      "title": f"سوره {suren_name_fa} | تلاوت آرام و دلنشین | ماهر المعیقلی",
      "description": f"تلاوت دلنشین سوره {suren_name_fa} با صدای شیخ ماهر المعیقلی. این ویدیو شامل متن قرآن کریم همراه با ترجمه انگلیسی دکتر الهلالی و دکتر محسن خان است. \n\n#قرآن #سوره #ماهر_المعیقلی"
    },
    "ms": {
      "title": f"Surah {suren_name_ms} | Bacaan Tenang & Syahdu | Maher Al-Muaiqly",
      "description": f"Saksikan bacaan indah Surah {suren_name_ms} oleh Syeikh Maher Al-Muaiqly. Video ini memaparkan teks Al-Quran berserta terjemahan bahasa Inggeris oleh Dr. Al-Hilali & Dr. Muhsin Khan. \n\n#AlQuran #Surah #MaherAlMuaiqly"
    },
    "de": {
      "title": f"Sure {suren_name_de} | Emotionale Rezitation | Maher Al-Muaiqly",
      "description": f"Erlebe die herzberührende Rezitation von Sure {suren_name_de} durch Sheikh Maher Al-Muaiqly. Dieses Video zeigt den Korantext mit der englischen Übersetzung von Dr. Al-Hilali & Dr. Muhsin Khan. \n\n#Koran #Sure #MaherAlMuaiqly"
    },
    "ru": {
      "title": f"Сура {suren_name_ru} | Красивое и спокойное чтение | Махер аль-Муайкли",
      "description": f"Слушайте трогательное чтение суры {suren_name_ru} шейхом Махером аль-Муайкли. Это видео содержит текст Корана с английским переводом доктора Аль-Хилали и доктора Мухсина Хана. \n\n#Коран #Сура #МахерАльМуайкли"
    }
  }
  }