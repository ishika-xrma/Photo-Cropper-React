import cv2
import numpy as np
import io
import zipfile


def enhance_image(image):
    """
    Improve image quality for better face detection.
    """

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(
        lab
    )

    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8)
    )

    l = clahe.apply(
        l
    )

    lab = cv2.merge(
        (l, a, b)
    )

    enhanced = cv2.cvtColor(
        lab,
        cv2.COLOR_LAB2BGR
    )

    kernel = np.array(
        [
            [-1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1]
        ]
    )

    return cv2.filter2D(
        enhanced,
        -1,
        kernel
    )


def detect_face(image):
    """
    Detect largest face using multiple cascades.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    cascade_paths = [
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml",

        cv2.data.haarcascades +
        "haarcascade_frontalface_alt2.xml"
    ]

    all_faces = []

    for path in cascade_paths:

        detector = cv2.CascadeClassifier(
            path
        )

        detections = detector.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=7,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(detections) > 0:
            all_faces.extend(
                detections.tolist()
            )

    if not all_faces:
        return None

    x, y, w, h = sorted(
        all_faces,
        key=lambda f: f[2] * f[3],
        reverse=True
    )[0]

    img_h, img_w = image.shape[:2]

    pad_w = int(w * 0.20)
    pad_h = int(h * 0.20)

    x = max(
        0,
        x - pad_w
    )

    y = max(
        0,
        y - pad_h
    )

    w = min(
        img_w - x,
        w + pad_w * 2
    )

    h = min(
        img_h - y,
        h + pad_h * 2
    )

    return x, y, w, h


def calculate_crop(
    image,
    face,
    ratio_type="standard"
):
    """
    Smart crop with face positioning metrics.
    """

    x, y, w, h = face

    img_h, img_w = image.shape[:2]

    target_ratio = (
        2.0 / 2.3
        if ratio_type == "standard"
        else 1.0
    )

    face_fraction = (
        0.70
        if ratio_type == "standard"
        else 0.65
    )

    cx = x + w // 2
    cy = y + h // 2

    crop_h = int(
        h / face_fraction
    )

    crop_w = int(
        crop_h * target_ratio
    )

    x1 = cx - crop_w // 2
    y1 = cy - crop_h // 2

    x2 = x1 + crop_w
    y2 = y1 + crop_h

    if x1 < 0:
        x2 -= x1
        x1 = 0

    if y1 < 0:
        y2 -= y1
        y1 = 0

    if x2 > img_w:
        x1 -= (
            x2 - img_w
        )
        x2 = img_w

    if y2 > img_h:
        y1 -= (
            y2 - img_h
        )
        y2 = img_h

    x1 = max(
        0,
        x1
    )

    y1 = max(
        0,
        y1
    )

    x2 = min(
        img_w,
        x2
    )

    y2 = min(
        img_h,
        y2
    )

    if (
        x2 - x1 < 300
        or
        y2 - y1 < 300
    ):
        return None

    return x1, y1, x2, y2


def process_image(
    file_bytes,
    ratio_type
):

    nparr = np.frombuffer(
        file_bytes,
        np.uint8
    )

    image = cv2.imdecode(
        nparr,
        cv2.IMREAD_COLOR
    )

    if image is None:
        return None

    enhanced = enhance_image(
        image
    )

    face = detect_face(
        enhanced
    )

    if face is None:
        return None

    crop = calculate_crop(
        image,
        face,
        ratio_type
    )

    if crop is None:
        return None

    x1, y1, x2, y2 = crop

    cropped = image[
        y1:y2,
        x1:x2
    ]

    output_size = (
        (600, 690)
        if ratio_type == "standard"
        else (600, 600)
    )

    final = cv2.resize(
        cropped,
        output_size,
        interpolation=cv2.INTER_CUBIC
    )

    _, buffer = cv2.imencode(
        ".jpg",
        final,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            95
        ]
    )

    return buffer.tobytes()


def create_zip(images):

    memory = io.BytesIO()

    with zipfile.ZipFile(
        memory,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zf:

        for name, data in images.items():

            zf.writestr(
                name,
                data
            )

    memory.seek(0)

    return memory