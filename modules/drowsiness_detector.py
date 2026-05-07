import os
import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist

from config import EAR_THRESHOLD, DROWSY_FRAMES


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LANDMARK_PATH = os.path.join(
    BASE_DIR,
    "models",
    "shape_predictor_68_face_landmarks.dat"
)

if not os.path.exists(LANDMARK_PATH):
    raise FileNotFoundError(f"Model not found: {LANDMARK_PATH}")


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(LANDMARK_PATH)


def eye_aspect_ratio(eye):
    a = dist.euclidean(eye[1], eye[5])
    b = dist.euclidean(eye[2], eye[4])
    c = dist.euclidean(eye[0], eye[3])

    if c == 0:
        return 0.0

    return (a + b) / (2.0 * c)


def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)

    for i in range(68):
        coords[i] = (shape.part(i).x, shape.part(i).y)

    return coords


def process_frame(frame, closed_counter):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    status = "NO FACE"
    ear_value = 0.0

    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        shape = predictor(gray, face)
        shape = shape_to_np(shape)

        left_eye = shape[42:48]
        right_eye = shape[36:42]

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear_value = (left_ear + right_ear) / 2.0

        cv2.polylines(frame, [left_eye], True, (255, 0, 0), 1)
        cv2.polylines(frame, [right_eye], True, (255, 0, 0), 1)

        if ear_value < EAR_THRESHOLD:
            closed_counter += 1
        else:
            closed_counter = 0

        if closed_counter >= DROWSY_FRAMES:
            status = "DROWSY"
            color = (0, 0, 255)
        else:
            status = "AWAKE"
            color = (0, 255, 0)

        cv2.putText(
            frame,
            f"Status: {status}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

        cv2.putText(
            frame,
            f"EAR: {ear_value:.2f}",
            (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

        break

    if len(faces) == 0:
        closed_counter = 0
        status = "NO FACE"

        cv2.putText(
            frame,
            "Status: NO FACE",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    return frame, status, ear_value, closed_counter


def detect_drowsiness(frame, counter):
    return process_frame(frame, counter)