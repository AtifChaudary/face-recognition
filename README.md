# Face Recognition Attendance App (Flask)

This Flask application implements a basic student attendance system using face recognition.

## Features:

Registers students by storing their image and face encoding.
Matches uploaded images against registered faces and identifies the student (if found).


## Requirements:

* Python 3.x
* Flask
* dlib (https://github.com/topics/dlib)
* face_recognition (https://github.com/topics/face-recognition)


## Project Structure:

```bash
project_name/
├── app.py                   # Main Flask application file
├── requirements.txt         # File listing required Python packages
├── uploads/                 # Folder to store uploaded student images
│   └── registered_data.json # JSON file to store registered student data
└── venv/                    # Virtual environment folder (optional)
```


## Installation:

1. Clone this repository.
2. Create a virtual environment (recommended) and activate it.
3. Install required packages: `pip install -r requirements.txt`


## Usage:

1. Run the application: python app.py (or flask run)
2. **Register Student:**
   * Send a POST request to `http://localhost:5000/register` with a multipart form data containing the student image file.
   * The response will indicate successful registration and the filename.
3. **Match Student:**
   * Send a POST request to `http://localhost:5000/match` with a multipart form data containing the image to be matched.
   * The response will contain the filename of the matched student and their name (if found), or a message indicating no match.


## Note:

* This is a basic implementation and can be further enhanced with features like error handling, security measures, and a database for student information.
* The face recognition accuracy depends on various factors like lighting and image quality.


## Credits:

* This project utilizes libraries like Flask, dlib, and face_recognition. Refer to their respective documentation for further details.