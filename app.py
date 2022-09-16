from ast import Param
import json
import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import boto3
import botocore
from sqs_listener import SqsListener

AWS_ACCESS_KEY_ID='access_key'
AWS_SECRET_ACCESS_KEY='secret_key'
REGION_NAME='us-east-1'

s3 = boto3.client('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key= AWS_SECRET_ACCESS_KEY
                     )
BUCKET_NAME='temp-bucket1-aditya'
s4 = boto3.resource('s3')

# sqs = boto3.resource("sqs","us-east-1")

client_sqs_rcv = boto3.client('sqs', region_name=REGION_NAME,
                    aws_access_key_id=AWS_ACCESS_KEY_ID, 
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                    
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/594228217638/test-queue-aditya.fifo'
QUEUE_NAME='test-queue-aditya.fifo'
max_queue_messages = 10
message_bodies = []
sqs = boto3.resource('sqs', region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

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
def downloadFile():   
    try:
        s4.Bucket(BUCKET_NAME).download_file('file_example_JPG_100kB.jpeg', 'file_example_JPG_100kB.jpeg')
        print('file downloaded')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise Exception
    return jsonify({"response": "success", "message": "file downloaded "})

def send_message(file_name):
    sqs_client = boto3.client("sqs", region_name="us-east-1")

    message = {"test-key-1": "test-value-1", "file": file_name}
    response = sqs_client.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message),
        MessageGroupId="test"
    )
    print(response)

# def recieve_message():
#     # receive message and delete after processing
#     for message in queue.receive_messages():
#         # process the message
#         print(message.body)
#         # delete the message from the queue after processing
#         message.delete()
# # app.run()

# recieve_message()

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


def receive_queue_msg():
    while True:
        queue_response = client_sqs_rcv.receive_message(
            QueueUrl=QUEUE_URL,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=30,
            WaitTimeSeconds=10
        )
        print(queue_response)
        if queue_response is not None:
            if "Messages" in queue_response:
                Messages=queue_response['Messages']
                if not Messages:
                    message = Messages[0]
                    client_sqs_rcv.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                    )
        else :
            time.sleep(10)


receive_queue_msg()    

# def handle_queue_msg(param1, param2):
#     print("queue msg recieved")
#     print(param1)
#     print(param2)

# while True:
#     messages_to_delete = []
#     for message in queue.receive_messages(
#             MaxNumberOfMessages=max_queue_messages):
#         # process message body
#         print("nmssssggg")
#         print(message)
#         body = json.loads(message.body)
#         print("message recvd from queue")
#         print(body)
#         message_bodies.append(body)
#         # add message to delete
#         messages_to_delete.append({
#             'Id': message.message_id,
#             'ReceiptHandle': message.receipt_handle
#         })

#     # if you don't receive any notifications the
#     # messages_to_delete list will be empty
#     if len(messages_to_delete) == 0:
#         break
#     # delete messages to remove them from SQS queue
#     # handle any errors
#     else:
#         delete_response = queue.delete_messages(
#                 Entries=messages_to_delete)

app.run(host='0.0.0.0', port=5000)

# class MyListener(SqsListener):
#     def handle_message(self, body, attributes, messages_attributes):
#         handle_queue_msg(body['param1'], body['param2'])

# listener = MyListener('my-message-queue', 'my-error-queue')
# listener.listen()




   