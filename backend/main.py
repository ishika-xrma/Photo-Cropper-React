from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import uuid

from image_processor import (
    process_images_batch
)


app = FastAPI()


origins = [
    "http://localhost:5173",
    "https://photo-cropper-react.netlify.app",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["job-id"]
)


jobs = {}


@app.get("/")
def home():

    return {
        "status": "alive"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.get("/progress/{job_id}")
def get_progress(
    job_id: str
):

    return jobs.get(
        job_id,
        {}
    )


@app.post("/crop")
async def crop_images(
    files: list[UploadFile] = File(...),
    ratio_type: str = Form(...)
):

    job_id = str(
        uuid.uuid4()
    )

    jobs[job_id] = {
        "current": "",
        "done": 0,
        "total": len(files),
        "finished": False
    }


    file_data = []


    for file in files:

        data = await file.read()

        file_data.append(
            (
                file.filename,
                data
            )
        )


    zip_file = process_images_batch(
        file_data,
        ratio_type,
        jobs,
        job_id
    )


    jobs[
        job_id
    ][
        "finished"
    ] = True


    return StreamingResponse(
        zip_file,
        media_type="application/zip",
        headers={
            "job-id": job_id,
            "Content-Disposition":
            "attachment; filename=passport_photos.zip"
        }
    )