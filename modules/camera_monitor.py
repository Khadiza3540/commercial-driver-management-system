import os
import cv2
import numpy as np

from modules.drowsiness_detector import process_frame
from modules.alert_manager import play_alarm, stop_alarm
from database import start_session, end_session, add_alert


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FACE_CASCADE_PATH = os.path.join(BASE_DIR, "models", "haarcascade_frontalface_default.xml")
CLASSIFIER_PATH = os.path.join(BASE_DIR, "data", "classifier.xml")
LABELS_PATH = os.path.join(BASE_DIR, "data", "labels.npy")


def run_monitoring():
    if not os.path.exists(FACE_CASCADE_PATH):
        print("Face cascade not found:", FACE_CASCADE_PATH)
        return

    if not os.path.exists(CLASSIFIER_PATH):
        print("Face classifier not found. Please register driver first.")
        return

    if not os.path.exists(LABELS_PATH):
        print("Labels file not found:", LABELS_PATH)
        return

    face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(CLASSIFIER_PATH)

    labels = np.load(LABELS_PATH, allow_pickle=True).item()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not opened")
        return

    closed_counter = 0
    alarm_on = False

    session_id = None
    session_started = False
    alert_saved = False

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        authorized = False
        driver_name = "Unknown"
        driver_id = None

        for (x, y, w, h) in faces:
            face_img = gray[y:y + h, x:x + w]
            face_img = cv2.resize(face_img, (200, 200))

            label_id, confidence = recognizer.predict(face_img)

            if confidence < 45 and label_id in labels:
                raw_name = labels[label_id]
                parts = raw_name.split("_")

                try:
                    driver_id = int(parts[0])
                    driver_name = parts[1] if len(parts) > 1 else "Driver"
                    authorized = True
                    color = (0, 255, 0)
                except ValueError:
                    authorized = False
                    color = (0, 0, 255)
            else:
                authorized = False
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                frame,
                driver_name if authorized else "Unknown",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                2
            )

            break

        if authorized:
            if not session_started:
                try:
                    session_id = start_session(driver_id, driver_name)
                    session_started = True
                except Exception as e:
                    print("Session start error:", e)

            frame, status, ear, closed_counter = process_frame(frame, closed_counter)

            status_color = (0, 0, 255) if status == "DROWSY" else (0, 255, 0)

            cv2.putText(
                frame,
                f"Driver: {driver_name}",
                (30, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Status: {status}",
                (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                status_color,
                2
            )

            cv2.putText(
                frame,
                f"EAR: {ear:.2f}",
                (30, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                status_color,
                2
            )

            if status == "DROWSY":
                if not alarm_on:
                    play_alarm()
                    alarm_on = True

                if not alert_saved and session_id is not None:
                    try:
                        add_alert(session_id, driver_id, driver_name)
                        alert_saved = True
                    except Exception as e:
                        print("Alert save error:", e)
            else:
                if alarm_on:
                    stop_alarm()
                    alarm_on = False

                alert_saved = False

        else:
            closed_counter = 0

            if alarm_on:
                stop_alarm()
                alarm_on = False

            cv2.putText(
                frame,
                "Unauthorized Person",
                (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        cv2.imshow("Monitoring System", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    if alarm_on:
        stop_alarm()

    if session_id is not None:
        try:
            end_session(session_id)
        except Exception as e:
            print("Session end error:", e)

    cap.release()
    cv2.destroyAllWindows()


def start_camera():
    run_monitoring()