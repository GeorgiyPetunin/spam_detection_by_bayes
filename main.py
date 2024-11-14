import re
from docx import Document
import pandas as pd
import os
import PyPDF4
from tkinter import filedialog
import joblib
import customtkinter as ctk


def count_words(text):
    words = text.split()
    return len(words)

def read_docx(file_path):
    doc = Document(file_path)
    text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
    return text

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf8') as file:
        text = file.read()
    return text

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF4.PdfFileReader(file)
        text = ''
        for page in reader.pages:
            text += page.extractText()
    return text

def split_text_by_punctuation(text):
    # Додані додаткові символи пунктуації до регулярного виразу
    sentences = re.split(r'[?!.,:%№;*(){}=\-+]', text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences

def process_file(file_path):
    file_extension = os.path.splitext(file_path)[1]
    
    if file_extension == '.docx':
        text = read_docx(file_path)
    elif file_extension == '.txt':
        text = read_txt(file_path)
    elif file_extension == '.pdf':
        text = read_pdf(file_path)
    else:
        error_label.configure(text = 'You selected an unsupported file format...')
        raise ValueError('Непідтримуваний формат файлу')
    
    sentences = split_text_by_punctuation(text)
    
    word_counts = [count_words(sentence) for sentence in sentences]
    
    df = pd.DataFrame({'Sentence': sentences, 'Word Count': word_counts})
    return df

def check_file():
    file_path = filedialog.askopenfilename()  # відкрити діалогове вікно для вибору файлу
    
    if file_path:
        file_label.configure(text="Selected file:\n {}".format(os.path.basename(file_path)))

        df = process_file(file_path)

        model = joblib.load('model.pkl')

        labels = model.predict(df['Sentence'])

        df['Label'] = labels

        sum_word_count_label_1 = df.loc[df['Label'] == 1, 'Word Count'].sum()

        total_word_count = df['Word Count'].sum()

        percentage_of_watery_text = sum_word_count_label_1 / total_word_count

        result_label.configure(text="The percentage of watery text in your file = {:.1%}".format(percentage_of_watery_text))


app = ctk.CTk()

app.title('Text verification')
app.geometry('400x200')

check_button = ctk.CTkButton(app, text = 'Check', command = check_file)
check_button.pack(pady = 20)

file_label = ctk.CTkLabel(app, text='')
file_label.pack()

result_label = ctk.CTkLabel(app, text = '')
result_label.pack()

error_label = ctk.CTkLabel(app, text = '')
error_label.pack()

app.mainloop()