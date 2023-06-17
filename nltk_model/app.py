from compareLetter import predict_letter_quality
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "*"}})

app.config['CORS_HEADERS'] = 'Content-Type'



@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    data = request.get_json()
    user_letter = data['userLetter']
    prediction, issues = predict_letter_quality(user_letter)

    response = {
        'prediction': prediction,
        'issues': issues
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run()



import pickle

with open('model.pkl', 'rb') as file:
    model = pickle.load(file)


