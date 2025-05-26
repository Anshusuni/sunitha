from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import Binary
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["image_analysis"]
collection = db["images"]
@app.route("/")
def home():
    return "Backend running"

@app.route("/analyze", methods=["POST"])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    image = request.files['image']
    image_data = image.read()

    # Store in MongoDB
    collection.insert_one({
        "filename": image.filename,
        "data": Binary(image_data)
    })

    # Dummy analysis (replace with real model logic)
    result = f"Image {image.filename} received and stored."

    return jsonify({"result": result})