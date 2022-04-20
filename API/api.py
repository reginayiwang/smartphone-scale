from flask import Flask, request, jsonify
import joblib
import traceback
import os
from io import TextIOWrapper
import signals

apple_model = joblib.load("models/Apple_model.pkl")
onion_model = joblib.load("models/Onion_model.pkl")
pear_model = joblib.load("models/Pear_model.pkl")
all_model = joblib.load("models/AllFood_model.pkl")
og_apple_model = joblib.load("models/OG_Apple_model.pkl")
og_onion_model = joblib.load("models/OG_Onion_model.pkl")
og_pear_model = joblib.load("models/OG_Pear_model.pkl")
og_all_model = joblib.load("models/OG_AllFood_model.pkl")

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'VibroScale Enhanced API'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        acc_file = TextIOWrapper(request.files['acc'])
        gyro_file = TextIOWrapper(request.files['gyro'])
        food = request.form['food']

        features = signals.make_feats(acc_file, gyro_file, False).reshape(1, -1)
        if food == 'Apple':
            weight = apple_model.predict(features)
        elif food == 'Onion':
            weight = onion_model.predict(features)
        elif food == 'Pear':
            weight = pear_model.predict(features)
        else:
            weight = all_model.predict(features)

        return jsonify({'weight': str(weight)})

    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route('/predict_og', methods=['POST'])
def predict_og():
    try:
        acc_file = TextIOWrapper(request.files['acc'])
        gyro_file = TextIOWrapper(request.files['gyro'])
        food = request.form['food']
        
        features = signals.make_feats(acc_file, gyro_file, True).reshape(1, -1)
        if food == 'Apple':
            weight = og_apple_model.predict(features)
        elif food == 'Onion':
            weight = og_onion_model.predict(features)
        elif food == 'Pear':
            weight = og_pear_model.predict(features)
        else:
            weight = og_all_model.predict(features)

        return jsonify({'weight': str(weight)})

    except:
        return jsonify({'trace': traceback.format_exc()})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)