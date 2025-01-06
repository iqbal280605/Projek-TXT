import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import spacy
import joblib
import os
import sys
from heapq import nlargest
from spacy.lang.en.stop_words import STOP_WORDS

if getattr(sys, 'frozen', False):
    current_dir = sys._MEIPASS2
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

model_alur_path = os.path.join(current_dir, 'D:\kuliah\desktop\model_alur_naive_bayes.pkl')
model_tema_path = os.path.join(current_dir, 'D:\kuliah\desktop\model_tema_naive_bayes.pkl')
vectorizer_path = os.path.join(current_dir, 'D:\kuliah\desktop\model_vectorizer.pkl')
csv_orang_path = os.path.join(current_dir, 'D:\kuliah\desktop\orang.csv')
csv_tempat_path = os.path.join(current_dir, 'D:\kuliah\desktop\datatempat.csv')
bg_image_path = os.path.join(current_dir, 'D:\kuliah\desktop\Background.png')

model_alur = joblib.load(model_alur_path)  
model_tema = joblib.load(model_tema_path)  
vectorizer = joblib.load(vectorizer_path)

def tokoh(text):
    orang = set()

    punctuation = '''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'''
    for char in punctuation:
        text = text.replace(char, "")

    file_orang = open(csv_orang_path, 'r', encoding='utf-8')
    data_csv = [line.strip() for line in file_orang]

    for item in text.split():
        if item in data_csv:
            orang.add(item)

    return list(orang)

def latar_tempat(text):
    tempat = set()

    punctuation = '''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'''
    for char in punctuation:
        text = text.replace(char, "")

    file_tempat = open(csv_tempat_path, 'r', encoding='utf-8')
    data_csv = [line.strip() for line in file_tempat]

    for item in text.split():
        if item in data_csv:
            tempat.add(item)

    return list(tempat)

def tema(text):
    transformed_text = vectorizer.transform([text])
    hasil_prediksi = model_tema.predict(transformed_text)

    if hasil_prediksi[0] == 1:
        label = 'Romantis'
    elif hasil_prediksi[0] == 2:
        label = 'Persahabatan'
    elif hasil_prediksi[0] == 3:
        label = 'Petualangan'
    elif hasil_prediksi[0] == 4:
        label = 'Perjuangan'
    elif hasil_prediksi[0] == 5:
        label = 'Religi'
    else:
        label = 'Label tidak dikenali'

    return label

def alur(text):
    transformed_text = vectorizer.transform([text])
    hasil_prediksi = model_alur.predict(transformed_text)

    if hasil_prediksi[0] == 1:
        label = 'Maju'
    elif hasil_prediksi[0] == 2:
        label = 'Mundur'
    elif hasil_prediksi[0] == 3:
        label = 'Campuran'
    else:
        label = 'Label tidak dikenali'

    return label

def ringkasancerita(text):
    stopwords = STOP_WORDS
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    doc.text

    punctuation = "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'\t\n\r\x0b\x0c'"

    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1

    max_frequency = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word]/max_frequency

    sentence_tokens = [sent for sent in doc.sents]

    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]

    select_lenght = int(len(sentence_tokens)*0.3)
    summary = nlargest(select_lenght, sentence_scores, key= sentence_scores.get)
    final_summary = [word.text for word in summary]
    summary_new = ' '.join(final_summary)
    return summary_new

def analyze_story_elements(text):
    if not text:
        return "Error: Teks kosong atau tidak valid."

    tokoh_cerita = tokoh(text)
    latar_tempat_cerita = latar_tempat(text)
    tema_cerita = tema(text)
    alur_cerita = alur(text)
    ringkasan_cerita = ringkasancerita(text)

    analysis = ["      ===== ANALISIS UNSUR CERITA =====\n"]

    analysis.append("TOKOH:")
    if tokoh_cerita:
        analysis.extend([f"- {char}" for char in tokoh_cerita])
    else:
        analysis.append("(Tidak ditemukan tokoh yang jelas)")

    analysis.append("\nLATAR:\nTempat:")
    if latar_tempat_cerita:
        analysis.extend([f"- {place}" for place in latar_tempat_cerita])
    else:
        analysis.append("(Tidak ditemukan latar tempat yang jelas)")

    analysis.append("\nALUR CERITA:")
    analysis.append("- " + alur_cerita)

    analysis.append("\nTEMA CERITA:")
    analysis.append("- " + tema_cerita)

    analysis.append("\nRINGKASAN CERITA:")
    analysis.append(ringkasan_cerita)

    return "\n".join(analysis)

def generate_analysis():
    analysis_box.delete(1.0, tk.END)

    story_text = story_input.get(1.0, tk.END).strip()
    if story_text:
        text = story_text
    else:
        messagebox.showwarning("Tidak Ada Input", "Silakan ketik cerita terlebih dahulu.")
        return

    analysis_result = analyze_story_elements(text)
    analysis_box.insert(tk.END, analysis_result)

root = tk.Tk()
root.title("Story Mancer")
root.resizable(False, False)
root.geometry("500x666")

bg_image = Image.open(bg_image_path)
bg_image = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(root, width=bg_image.width(), height=bg_image.height())
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_image, anchor="nw")

story_input = ScrolledText(root, width=30, height=1, wrap=tk.WORD, font=("Arial", 10), borderwidth=0, relief="solid")
canvas.create_window(250, 118, window=story_input)

analysis_box = ScrolledText(root, width=44, height=20.3, wrap=tk.WORD, font=("Arial", 10), borderwidth=0, relief="solid")
canvas.create_window(250, 384, window=analysis_box)

generate_button = tk.Button(root, text="Generate", command=generate_analysis, font=("Arial", 8), bg="#294173", fg="white", width=10, height=0, pady=0)
canvas.create_window(250, 165, window=generate_button)

root.mainloop()
