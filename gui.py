import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import spacy
import pickle
from tkinter import messagebox
import PyPDF2
import re
import joblib
import os 
import sys
from heapq import nlargest
from spacy.lang.en.stop_words import STOP_WORDS

class StoryMancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Story Mancer")
        self.root.resizable(False, False)

        self.bg_image = Image.open(self.resource_path("background.png"))
        file_path = self.resource_path("background.png")
        print(f"Looking for file at: {file_path}")
        self.bg_image = ImageTk.PhotoImage(self.bg_image)

        self.root.geometry("500x666")

        self.canvas = tk.Canvas(self.root, width=self.bg_image.width(), height=self.bg_image.height())
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # Kotak teks untuk mengetik cerita
        self.story_input = ScrolledText(self.root, width=30, height=1, wrap=tk.WORD, font=("Arial", 10), borderwidth=0, relief="solid")
        self.canvas.create_window(250, 118, window=self.story_input)

        # Kotak teks untuk hasil analisis
        self.analysis_box = ScrolledText(self.root, width=44, height=20.3, wrap=tk.WORD, font=("Arial", 10), borderwidth=0, relief="solid")
        self.canvas.create_window(250, 384, window=self.analysis_box)

        # Tombol untuk menganalisis cerita
        self.generate_button = tk.Button(self.root, text="Generate", command=self.generate_analysis, font=("Arial", 8), bg="#294173", fg="white", width=10, height=0, pady=0)
        self.canvas.create_window(250, 165, window=self.generate_button)

        self.file_path = None

    def generate_analysis(self):
        self.analysis_box.delete(1.0, tk.END)

        # Periksa apakah ada teks di kotak input manual
        story_text = self.story_input.get(1.0, tk.END).strip()

        if story_text:  # Jika cerita diketik oleh pengguna
            text = story_text
        elif self.file_path:  # Jika pengguna mengunggah file PDF
            text = self.extract_text_from_pdf(self.file_path)
        else:
            messagebox.showwarning("Tidak Ada Input", "Silakan ketik cerita terlebih dahulu.")
            return

        if not text:
            messagebox.showerror("Error", "Gagal membaca teks cerita.")
            return

        analysis_result = self.analyze_story_elements(text)
        self.analysis_box.insert(tk.END, analysis_result)
    
    def resource_path(self,relative_path):
        if getattr(sys, 'frozen', False):
            current_dir = sys._MEIPASS  
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__)) 

        return os.path.join(current_dir, relative_path)
    
    def tokoh(self,text):
        orang = set()

        tokoh_file_path = self.resource_path("Orang.csv")
        file_orang = open(tokoh_file_path, 'r', encoding='utf-8')
        data_csv = [line.strip() for line in file_orang]

        for item in text.split():
            if item in data_csv:
                orang.add(item)

        file_orang.close()

        pickle_file_path = self.resource_path("model_ner.pkl")
        file = open(pickle_file_path, "rb")
        ner_tokoh = pickle.load(file)
        tokoh_cerita = ner_tokoh(text)
        for ent in tokoh_cerita.ents:
            if ent.label_ in ['PERSON']:
                orang.add(ent.text)
        
        file.close()

        return list(orang)

    def latar_tempat(self,text):
        tempat = set()

        tokoh_file_path = self.resource_path("datatempat.csv")
        file_tempat = open(tokoh_file_path, 'r', encoding='utf-8')
        data_csv = [line.strip() for line in file_tempat]

        for item in text.split():
            if item in data_csv:
                tempat.add(item)

        file_tempat.close()

        pickle_file_path = self.resource_path("model_ner.pkl")
        file = open(pickle_file_path, "rb")
        ner_tokoh = pickle.load(file)
        tokoh_cerita = ner_tokoh(text)
        for ent in tokoh_cerita.ents:
            if ent.label_ in ['LOCATION']:
                tempat.add(ent.text)

        file.close()

        return list(tempat)

    def Vektorizer_alur_tema(self):
        vectorizer = self.resource_path('model_vectorizer.pkl')
        vectorizerr = joblib.load(vectorizer)

        return vectorizerr

    def tema(self,text):
        model_tema = self.resource_path('model_tema_naive_bayes.pkl')
        model_temaa = joblib.load(model_tema)  

        vectorizer_tema = self.Vektorizer_alur_tema()

        X_new = vectorizer_tema.transform([text])  
        hasil_prediksi = model_temaa.predict(X_new) 

        if hasil_prediksi[0] == 1:
            label = 'Romantis'
        elif hasil_prediksi[0] == 2:
            label = 'Persahabatan'
        elif hasil_prediksi[0] == 3:
            label = 'Pahlawan'
        elif hasil_prediksi[0] == 4:
            label = 'Petualangan'
        else:
            label = 'Label tidak dikenali'

        return label
    
    def alur(self,text):
        model_alur = self.resource_path('model_naive_bayes.pkl')
        model_alurr = joblib.load(model_alur)  

        vectorizer_alur = self.Vektorizer_alur_tema()

        X_new = vectorizer_alur.transform([text])  
        hasil_prediksi = model_alurr.predict(X_new) 

        if hasil_prediksi[0] == 1:
            label = 'Maju'
        elif hasil_prediksi[0] == 2:
            label = 'Mundur'
        elif hasil_prediksi[0] == 3:
            label = 'Campuran'
        else:
            label = 'Label tidak dikenali'

        return label
    def ringkasancerita(self,text):
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
    
    def analyze_story_elements(self, text):
        if not text:
            return "Error: Teks kosong atau tidak valid."
        
        # Analisis setiap unsur cerita
        tokoh_cerita = self.tokoh(text)
        latar_tempat = self.latar_tempat(text)
        tema_cerita = self.tema(text)
        alur_cerita= self.alur(text)
        ringkasan_cerita = self.ringkasancerita(text)

        analysis = []
        analysis.append("       ===== ANALISIS UNSUR CERITA =====\n")
        
        analysis.append("TOKOH:")
        if tokoh_cerita:
            analysis.extend([f"- {char}" for char in tokoh_cerita])
        else:
            analysis.append("(Tidak ditemukan tokoh yang jelas)")
        
        analysis.append("\nLATAR:")
        analysis.append("Tempat:")
        if latar_tempat:
            analysis.extend([f"- {place}" for place in latar_tempat])
        else:
            analysis.append("(Tidak ditemukan latar tempat yang jelas)")
        
        # analysis.append("\nWaktu:")
        # if settings['waktu']:
        #     analysis.extend([f"- {time}" for time in settings['waktu']])
        # else:
        #     analysis.append("(Tidak ditemukan latar waktu yang jelas)")
        # analysis.append("")
        
        analysis.append("\nALUR CERITA:")
        if tema_cerita:
            analysis.append("- " + tema_cerita)
        else:
            analysis.append("Tidak ditemukan tema yang jelas")
        analysis.append("")

        analysis.append("\nTEMA CERITA:")
        if alur_cerita:
            analysis.append("- " + alur_cerita)
        else:
            analysis.append("Tidak ditemukan alur yang jelas")
        analysis.append("")

        analysis.append("\nRINGKASAN CERITA:")
        analysis.append(ringkasan_cerita)
        
        return "\n".join(analysis)

root = tk.Tk()
app = StoryMancerApp(root)
root.mainloop()