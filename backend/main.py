from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    BackgroundTasks
)

from fastapi.responses import (
    StreamingResponse
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

import uuid


from image_processor import (
    process_images_batch
)



app = FastAPI()



origins = [

    "http://localhost:5173",

    "https://photo-cropper-react.netlify.app"

]



app.add_middleware(

    CORSMiddleware,

    allow_origins=origins,

    allow_methods=["*"],

    allow_headers=["*"]

)



jobs = {}



@app.post("/create-job")
def create_job(
    total: int = Form(...)
):

    job_id = str(
        uuid.uuid4()
    )


    jobs[
        job_id
    ] = {

        "current": "",

        "done": 0,

        "total": total,

        "finished": False,

        "zip_file": None

    }


    return {
        "job_id": job_id
    }



@app.get("/progress/{job_id}")
def get_progress(
    job_id: str
):

    return jobs.get(
        job_id,
        {}
    )



def process_job(
    files,
    ratio_type,
    job_id
):

    zip_file = process_images_batch(

        files,

        ratio_type,

        jobs,

        job_id

    )


    jobs[
        job_id
    ][
        "zip_file"
    ] = zip_file


    jobs[
        job_id
    ][
        "finished"
    ] = True



@app.post("/crop")
async def crop_images(

    background_tasks:
    BackgroundTasks,

    files:
    list[UploadFile] =
    File(...),

    ratio_type:
    str =
    Form(...),

    job_id:
    str =
    Form(...)

):


    file_data = []


    for file in files:

        data =
        await file.read()


        file_data.append(
            (
                file.filename,
                data
            )
        )


    background_tasks.add_task(

        process_job,

        file_data,

        ratio_type,

        job_id

    )


    return {
        "started": True
    }



@app.get("/download/{job_id}")
def download(
    job_id: str
):

    zip_file = jobs[
        job_id
    ][
        "zip_file"
    ]


    return StreamingResponse(

        zip_file,

        media_type=
        "application/zip",

        headers={

            "Content-Disposition":
            "attachment; filename=passport_photos.zip"

        }

    )