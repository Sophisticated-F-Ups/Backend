from fastapi import FastAPI, File, UploadFile, status
import os
from dotenv import load_dotenv
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World"}

# Receive video file from client and get the file extension using fastapi
@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    # Get the extension of the file
    _ , extension = filename.split('.')
    #Write the file
    with open(f"file.{extension}" , "wb") as f:
        f.write(file.file.read())

    #Upload the video or audio to assembly ai
    file = upload_file(open(f"file.{extension}" , "rb"))
    #Remove the file
    os.remove(f"file.{extension}")
    #Get the response from assembly ai
    response = get_text(file[0], file[1])
    index = 0
    #Check if response was not ready
    while response["status"] != 'completed':
        index += 1
        response = get_text(file[0], file[1])
    print("Requests to assemblyAI: {index} times done")
    return response

def upload_file(fileObj):
    '''
    Parameter:
    fileObj: The File Object to transcribe
    Return Value:
    token : The API key
    transcribe_id: The ID of the file which is being transcribed
    '''
    load_dotenv()
    token = os.getenv('API_TOKEN')
    file_url = get_url(token, fileObj)
    transcribe_id = get_transcribe_id(token,file_url)
    return token,transcribe_id

def get_text(token, transcribe_id):
    '''
    --Params--
    token: The API key
    transcribe_id: The ID of the file which is being
     Return Value: result
     result : The response object
    ''' 
    endpoint= f'https://api.assemblyai.com/v2/transcript/{transcribe_id}'
    headers = {'authorization': token}
    result = requests.get(endpoint, headers=headers).json()
    return result

def get_transcribe_id(token,url):
    '''
    --Params--
    token: The API key
    url : Url to uploaded file
    Return Value: id
    id : The transcribe id of the file
    '''
    endpoint = 'https://api.assemblyai.com/v2/transcript'
    json = {'audio_url': url}
    headers = {'authorization': token, 'content-type': 'application/json'}
    response = requests.post(endpoint, json=json, headers=headers)
    transcribe_id = response.json()['id']
    print('Made request and file is currently queued')
    return transcribe_id

def get_url(token,data):
    '''
    --Params--
    token: The API key
    data : The File Object to upload
    Return Value: url
    url : Url to uploaded file
    '''
    headers = {'authorization': token}
    response = requests.post('https://api.assemblyai.com/v2/upload',
    headers=headers,
    data=data)
    url = response.json()['upload_url']
    print('Uploaded File and got temporary URL to file')
    return url