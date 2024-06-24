from flask import Flask, request, jsonify
import os
import dlib
from face_recognition import face_encodings, load_image_file, face_locations
import numpy as np
import json
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATA_FILE = 'registered_data.json'


def load_registered_data():
    data = {}
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], DATA_FILE)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    return data


def save_registered_data(data):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], DATA_FILE), 'w') as f:
        json.dump(data, f)


registered_files = load_registered_data()


def load_and_convert_image(file_path):
    # Load image with OpenCV
    image = cv2.imread(file_path)
    if image is None:
        raise ValueError("Failed to load image")

    # Convert image to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return rgb_image


def validate_request(request):
    required_fields = ['image', 'name', 'student_id']

    combined_data = {**request.form, **request.files}
    missing_fields = [field for field in required_fields if field not in combined_data]

    if missing_fields:
        return jsonify({'error': f"{', '.join(missing_fields)} not provided"}), 400

    return None


@app.route('/register', methods=['POST'])
def register():
    validation_error = validate_request(request)
    if validation_error:
        return validation_error

    file = request.files['image']
    filename = file.filename

    if not filename.lower().endswith(('.jpeg', '.jpg')):
        return jsonify({'error': 'Invalid image format (only jpeg/jpg supported)'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        gray = load_and_convert_image(file_path)
        detector = dlib.get_frontal_face_detector()
        faces = detector(gray, 1)

        if not faces:
            return jsonify({'error': 'No faces detected in the image'}), 400

        shape_predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

        for face in faces:
            image = load_image_file(file_path)
            # Compute face encodings using dlib
            face_loc = face_locations(image)
            face_enc = [
                face_encodings(image, [face_loc[i]], model="large")[0]
                for i in range(len(face_loc))
            ]
            registered_files[request.form['student_id']] = {
                "student_name": request.form['name'],
                "student_id": request.form['student_id'],
                "face_encoding": [encoding.tolist() for encoding in face_enc]
            }
            (x, y, w, h) = (face.left(), face.top(), face.width(), face.height())
            cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 0), 2)

        save_registered_data(registered_files)
        return jsonify({
            'status': "OK",
            'code': 200,
            'message': f'Student register successfully',
            'data': {
                'student_name': registered_files[request.form['student_id']]['student_name'],
                "student_id": registered_files[request.form['student_id']]['student_id'],
                'face_encoding': registered_files[request.form['student_id']]['face_encoding']
            }
        })
    except Exception as e:
        print(e)
        return jsonify({'error': f"{e}"}), 500


@app.route('/match', methods=['POST'])
def match():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        gray = load_and_convert_image(file_path)
        detector = dlib.get_frontal_face_detector()
        faces = detector(gray, 1)

        if not faces:
            return jsonify({'error': 'No faces detected in the image'}), 400

        shape_predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

        for face in faces:
            image = load_image_file(file_path)
            # Compute face encodings using dlib
            face_loc = face_locations(image)
            face_enc = [
                face_encodings(image, [face_loc[i]], model="large")[0]
                for i in range(len(face_loc))
            ]

            face_encoded_list = [encoding.tolist() for encoding in face_enc]

            for student in registered_files:
                known_encoding = registered_files[student]['face_encoding'][0]
                distance = np.linalg.norm(np.array(known_encoding) - np.array(face_encoded_list[0]))
                if distance <= 0.6:
                    return jsonify({
                        'status': 'OK',
                        'code': 200,
                        'message': f'Face match successfully',
                        'data': {
                            'student_name': registered_files[student]['student_name'],
                            "student_id": registered_files[student]['student_id']
                        }
                    }), 200

        return jsonify({'message': 'No match found'})
    except Exception as e:
        print(f"Error during face detection: {e}")
        return jsonify({'error': 'Failed to detect face in image'}), 500


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
