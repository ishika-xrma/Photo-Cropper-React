from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from image_processor import (
    process_image,
    create_zip
)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://YOUR-VERCEL-APP.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/crop")
async def crop_images(
    files: list[UploadFile]=File(...),
    ratio_type: str=Form(...)
):

    processed = {}

    for file in files:

        data = await file.read()

        result = process_image(
            data,
            ratio_type
        )

        if result:

            processed[
                file.filename
            ] = result

    zip_file = create_zip(
        processed
    )

    return StreamingResponse(
        zip_file,
        media_type="application/zip",
        headers={
            "Content-Disposition":
            "attachment; filename=passport_photos.zip"
        }
    )
