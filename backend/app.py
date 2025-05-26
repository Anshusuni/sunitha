d/from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
from PIL import Image
import numpy as np
import io

# Load the trained model once (globally)
model = load_model("b-h-1000.h5")

# If you have class names, replace this list
class_labels = ['boron', 'healthy']  # <-- Replace with your real 3+ labels if more

# Preprocess image to 150x150
def preprocess_image(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img = img.resize((150, 150))  # Your training size
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalization (if you used it during training)
    return img_array

@app.route("/analyze", methods=["POST"])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    image_file = request.files['image']
    image_data = image_file.read()

    # Optional: Store in MongoDB
    collection.insert_one({
        "filename": image_file.filename,
        "data": Binary(image_data)
    })

    # Preprocess and predict
    processed = preprocess_image(image_data)
    prediction = model.predict(processed)

    # Get predicted class index
    predicted_index = np.argmax(prediction, axis=1)[0]

    # Map to label
    if predicted_index < len(class_labels):
        result_label = class_labels[predicted_index]
    else:
        result_label = str(predicted_index)  # fallback

    return jsonify({
        "filename": image_file.filename,
        "predicted_class": result_label,
        "raw_output": prediction.tolist()
    })
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
from PIL import Image
import numpy as np
import io

# Load the trained model once (globally)
model = load_model("b-h-1000.h5")

# If you have class names, replace this list
class_labels = ['boron', 'healthy']  # <-- Replace with your real 3+ labels if more

# Preprocess image to 150x150
def preprocess_image(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img = img.resize((150, 150))  # Your training size
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalization (if you used it during training)
    return img_array

@app.route("/analyze", methods=["POST"])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    image_file = request.files['image']
    image_data = image_file.read()

    # Optional: Store in MongoDB
    collection.insert_one({
        "filename": image_file.filename,
        "data": Binary(image_data)
    })

    # Preprocess and predict
    processed = preprocess_image(image_data)
    prediction = model.predict(processed)

    # Get predicted class index
    predicted_index = np.argmax(prediction, axis=1)[0]

    # Map to label
    if predicted_index < len(class_labels):
        result_label = class_labels[predicted_index]
    else:
        result_label = str(predicted_index)  # fallback

    return jsonify({
        "filename": image_file.filename,
        "predicted_class": result_label,
        "raw_output": prediction.tolist()
    })
