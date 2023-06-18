from flask import Flask, request, jsonify
from flask_cors import CORS
from compareLetter import predict_letter_quality
import pickle


app = Flask(__name__)
CORS(app)

CORS(app, resources={r"/predict": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

# Загрузка модели
with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

@app.route('/predict', methods=['POST'])
def predict():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 415

    data = request.get_json()
    user_letter = data['userLetter']

    # Передаем модель в функцию predict_letter_quality
    prediction, quality_score, issues = predict_letter_quality(user_letter, model)

    response = {
        'prediction': prediction,
        'issues': issues,
        'quality_score': quality_score,
    }
    print(response)

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(port=8000, debug=True)
