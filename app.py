from flask import Flask, jsonify
from phenotype import extract_features

app = Flask(__name__)

# sample = "thick peel Harvest clean fruit flesh juicy fruit size is medium average fruit flavor with moderate brix moderate acid High seed number trifoliate aftertaste come back and recheck"


@app.route('/<string:text>')
def process(text):
    return jsonify({"features": extract_features(text)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=True)
