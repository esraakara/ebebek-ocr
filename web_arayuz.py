import streamlit as st
import easyocr
import cv2
import numpy as np
from pdf2image import convert_from_path
import pdfplumber
import os

# Sayfa Ayarları
st.set_page_config(page_title="ebebek Mevzuat Denetçisi", layout="wide")
st.title("🛡️ Etiket Mevzuat Uygunluk Denetim Sistemi")
st.sidebar.info("ebebek Kalite ve Sertifikasyon Departmanı İçin Geliştirilmiştir")

# 4. Yollar ve Model Tanımlamaları

yasakli_kelimeler = ["MUCİZE", "HASTALIĞI ÖNLER", "KESİN ÇÖZÜM", "TEDAVİ EDER", "ZAYIFLATIR"]

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['tr', 'en'])

reader = load_ocr()

# 5. Dinamik Analiz Paneli
st.subheader("📋 Denetim Merkezi")
col_f1, col_f2 = st.columns(2)

with col_f1:
    spec_file = st.file_uploader("1. Ürün Spesifikasyon Formu (Referans)", type=['pdf'])
with col_f2:
    label_file = st.file_uploader("2. Denetlenecek Ürün Etiketi", type=['pdf'])

if spec_file and label_file:
    with st.spinner('Mevzuat ve Spesifikasyon karşılaştırılıyor...'):
        
        # --- SPESİFİKASYON OKUMA ---
        with pdfplumber.open(spec_file) as pdf:
            spec_metni = "".join([page.extract_text() for page in pdf.pages]).upper()

        # --- ETİKET OCR İŞLEMİ ---
        with open("temp_label.pdf", "wb") as f:
            f.write(label_file.getbuffer())
        
        pages = convert_from_path("temp_label.pdf", 300, poppler_path="")
        img = np.array(pages[0])
        
        results = reader.readtext(img, detail=0)
        label_metni = " ".join(results).upper()

        # --- EKRAN ÇIKTILARI ---
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("🖼️ Denetlenen Etiket Görüntüsü")
            st.image(img, use_column_width=True)

        with c2:
            st.subheader("🔍 Analiz Sonuçları")
            
            # 1. Bölüm: Spesifikasyon Karşılaştırması
            st.write("### 📊 Spesifikasyon Uygunluğu")
            denetim_kriterleri = {
                "Malzeme Türü": ["PP", "POLİPROPİLEN", "SİLİKON", "PASLANMAZ ÇELİK"],
                "Hacim/Kapasite": ["120ML", "150ML", "240ML", "270ML", "300ML"],
                "Yaş Grubu": ["0-6", "6-18", "18+", "0+ AY"],
                "Üretim Yeri": ["TÜRKİYE", "MADE IN TURKEY", "ÇİN", "P.R.C"]
            }

            for baslik, anahtarlar in denetim_kriterleri.items():
                bulunan_deger = [k for k in anahtarlar if k in spec_metni]
                if bulunan_deger:
                    kriter = bulunan_deger[0]
                    if kriter in label_metni:
                        st.write(f"✅ **{baslik} ({kriter}):** Uygun")
                    else:
                        st.write(f"❌ **{baslik} ({kriter}):** Etikette bulunamadı!")

            st.divider()

            # 2. Bölüm: Mevzuat ve Standart Kontrolü
            st.write("### 📜 Mevzuat Uygunluğu")
            standartlar = {
                "14350": "TS EN 14350 (Biberon & İçecek Gereçleri)",
                "1400": "TS EN 1400 (Emzikler)",
                "14372": "EN 14372 (Mutfak Gereçleri)",
                "12586": "TS EN 12586 (Emzik Askıları)",
                "12546": "TS EN 12546 (Termoslar)"
            }

            tespit_edilen = "Bulunamadı"
            for no, isim in standartlar.items():
                if no in label_metni:
                    tespit_edilen = isim
                    break

            if tespit_edilen != "Bulunamadı":
                st.write(f"✅ **Tespit Edilen Standart:** {tespit_edilen}")
            else:
                st.write(f"❌ **Standart No:** Tespit edilemedi")

            # 3. Bölüm: Genel Hijyen ve Yasaklar
            diger_kontroller = {
                "BPA Güvenlik Beyanı (BPA Free)": ["BPA", "FREE", "İÇERMEZ"],
                "Üretici / İthalatçı İzlenebilirlik": ["EBEBEK", "MAĞAZACILIK", "TR-"],
                "Kullanım ve Hijyen Talimatı": ["KAYNAR SU", "5 DAKİKA", "TEMİZLEYİNİZ"]
            }

            for madde, anahtar in diger_kontroller.items():
                if any(k in label_metni for k in anahtar):
                    st.write(f"✅ **{madde}**")
                else:
                    st.write(f"❌ **{madde}**")

            # Mevzuat İhlali (Yasaklı Kelimeler)
            ihlaller = [k for k in yasakli_kelimeler if k in label_metni]
            if ihlaller:
                st.error(f"⚠️ **İHLAL:** {', '.join(ihlaller)} tespit edildi!")
            else:
                st.success("Kritik mevzuat ihlali yok.")

st.divider()
st.caption("ebebek Kalite ve Sertifikasyon Staj Projesi - 2026")          
           

        
