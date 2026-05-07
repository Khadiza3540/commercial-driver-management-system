import cv2
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def recognize_face():
    face_cascade = cv2.CascadeClassifier(
        os.path.join(BASE_DIR, "models", "haarcascade_frontalface_default.xml")
    )

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(os.path.join(BASE_DIR, "data", "classifier.xml"))

    labels = np.load(os.path.join(BASE_DIR, "data", "labels.npy"), allow_pickle=True).item()

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (200, 200))

            label_id, confidence = recognizer.predict(face_img)
            if confidence < 35:
                name = labels[label_id].split("_")[1]
                authorized = True
            else:
                name = "Unknown"
                authorized = False

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.putText(
                frame,
                name,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()