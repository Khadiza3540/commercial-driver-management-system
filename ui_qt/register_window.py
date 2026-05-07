import sys
import os
import re
import cv2
import numpy as np
from PIL import Image



from database import create_tables, register_driver, authorize_driver

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QLineEdit, QTextEdit, QCheckBox, QFrame, QMessageBox
)
from PySide6.QtCore import Qt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE_DIR = os.path.join(BASE_DIR, "data", "faces")
CLASSIFIER_PATH = os.path.join(BASE_DIR, "data", "classifier.xml")


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()

        create_tables()

        self.setWindowTitle("CDMS - Driver Registration")
        self.resize(1200, 700)
        self.setMinimumSize(1000, 650)

        self.setStyleSheet("""
            QWidget {
                background-color: #050b1a;
                color: white;
                font-family: Segoe UI;
            }

            QFrame#card {
                background-color: #071426;
                border: 1px solid #1683ff;
                border-radius: 18px;
            }

            QLabel {
                background: transparent;
            }

            QLabel#title {
                font-size: 30px;
                font-weight: 900;
                color: white;
            }

            QLabel#blue {
                font-size: 30px;
                font-weight: 900;
                color: #18a0ff;
            }

            QLabel#subtitle {
                color: #b8c1cc;
                font-size: 14px;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: bold;
                color: white;
            }

            QLabel#label {
                color: white;
                font-size: 12px;
                font-weight: bold;
            }

            QLabel#error {
                color: #ef4444;
                font-size: 10px;
            }

            QLineEdit, QTextEdit {
                background-color: #081226;
                border: 1px solid #1f70c1;
                border-radius: 9px;
                padding: 10px 12px;
                color: white;
                font-size: 12px;
            }

            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #18a0ff;
            }

            QPushButton#primaryBtn {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton#primaryBtn:hover {
                background-color: #075ee6;
            }

            QCheckBox {
                color: #cbd5e1;
                font-size: 12px;
            }

            QCheckBox::indicator {
                width: 17px;
                height: 17px;
                border-radius: 4px;
                border: 1px solid #1f70c1;
                background: transparent;
            }

            QCheckBox::indicator:checked {
                background-color: #0d6efd;
                border: 1px solid #18a0ff;
            }
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(25, 20, 25, 20)
        main.setSpacing(12)

        # Header
        header = QVBoxLayout()
        title_row = QHBoxLayout()
        title1 = QLabel("Driver")
        title1.setObjectName("title")
        title2 = QLabel("Registration")
        title2.setObjectName("blue")
        title_row.addStretch()
        title_row.addWidget(title1)
        title_row.addSpacing(8)
        title_row.addWidget(title2)
        title_row.addStretch()

        subtitle = QLabel("Register new driver and capture face for verification")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        header.addLayout(title_row)
        header.addWidget(subtitle)
        main.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(18)

        # Left form card
        form_card = QFrame()
        form_card.setObjectName("card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(10)

        section_title = QLabel("👤  Driver Information")
        section_title.setObjectName("sectionTitle")
        form_layout.addWidget(section_title)

        grid1 = QHBoxLayout()
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()

        self.entries = {}
        self.errors = {}

        def add_input(parent, key, label, placeholder, password=False):
            lbl = QLabel(label)
            lbl.setObjectName("label")

            entry = QLineEdit()
            entry.setPlaceholderText(placeholder)
            entry.setFixedHeight(42)

            if password:
                entry.setEchoMode(QLineEdit.Password)

            err = QLabel("")
            err.setObjectName("error")

            parent.addWidget(lbl)
            parent.addWidget(entry)
            parent.addWidget(err)

            self.entries[key] = entry
            self.errors[key] = err

            entry.textChanged.connect(lambda: self.validate_single(key, silent=True))

        add_input(left_col, "name", "Full Name", "Enter full name")
        add_input(right_col, "license", "License Number", "Enter license number")

        add_input(left_col, "username", "Username", "Enter username")
        add_input(right_col, "email", "Email Address", "Enter email address")

        add_input(left_col, "phone", "Phone Number", "01712345678")
        add_input(right_col, "dob", "Date of Birth", "YYYY-MM-DD")

        add_input(left_col, "vehicle_no", "Vehicle Number", "DHK-1234")
        add_input(right_col, "license", "License Number", "Enter license number")

        add_input(left_col, "password", "Password", "Enter password", password=True)
        add_input(right_col, "confirm_password", "Confirm Password", "Confirm password", password=True)

        address_lbl = QLabel("Address")
        address_lbl.setObjectName("label")

        self.address = QTextEdit()
        self.address.setPlaceholderText("Enter address")
        self.address.setFixedHeight(50)

        self.address_error = QLabel("")
        self.address_error.setObjectName("error")

        left_col.addWidget(address_lbl)
        left_col.addWidget(self.address)
        left_col.addWidget(self.address_error)
        left_col.addSpacing(8)

        grid1.addLayout(left_col)
        grid1.addSpacing(15)
        grid1.addLayout(right_col)

        form_layout.addLayout(grid1)

        form_layout.addSpacing(8)

        self.terms = QCheckBox("I agree to the Terms & Conditions")
        self.terms.setStyleSheet("""
            QCheckBox {
                background: transparent;
                color: #cbd5e1;
                font-size: 12px;
                padding: 4px;
            }
        """)
        form_layout.addWidget(self.terms)

        self.general_error = QLabel("")
        self.general_error.setObjectName("error")
        form_layout.addWidget(self.general_error)

        submit_btn = QPushButton("NEXT: CAPTURE FACE  →")
        submit_btn.setObjectName("primaryBtn")
        submit_btn.setFixedHeight(55)
        submit_btn.clicked.connect(self.submit_register)
        form_layout.addWidget(submit_btn)

        # Right preview card
        preview_card = QFrame()
        preview_card.setObjectName("card")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(25, 25, 25, 25)
        preview_layout.setSpacing(12)

        preview_title = QLabel("📷  Face Capture Preview")
        preview_title.setObjectName("sectionTitle")

        preview_sub = QLabel("Position your face in the camera frame")
        preview_sub.setObjectName("subtitle")

        face_box = QLabel("👤")
        face_box.setAlignment(Qt.AlignCenter)
        face_box.setFixedHeight(260)
        face_box.setStyleSheet("""
            QLabel {
                background-color: #081226;
                border: 1px solid #1f70c1;
                border-radius: 12px;
                font-size: 90px;
                color: #1f70c1;
            }
        """)

        self.capture_status = QLabel("● Camera Ready                           Images Captured: 0 / 300")
        self.capture_status.setStyleSheet("color:#22c55e;font-size:12px;")

        instructions = QLabel(
            "ⓘ  Instructions\n\n"
            "• Look straight at the camera\n"
            "• Ensure good lighting on your face\n"
            "• Capture 300 images for best results\n"
            "• Remove glasses, hat or mask\n"
            "• Keep a neutral facial expression"
        )
        instructions.setStyleSheet("""
            QLabel {
                background-color: #081226;
                border: 1px solid #1f70c1;
                border-radius: 12px;
                padding: 14px;
                color: #cbd5e1;
                font-size: 12px;
            }
        """)
        instructions.setWordWrap(True)

        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(preview_sub)
        preview_layout.addWidget(face_box)
        preview_layout.addWidget(self.capture_status)
        preview_layout.addWidget(instructions)
        preview_layout.addStretch()

        body.addWidget(form_card, 1)
        body.addWidget(preview_card, 1)

        main.addLayout(body)

    def mark_error(self, key, message):
        self.entries[key].setStyleSheet("""
            QLineEdit {
                background-color: #081226;
                border: 1px solid #ef4444;
                border-radius: 9px;
                padding: 10px 12px;
                color: white;
                font-size: 12px;
            }
        """)
        self.errors[key].setText(message)
        return False

    def clear_error(self, key):
        self.entries[key].setStyleSheet("")
        self.errors[key].setText("")

    def validate_single(self, key, silent=False):
        value = self.entries[key].text().strip()

        if key == "name":
            if len(value) < 3:
                return self.mark_error(key, "Minimum 3 characters")
        elif key == "username":
            if not re.match(r"^[A-Za-z0-9_]{4,20}$", value):
                return self.mark_error(key, "4-20 chars: letters, numbers, underscore")
        elif key == "email":
            if not re.match(r"^[\\w\\.-]+@[\\w\\.-]+\\.\\w{2,}$", value):
                return self.mark_error(key, "Enter valid email address")
        elif key == "license":
            if not re.match(r"^[A-Za-z0-9-]{5,20}$", value):
                return self.mark_error(key, "5-20 chars: letters, numbers, hyphen")
        elif key == "dob":
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                return self.mark_error(key, "Format: YYYY-MM-DD")
        elif key == "phone":
            if not re.match(r"^01[3-9]\d{8}$", value):
                return self.mark_error(key, "Use BD format: 01712345678")
        elif key == "vehicle_no":
            if not re.match(r"^[A-Za-z0-9-]{3,20}$", value):
                return self.mark_error(key, "3-20 chars: letters, numbers, hyphen")
        elif key == "password":
            if len(value) < 6:
                return self.mark_error(key, "Minimum 6 characters")
        elif key == "confirm_password":
            if value != self.entries["password"].text().strip():
                return self.mark_error(key, "Password does not match")

        self.clear_error(key)
        return True

    def validate_all(self):
        valid = True

        for key in self.entries:
            if not self.validate_single(key):
                valid = False

        if len(self.address.toPlainText().strip()) < 5:
            self.address.setStyleSheet("""
                QTextEdit {
                    background-color: #081226;
                    border: 1px solid #ef4444;
                    border-radius: 9px;
                    padding: 10px 12px;
                    color: white;
                    font-size: 12px;
                }
            """)
            self.address_error.setText("Address minimum 5 characters")
            valid = False
        else:
            self.address.setStyleSheet("")
            self.address_error.setText("")

        if not self.terms.isChecked():
            self.general_error.setText("You must agree to Terms & Conditions")
            valid = False
        else:
            self.general_error.setText("")

        return valid

    def submit_register(self):
        if not self.validate_all():
            return

        name = self.entries["name"].text().strip()
        username = self.entries["username"].text().strip()
        password = self.entries["password"].text().strip()
        email = self.entries["email"].text().strip()
        license_no = self.entries["license"].text().strip()
        phone = self.entries["phone"].text().strip()
        address = self.address.toPlainText().strip()
        vehicle_no = self.entries["vehicle_no"].text().strip()
        dob = self.entries["dob"].text().strip()

        try:
            driver_id = register_driver(
                name,
                username,
                password,
                email,
                license_no,
                phone,
                address,
                vehicle_no,
                dob
            )

            QMessageBox.information(
                self,
                "Face Capture",
                "Camera will open now.\nPlease look at the camera until 300 images are captured."
            )

            success = self.capture_faces(driver_id, name)

            if not success:
                QMessageBox.warning(self, "Warning", "Face capture incomplete.")
                return

            trained = self.train_face_model()

            if not trained:
                QMessageBox.critical(self, "Error", "Face model training failed.")
                return

            authorize_driver(driver_id)

            QMessageBox.information(self, "Success", "Driver registered successfully ✅")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def capture_faces(self, driver_id, name):
        os.makedirs(FACE_DIR, exist_ok=True)

        safe_name = name.replace(" ", "_")
        driver_folder = os.path.join(FACE_DIR, f"{driver_id}_{safe_name}")
        os.makedirs(driver_folder, exist_ok=True)

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        cap = cv2.VideoCapture(0)
        count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                count += 1

                face_img = gray[y:y + h, x:x + w]
                face_img = cv2.resize(face_img, (200, 200))

                save_path = os.path.join(driver_folder, f"{count}.jpg")
                cv2.imwrite(save_path, face_img)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"Capturing: {count}/300",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

                self.capture_status.setText(f"● Camera Ready                           Images Captured: {count} / 300")

                if count >= 300:
                    break

            cv2.imshow("Face Capture", frame)

            if cv2.waitKey(1) == 13 or count >= 300:
                break

        cap.release()
        cv2.destroyAllWindows()

        return count >= 300

    def train_face_model(self):
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        faces = []
        ids = []
        labels = {}

        if not os.path.exists(FACE_DIR):
            return False

        for folder_name in os.listdir(FACE_DIR):
            folder_path = os.path.join(FACE_DIR, folder_name)

            if not os.path.isdir(folder_path):
                continue

            try:
                driver_id = int(folder_name.split("_")[0])
            except ValueError:
                continue

            labels[driver_id] = folder_name

            for image_name in os.listdir(folder_path):
                image_path = os.path.join(folder_path, image_name)

                try:
                    img = Image.open(image_path).convert("L")
                    img_np = np.array(img, "uint8")

                    faces.append(img_np)
                    ids.append(driver_id)
                except Exception:
                    continue

        if len(faces) > 0:
            recognizer.train(faces, np.array(ids))
            recognizer.save(CLASSIFIER_PATH)

            labels_path = os.path.join(BASE_DIR, "data", "labels.npy")
            np.save(labels_path, labels)

            return True

        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RegisterWindow()
    win.showMaximized()
    sys.exit(app.exec())