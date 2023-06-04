import os
import random
import nltk
import string

from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from spellchecker import SpellChecker


nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')

def synonym_replacement(words, n):
    new_words = words.copy()
    random_word_list = list(set([word for word in words if word not in stopwords.words('english')]))
    random.shuffle(random_word_list)
    num_replaced = 0
    for random_word in random_word_list:
        synonyms = get_synonyms(random_word)
        if len(synonyms) >= 1:
            synonym = random.choice(list(synonyms))
            new_words = [synonym if word == random_word else word for word in new_words]
            num_replaced += 1
        if num_replaced >= n:
            break

    sentence = ' '.join(new_words)
    new_words = sentence.split(' ')

    return new_words

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonym = l.name().replace("_", " ").replace("-", " ").lower()
            synonym = "".join([char for char in synonym if char in ' qwertyuiopasdfghjklzxcvbnm'])
            synonyms.add(synonym)
    if word in synonyms:
        synonyms.remove(word)
    return list(synonyms)

def preprocess_text(text):
    # Преобразуем текст в нижний регистр
    text = text.lower()
    # Удаляем пунктуацию
    text = ''.join([char for char in text if char not in string.punctuation])
    # Удаляем стоп-слова
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)

# Список для хранения писем и их меток
letters = []
labels = []


# Загрузка идеальных писем из файлов
for filename in os.listdir('ideal_letters'):
    with open(os.path.join('ideal_letters', filename), 'r') as f:
        letters.append(f.read())
        labels.append('ideal')

# Загрузка неидеальных писем из файлов
for filename in os.listdir('bad_letters'):
    with open(os.path.join('bad_letters', filename), 'r') as f:
        letters.append(f.read())
        labels.append('bad')

# Применяем функцию предобработки ко всем письмам
letters = [preprocess_text(letter) for letter in letters]

print(letters)
# Добавляем аугментированные письма
augmented_letters = []
for letter in letters:
    words = nltk.word_tokenize(letter)
    augmented_words = synonym_replacement(words, 25)
    augmented_letter = ' '.join(augmented_words)
    augmented_letters.append(augmented_letter)

# Добавляем аугментированные письма и их метки
letters += augmented_letters
labels += labels[:len(augmented_letters)]

# Разделим данные на обучающую и тестовую выборки
train_letters, test_letters, train_labels, test_labels = train_test_split(letters, labels, test_size=0.2)

# Создаем pipeline, который сначала преобразует наши данные в TF-IDF векторы, а затем применяет классификатор наивного Байеса
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

# Обучаем модель на обучающих данных
model.fit(train_letters, train_labels)

# Тестируем модель на тестовых данных
print("Точность модели: ", model.score(test_letters, test_labels))

def predict_letter_quality():
    # Get user input
    print("Please enter your letter. When you're done, enter 'END' on a new line.")
    user_letter = ""
    while True:
        line = input()
        if line == "END":
            break
        user_letter += line + "\n"

    # Preprocess the letter
    processed_letter = preprocess_text(user_letter)

    # Make prediction
    prediction = model.predict([processed_letter])

    # Check for issues
    issues = []

    word_count = len(processed_letter.split())
    print(word_count)
    if word_count < 150:
        issues.append("The letter is too short.")
    elif word_count > 500:
        issues.append("The letter is too long.")

    jargon_words = ["jargon1", "jargon2"]  # replace with your list of jargon words
    if any(jargon_word in processed_letter for jargon_word in jargon_words):
        issues.append("The letter contains jargon or technical terms.")

    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(user_letter)
    print(sentiment)
    print(sentiment['compound'])
    if sentiment['neg'] > 0.07: # Threshold for non positive sentiment
        issues.append("The letter has a negative tone.")

    spell = SpellChecker()
    misspelled = spell.unknown(processed_letter.split())
    print(misspelled)
    print(len(misspelled))
    if len(misspelled) > 18:
        issues.append("The letter contains too many spelling mistakes.")


    # Return the result
    if prediction[0] == 'ideal' and not issues:
        return "ideal"
    else:
        return "bad", issues

# Use the function
print(predict_letter_quality())
