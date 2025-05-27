# backend/app.py

import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.binary import Binary
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
from PIL import Image
import numpy as np
import io

# ─── Flask setup ───────────────────────────────────────────────────────────────
app = Flask(__name__)

# ─── MongoDB setup ────────────────────────────────────────────────────────────
# (set MONGODB_URI in Render's env vars; falls back to localhost for local dev)
mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["lost_and_found"]         # change to your DB name
collection = db["uploads"]            # change to your collection name

# ─── Model loading ─────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "b-h-1000.h5")
model = load_model(MODEL_PATH)
class_labels = ['boron', 'healthy']   # extend if you have more classes

# ─── Helpers ──────────────────────────────────────────────────────────────────
def preprocess_image(img_bytes):
    """
    - Reads raw bytes into a PIL image
    - Resizes to 150×150
    - Converts to numpy array, scales to [0,1]
    - Adds batch dimension
    """
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img = img.resize((150, 150))
    arr = keras_image.img_to_array(img)
    arr = np.expand_dims(arr, axis=0) / 255.0
    return arr

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    # 1) ensure file present
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files['image']
    data = f.read()

    # 2) save raw bytes to MongoDB
    collection.insert_one({
        "filename": f.filename,
        "data": Binary(data)
    })

    # 3) run through your Keras model
    x = preprocess_image(data)
    preds = model.predict(x)
    idx = np.argmax(preds, axis=1)[0]
    label = class_labels[idx] if idx < len(class_labels) else str(idx)

    # 4) respond
    return jsonify({
        "filename": f.filename,
        "predicted_class": label,
        "raw_output": preds.tolist()
    })

# ─── App entrypoint ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    # for local debugging; Render will use gunicorn instead
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
