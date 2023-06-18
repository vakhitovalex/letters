import os
import random
import nltk
import string
import pickle


from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline, Pipeline, FeatureUnion
from sklearn.model_selection import train_test_split
from spellchecker import SpellChecker
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import FunctionTransformer
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')



class TextLengthExtractor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [[len(text)] for text in X]

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

def preprocess_text(text):
    text = text.lower()
    text = ''.join([char for char in text if char not in string.punctuation])
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    words = [word for word in words if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(words)

letters = []
labels = []

for filename in os.listdir('ideal_letters'):
    with open(os.path.join('ideal_letters', filename), 'r') as f:
        letters.append(f.read())
        labels.append('ideal')

for filename in os.listdir('bad_letters'):
    with open(os.path.join('bad_letters', filename), 'r') as f:
        letters.append(f.read())
        labels.append('bad')

letters = [preprocess_text(letter) for letter in letters]

augmented_letters = []
for letter in letters:
    words = nltk.word_tokenize(letter)
    augmented_words = synonym_replacement(words, 5)
    augmented_letter = ' '.join(augmented_words)
    augmented_letters.append(augmented_letter)

letters += augmented_letters
labels += labels[:len(augmented_letters)]

train_letters, test_letters, train_labels, test_labels = train_test_split(letters, labels, test_size=0.2)

model = Pipeline([
    ('features', FeatureUnion([
        ('tfidf', TfidfVectorizer()),
        ('length', TextLengthExtractor())
    ])),
    ('classifier', RandomForestClassifier(n_estimators=100, max_depth=15))
])

model.fit(train_letters, train_labels)
predictions = model.predict(test_letters)

print("Model Accuracy: ", model.score(test_letters, test_labels))

def predict_letter_quality(user_letter, model):
    processed_letter = preprocess_text(user_letter)
    prediction = model.predict([processed_letter])
    prediction_proba = model.predict_proba([processed_letter])

    prob_ideal = prediction_proba[0][model.classes_.tolist().index('ideal')]

    if prediction[0] == 'ideal':
        quality_score = prob_ideal * 100
    else:
        quality_score = (1 - prob_ideal) * 100

    issues = []
    word_count = len(processed_letter.split())
    if word_count < 150:
        issues.append("The letter is too short.")
    elif word_count > 500:
        issues.append("The letter is too long.")

    jargon_words = ['advocate', 'agendize', 'aggregate', 'assess', 'alignment', 'applications', 'articulation', 'assessment', 'best practices', 'brain research', 'business partnerships', 'capacity', 'classification', 'cohorts', 'concept maps', 'Common Core Standards', 'communities', 'competencies', 'content', 'convergence', 'career and technical education', 'critical thinking', 'culminating products', 'curiosity', 'curriculum compacting', 'curriculum integration', 'curriculum', 'debriefs', 'decision-making', 'dialogue', 'differentiated lessons', 'education', 'efficacies', 'enduring understandings', 'engagement structures', 'enrichment', 'ESLR\'s', 'experiences', 'explicit direct instruction', 'facilitators', 'functionalities', 'goals', 'guiding coalitions', 'growth mindsets', 'higher-order thinking', 'infrastructures', 'initiatives', 'inquiry', 'instruction', 'interfaces', 'learning', 'Learning Focused Lesson Plans', 'learning styles', 'liaisons', 'life-long learning', 'living documents', 'manipulatives', 'mastery learning', 'methodologies', 'models', 'multiple intelligences', 'need-to-knows']
    jargon_count = sum(1 for jargon_word in jargon_words if jargon_word in processed_letter)
    if jargon_count >= 3:
        issues.append(f"The letter contains {jargon_count} jargon or technical terms.")

    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(user_letter)
    if sentiment['neg'] > 0.07:
        issues.append("The letter has a negative tone.")

    spell = SpellChecker()
    misspelled = spell.unknown(processed_letter.split())
    if len(misspelled) > 18:
        issues.append("The letter contains too many spelling mistakes.")

    if prediction[0] == 'ideal' and not issues:
        return "ideal", quality_score, []
    else:
        return "bad", quality_score, issues

param_grid = {
    'classifier__n_estimators': [50, 100, 200, 300],
    'classifier__max_depth': [10, 15, 20, 30]
}

grid_search = GridSearchCV(model, param_grid, cv=5)
grid_search.fit(train_letters, train_labels)

best_model = grid_search.best_estimator_

print("Best n_estimators: ", grid_search.best_params_['classifier__n_estimators'])
print("Best max_depth: ", grid_search.best_params_['classifier__max_depth'])

print("Classification Report:")
print(classification_report(test_labels, predictions))

print("Confusion Matrix:")
print(confusion_matrix(test_labels, predictions))


with open('model.pkl', 'wb') as file:
    pickle.dump(model, file)
