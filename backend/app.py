# backend/app.py

import os
import io
import numpy as np
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.binary import Binary
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
from PIL import Image

# ─── Flask setup ───────────────────────────────────────────────────────────────
app = Flask(__name__)

# ─── MongoDB setup (optional) ──────────────────────────────────────────────────
# If you don't need Mongo, you can delete everything from here down to 'collection = ...'
mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["lost_and_found"]       # change to your DB name
collection = db["uploads"]          # change to your collection name

# ─── Model loading ─────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "b-h-1000.h5")
model = load_model(MODEL_PATH)
# Update this list to match your model’s classes:
class_labels = ['boron', 'healthy']

# ─── Image preprocessing helper ────────────────────────────────────────────────
def preprocess_image(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img = img.resize((150, 150))  # match your training size
    arr = keras_image.img_to_array(img)
    arr = np.expand_dims(arr, axis=0) / 255.0
    return arr

# ─── Analyze endpoint ──────────────────────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    # 1) check for file
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files['image']
    data = f.read()

    # 2) (optional) store raw bytes in MongoDB
    collection.insert_one({
        "filename": f.filename,
        "data": Binary(data)
    })

    # 3) run model
    x = preprocess_image(data)
    preds = model.predict(x)
    idx = int(np.argmax(preds, axis=1)[0])
    label = class_labels[idx] if idx < len(class_labels) else str(idx)

    # 4) respond
    return jsonify({
        "filename": f.filename,
        "predicted_class": label,
        "raw_output": preds.tolist()
    })

# ─── Entrypoint for local testing ──────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
