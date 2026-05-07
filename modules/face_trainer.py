import cv2
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def train_model():
    data_path = os.path.join(BASE_DIR, "data", "faces")

    faces = []
    labels = []
    label_map = {}

    current_id = 0

    for person in os.listdir(data_path):
        person_path = os.path.join(data_path, person)

        if not os.path.isdir(person_path):
            continue

        label_map[current_id] = person

        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)

            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            if img is None:
                continue

            faces.append(img)
            labels.append(current_id)

        current_id += 1

    # LBPH model
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))

    # save model
    model_path = os.path.join(BASE_DIR, "data", "classifier.xml")
    recognizer.save(model_path)

    # save label map
    np.save(os.path.join(BASE_DIR, "data", "labels.npy"), label_map)

    print("Training Complete ")