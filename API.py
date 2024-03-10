import shutil
from fastapi import FastAPI, Depends, Path, File, UploadFile
from pkgutil import get_data
from typing import List
from fastapi import FastAPI, HTTPException
import random
import string
from fastapi.responses import FileResponse
import os
from numpy import delete
from core import speech_to_text, text_generative_model, text_to_speech, text_to_video
from pydantic import BaseModel
from fastapi import Depends, Query, Body
from pymongo import MongoClient
from bson import ObjectId
from utils import assets_dir, push_new_asset
from fastapi.middleware.cors import CORSMiddleware


def random_string(length=7):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(7))


jobs = []


class Job:
    # possible values :
    #  * ["in_progress" , <percentage>]
    # * ['done' , <result>]
    # * ['error' , <error>]
    # * ['not_started']
    status = ['not_started']

    def __init__(self):
        existing_ids = list(set([job.id for job in jobs]))
        while True:
            tmp = random_string()
            if tmp not in existing_ids:
                self.id = tmp
                break

    def started(self):
        self.status = ['in_progress', 0]

    def update_progress(self, new_percentage):
        self.status = ['in_progress', new_percentage]

    def error(self, error_message):
        self.status = ['error', error_message]

    def finished(self, result):
        self.status = ['done', result]


app = FastAPI()
app.add_middleware(CORSMiddleware)


class TextToSpeechBody(BaseModel):
    text: str


@app.post("/models/inference/text_to_speech")
def route(body: TextToSpeechBody):
    asset_id = text_to_speech(body.text)
    return {"asset_id": asset_id}


class SpeechToTextBody(BaseModel):
    asset_id: int


@app.post('/models/inference/speech_to_text')
def route(body: SpeechToTextBody):
    asset_file_path = find_asset_file_path(str(body.asset_id))
    if asset_file_path == None:
        raise HTTPException(
            status_code=404, detail=f"could not find an asset with id = {body.asset_id}")

    result = speech_to_text(asset_file_path)

    return {"result": result["text"]}


class TextGenerativeModelBody(BaseModel):
    prompt: str


@app.post('/models/inference/text_generative_model')
def route(body: TextGenerativeModelBody):
    result = text_generative_model(body.prompt)
    return {"result": result}


class VideoGeneratorModelBody(BaseModel):
    prompt: str


@app.post('/models/inference/text_to_video')
def route(body: VideoGeneratorModelBody):
    asset_id = text_to_video(body.prompt)
    return {"asset_id": asset_id}


@app.get("/models/inference/status/{job_id}")
def route(job_id: str):
    search_result = [item for item in jobs if item.id == job_id]
    if len(search_result) == 0:
        raise HTTPException(
            404, "could not find such a job in server memory")
    return {"status": search_result[0].status}


# Replace with your connection string
client = MongoClient("mongodb://127.0.0.1:27017")


def get_database():
    return client["next-step"]  # Replace with your database name


@app.get("/collections/{collection_name}")
def get_collection_data(collection_name: str):
    collection = get_database()[collection_name]
    documents = list(collection.find())
    data = []
    for doc in documents:
        doc = {"id": str(doc["_id"]), **doc}
        del doc['_id']
        data.append(doc)
    return data


@app.put("/collections/{collection_name}/{id}")
def update_document(collection_name: str, id: str, patch: dict = Body(...), db=Depends(get_database)):
    collection = db[collection_name]
    update_result = collection.update_one(
        {"_id": ObjectId(id)}, {"$set": patch})
    return {"updated_count": update_result.modified_count}


@app.post("/collections/{collection_name}")
def insert_document(collection_name: str, value: dict = Body(...), db=Depends(get_database)):
    collection = db[collection_name]
    result = collection.insert_one(value)
    return {"inserted_id": str(result.inserted_id)}


@app.post("/files/")
async def upload_file(file: UploadFile = File(...)):
    file_path = file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    asset_id = push_new_asset(file_path, delete_orig_file=True)
    return {"filename": file.filename, "asset_id": asset_id}


def find_asset_file_path(asset_id: int):
    existing_filenames = os.listdir(assets_dir)
    tmp = [f for f in existing_filenames if f.split('.')[0] == asset_id]
    if len(tmp) == 0:
        return None
    else:
        return os.path.join(assets_dir, tmp[0])


@app.get("/files/{file_id}")
def download_file(file_id):
    file_path = find_asset_file_path(str(file_id))
    if file_path == None:
        raise HTTPException(
            status_code=404, detail=f"could not find an asset with asset_id = {file_id}")
    return FileResponse(file_path)
