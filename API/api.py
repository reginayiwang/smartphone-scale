from flask import Flask, request, jsonify
import sys
import joblib
import traceback
# import pandas as pd
from io import TextIOWrapper
import signals

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        acc_file = TextIOWrapper(request.files['acc'])
        gyro_file = TextIOWrapper(request.files['gyro'])
        food = request.form['food']
        features = signals.make_feats(acc_file, gyro_file)
        if food == 'Apple':
            weight = apple_model.predict(features.reshape(1, -1))
        elif food == 'Onion':
            weight = onion_model.predict(features.reshape(1, -1))
        elif food == 'Pear':
            weight = pear_model.predict(features.reshape(1, -1))
        else:
            weight = all_model.predict(features.reshape(1, -1))
        return jsonify({'weight': str(weight)})
    except:
        return jsonify({'trace': traceback.format_exc()})


if __name__ == '__main__':
    apple_model = joblib.load("Apples_ElasticNet_model.pkl")
    onion_model = joblib.load("Onions_ElasticNet_model.pkl")
    pear_model = joblib.load("Pears_ElasticNet_model.pkl")
    all_model = joblib.load("AllFood_ElasticNet_model.pkl")
    app.run()