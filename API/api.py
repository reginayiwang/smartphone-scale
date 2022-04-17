from flask import Flask, request, jsonify
import joblib
import traceback
from io import TextIOWrapper
import signals

apple_model = joblib.load("Apples_RFEElasticNet_model.pkl")
onion_model = joblib.load("Onions_RFEElasticNet_model.pkl")
pear_model = joblib.load("Pears_RFEElasticNet_model.pkl")
all_model = joblib.load("AllFood_RFEElasticNet_model.pkl")

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
    app.run()