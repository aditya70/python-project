import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import boto3


AWS_ACCESS_KEY_ID='access_key'
AWS_SECRET_ACCESS_KEY='secret_access/-key'
REGION_NAME='us-east-1'

s3 = boto3.client('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key= AWS_SECRET_ACCESS_KEY
                     )
BUCKET_NAME='temp-bucket-aditya'

sqs = boto3.resource("sqs","us-east-1")
queue = sqs.get_queue_by_name(QueueName="test-queue-aditya.fifo")

client = boto3.client(
    'dynamodb',
    aws_access_key_id     = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name           = REGION_NAME,
)

resource = boto3.resource(
    'dynamodb',
    aws_access_key_id     = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name           = REGION_NAME,
)

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
        if 'file' not in request.files:
            return jsonify({"response": "failed", "message": "File not found"})
        file = request.files['file']
        if file.filename == '':
            return jsonify({"response": "failed", "message": "File name should not be empty"})
        if file and is_file_extension_valid(file.filename):
            file_name = secure_filename(file.filename)
            category_folder = os.path.join(app.config['UPLOAD_FOLDER'], category)
            print("category_folder is", category_folder)
            os.makedirs(category_folder, exist_ok=True)
            # file.save(os.path.join(category_folder, file_name))
            file.save(file_name)
            s3.upload_file(
                    Bucket = BUCKET_NAME,
                    Filename=file_name,
                    Key = file_name
                )
            os.remove(file_name)   
            send_message(file_name)
            return jsonify({"response": "success", "message": "File uploaded successfully"})
    else:
         return jsonify({"response": "failed", "message": request.method + "is not allowed"})  

@cross_origin()
@app.route('/comments', methods=['POST'])
def create_comment():   
    data = request.data      
    print("comments data ",data)
    return jsonify({"response": "success", "message": "comment created"})

@cross_origin()
@app.route('/', methods=['GET'])
def index():   
    return jsonify({"response": "success", "message": "comment created"})

@cross_origin()
@app.route('/add', methods=['GET'])
def addItem():   
    print("add item to db")
    response = addItemToBook(1,'test-title','test-author')
    print(response)
    print("item operation in dynamodb")
    return jsonify({"response": "success", "message": "comment created"})

@cross_origin()
@app.route('/downlaod/s3', methods=['GET'])
def addItem():   
    print("add item to db")
    response = addItemToBook(1,'test-title','test-author')
    print(response)
    print("item operation in dynamodb")
    return jsonify({"response": "success", "message": "comment created"})

def send_message(file_name):
    sqs_client = boto3.client("sqs", region_name="us-east-1")

    message = {"test-key-1": "test-value-1", "file": file_name}
    response = sqs_client.send_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/594228217638/test-queue-aditya.fifo",
        MessageBody=json.dumps(message),
        MessageGroupId="test"
    )
    print(response)

def recieve_message():
    # receive message and delete after processing
    for message in queue.receive_messages():
        # process the message
        print(message.body)
        # delete the message from the queue after processing
        message.delete()
# app.run()

recieve_message()

BookTable = resource.Table('product')

def addItemToBook(id, title, author):

    response = BookTable.put_item(
        Item = {
            'id'     : id,
            'title'  : title,
            'author' : author
        }
    )

    return response  



app.run(host='0.0.0.0', port=5000)


   