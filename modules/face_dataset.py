import cv2
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def capture_driver_faces(driver_id, driver_name):
    face_cascade_path = os.path.join(BASE_DIR, "models", "haarcascade_frontalface_default.xml")
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    faces_dir = os.path.join(BASE_DIR, "data", "faces")

    # যদি faces নামে ভুল করে file থাকে, error দেখাবে
    if os.path.exists(faces_dir) and not os.path.isdir(faces_dir):
        raise Exception("data/faces is a file, not a folder. Delete it and create folder named faces.")

    os.makedirs(faces_dir, exist_ok=True)

    save_path = os.path.join(faces_dir, f"{driver_id}_{driver_name}")
    os.makedirs(save_path, exist_ok=True)

    print("Saving images to:", save_path)

    cap = cv2.VideoCapture(0)
    count = 0
    last_capture_time = 0
    capture_delay = 0.3

    if not cap.isOpened():
        print("Camera could not be opened")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame read failed")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        current_time = time.time()

        for (x, y, w, h) in faces:
            if current_time - last_capture_time >= capture_delay:
                count += 1

                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))

                file_path = os.path.join(save_path, f"{count}.jpg")
                cv2.imwrite(file_path, face_img)

                print("Saved:", file_path)
                last_capture_time = current_time

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.putText(frame, f"Capturing: {count}/300", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Capture Driver Face Dataset", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if count >= 300:
            print("300 images captured successfully")
            break

    cap.release()
    cv2.destroyAllWindows()