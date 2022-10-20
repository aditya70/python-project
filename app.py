from ast import Param
import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import boto3

AWS_ACCESS_KEY_ID='AKIAYUWWDA4TBFVTOXBR'
AWS_SECRET_ACCESS_KEY='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'
REGION_NAME='us-east-1'

s3 = boto3.client('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key= AWS_SECRET_ACCESS_KEY
                     )

BUCKET_NAME='input-file-cc'

UPLOAD_FOLDER = './uploads'

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@cross_origin()
@app.route('/', methods=['GET'])
def index():  
    return jsonify({"response": "success", "message": "Web Tier Application Started Successfully."})

@cross_origin()
@app.route('/api/v1/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'myfile' not in request.files:
            return jsonify({"response": "failed", "message": "File not found"})
        file = request.files['myfile']
        if file.filename == '':
            return jsonify({"response": "failed", "message": "File name should not be empty"})
        if file:
            file_name = secure_filename(file.filename)
            category_folder = os.path.join(app.config['UPLOAD_FOLDER'])
            os.makedirs(category_folder, exist_ok=True)
            file.save(file_name)
            s3.upload_file(
                Bucket = BUCKET_NAME,
                Filename=file_name,
                Key = file_name
            )
            # os.remove(file_name)   
            return jsonify({"response": "success", "message": "File uploaded successfully"})
    else:
         return jsonify({"response": "failed", "message": request.method + "is not allowed"})  

app.run(host='0.0.0.0')