from flask import Flask, request, jsonify
import os  # For file handling
import dlib
from face_recognition import load_image_file, face_encodings, compare_faces
import json


app = Flask(__name__)

# Define a location to store uploaded images
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Placeholder for storing registered filenames and student information
DATA_FILE = 'uploads/registered_data.json'


def load_registered_data():
  """Loads registered student data from JSON file (if it exists)."""
  data = {}
  if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], DATA_FILE)):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], DATA_FILE), 'r') as f:
      data = json.load(f)
  return data


def save_registered_data(data):
  """Saves registered student data to JSON file."""
  with open(os.path.join(app.config['UPLOAD_FOLDER'], DATA_FILE), 'w') as f:
    json.dump(data, f)


# Registered student data (loaded from JSON at startup)
registered_files = load_registered_data()


@app.route('/register', methods=['POST'])
def register():
    # Check if file is uploaded
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    filename = file.filename

    # Check for valid image format (replace with your logic)
    if not filename.endswith('.jpg'):
        return jsonify({'error': 'Invalid image format (only jpg supported)'}), 400

    # Save the uploaded image
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Face recognition logic
    image = load_image_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    detector = dlib.get_frontal_face_detector()
    faces = detector(image)

    # Process each detected face
    for face in faces:
        landmarks = face.landmark

        # Extract face encoding
        face_encoding = face_encodings(image, [landmarks])[0]

        # Store filename, student name, and encoding
        registered_files[filename] = {"student_name": "Student Name", "face_encoding": face_encoding.tolist()}  # Convert encoding to list for JSON

    # Save updated registered data
    save_registered_data(registered_files)

    return jsonify({'message': f'Image uploaded successfully as {filename}'})


@app.route('/match', methods=['POST'])
def match():
    # Check if file is uploaded
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    image = load_image_file(request.files['image'])

    # Face recognition logic
    detector = dlib.get_frontal_face_detector()
    faces = detector(image)

    # Process each detected face
    for face in faces:
        landmarks = face.landmark

        # Extract face encoding of uploaded image
        uploaded_encoding = face_encodings(image, [landmarks])[0]

        # Compare with registered encodings
        for filename, info in registered_files.items():
            registered_encoding = info["face_encoding"]
            match_result = compare_faces([uploaded_encoding], [registered_encoding])[0]
            if match_result:
                return jsonify({'filename': filename, 'student_name': info["student_name"]})

    return jsonify({'message': 'No match found'})


if __name__ == '__main__':
    app.run(debug=True)