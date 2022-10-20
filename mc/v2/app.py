from datetime import datetime
from distutils.log import debug
import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
UPLOAD_FOLDER = './uploads'

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def is_file_extension_valid(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cross_origin()
@app.route('/api/v1/upload', methods=['POST'])
def upload_file():
    
    if request.method == 'POST':
        category = request.form.get("category")
        if category is None:
            return jsonify({"response": "failed", "message": "category should not be empty"})
        if 'image' not in request.files:
            return jsonify({"response": "failed", "message": "File not found"})
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({"response": "failed", "message": "File name should not be empty"})
        if file and is_file_extension_valid(file.filename):
            file_name = secure_filename(file.filename)
            category_folder = os.path.join(app.config['UPLOAD_FOLDER'], category)
            file_name = "{category}_{datetime}.{fileExt}".format(category=category, datetime=datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), fileExt="jpg")

            print("category_folder is", category_folder, file_name)
            os.makedirs(category_folder, exist_ok=True)
            file.save(os.path.join(category_folder, file_name))
            return jsonify({"response": "success", "message": "File uploaded successfully"})
    else:
         return jsonify({"response": "failed", "message": request.method + "is not allowed"})  

@cross_origin()
@app.route('/', methods=['GET'])
def index():   
    return jsonify({"response": "success", "message": "Server Started"})


app.run(host='0.0.0.0',port=80, debug=True)

     
