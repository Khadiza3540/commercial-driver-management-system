import sys
import os
import cv2

#  database import
from database import get_driver_by_license, reset_password_by_driver_id

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QLineEdit, QFrame, QMessageBox
)
from PySide6.QtCore import Qt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASSIFIER_PATH = os.path.join(BASE_DIR, "data", "classifier.xml")


def verify_face(target_driver_id):
    if not os.path.exists(CLASSIFIER_PATH):
        QMessageBox.critical(None, "Error", "Face model not found. Please register driver first.")
        return False

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(CLASSIFIER_PATH)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cap = cv2.VideoCapture(0)
    match_count = 0
    wrong_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            match_count = 0

        for (x, y, w, h) in faces:
            face_img = gray[y:y + h, x:x + w]
            face_img = cv2.resize(face_img, (200, 200))

            predicted_id, confidence = recognizer.predict(face_img)

            if predicted_id == target_driver_id and confidence < 45:
                match_count += 1
                wrong_count = 0
                text = f"Verified {match_count}/20"
                color = (0, 255, 0)
            else:
                wrong_count += 1
                match_count = 0
                text = f"Wrong Person ({int(confidence)})"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.putText(frame, "Press Q to cancel", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow("Real Time Face Confirmation", frame)

        if match_count >= 20:
            cap.release()
            cv2.destroyAllWindows()
            return True

        if wrong_count >= 20:
            cap.release()
            cv2.destroyAllWindows()
            return False

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False


class ForgotPasswordWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.verified_driver_id = 0

        self.setWindowTitle("CDMS - Forgot Password")
        self.resize(620, 520)
        self.setMinimumSize(560, 460)

        self.setStyleSheet("""
            QWidget {
                background-color: #050b1a;
                color: white;
                font-family: Segoe UI;
            }

            QFrame#card {
                background-color: #071426;
                border: 1px solid #1683ff;
                border-radius: 20px;
            }

            QLabel {
                background: transparent;
            }

            QLabel#title {
                font-size: 28px;
                font-weight: 900;
                color: white;
            }

            QLabel#blue {
                font-size: 28px;
                font-weight: 900;
                color: #18a0ff;
            }

            QLabel#subtitle {
                color: #9aa7bd;
                font-size: 13px;
            }

            QLabel#status {
                color: #9aa7bd;
                font-size: 12px;
            }

            QLineEdit {
                background-color: #081226;
                border: 1px solid #1f70c1;
                border-radius: 10px;
                padding: 12px 14px;
                color: white;
                font-size: 13px;
            }

            QLineEdit:focus {
                border: 1px solid #18a0ff;
            }

            QPushButton#primaryBtn {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 13px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton#primaryBtn:hover {
                background-color: #075ee6;
            }

            QPushButton#successBtn {
                background-color: #22c55e;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 13px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton#successBtn:hover {
                background-color: #16a34a;
            }
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(40, 30, 40, 30)

        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 35, 40, 35)
        layout.setSpacing(14)

        title_row = QHBoxLayout()
        title1 = QLabel("Forgot")
        title1.setObjectName("title")
        title2 = QLabel("Password")
        title2.setObjectName("blue")
        title_row.addWidget(title1)
        title_row.addWidget(title2)
        title_row.addStretch()

        subtitle = QLabel("Verify your license and face before resetting password")
        subtitle.setObjectName("subtitle")

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("License Number")
        self.license_input.setFixedHeight(48)

        self.status_label = QLabel("Enter license number, then verify face")
        self.status_label.setObjectName("status")

        verify_btn = QPushButton("VERIFY FACE")
        verify_btn.setObjectName("primaryBtn")
        verify_btn.setFixedHeight(48)
        verify_btn.clicked.connect(self.face_confirm_action)

        self.password_frame = QFrame()
        self.password_frame.setStyleSheet("background: transparent; border: none;")

        pass_layout = QVBoxLayout(self.password_frame)
        pass_layout.setContentsMargins(0, 12, 0, 0)
        pass_layout.setSpacing(12)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("New Password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setFixedHeight(48)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setFixedHeight(48)

        reset_btn = QPushButton("RESET PASSWORD")
        reset_btn.setObjectName("successBtn")
        reset_btn.setFixedHeight(48)
        reset_btn.clicked.connect(self.reset_action)

        pass_layout.addWidget(self.new_password_input)
        pass_layout.addWidget(self.confirm_password_input)
        pass_layout.addWidget(reset_btn)

        self.password_frame.hide()

        footer = QLabel("🛡  License + Face Verification Required")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color:#7f8ca6;font-size:12px;")

        layout.addLayout(title_row)
        layout.addWidget(subtitle)
        layout.addSpacing(12)
        layout.addWidget(self.license_input)
        layout.addWidget(self.status_label)
        layout.addWidget(verify_btn)
        layout.addWidget(self.password_frame)
        layout.addStretch()
        layout.addWidget(footer)

        main.addWidget(card)

    def face_confirm_action(self):
        self.verified_driver_id = 0
        self.password_frame.hide()

        license_no = self.license_input.text().strip()

        if not license_no:
            QMessageBox.warning(self, "Error", "Please enter license number")
            return

        driver = get_driver_by_license(license_no)

        if not driver:
            QMessageBox.critical(self, "Error", "Driver not found or not authorized")
            return

        driver_id, driver_name = driver

        QMessageBox.information(
            self,
            "Face Confirmation",
            f"Camera will open for {driver_name}.\nPlease look at the camera."
        )

        success = verify_face(driver_id)

        if success:
            self.verified_driver_id = driver_id
            self.status_label.setText("Face verification successful ✅ Now set new password")
            self.status_label.setStyleSheet("color:#22c55e;font-size:12px;")
            self.password_frame.show()
            QMessageBox.information(self, "Success", "Face verified successfully ✅")
        else:
            self.verified_driver_id = 0
            self.status_label.setText("Face verification failed ❌")
            self.status_label.setStyleSheet("color:#ef4444;font-size:12px;")
            QMessageBox.critical(self, "Error", "Face verification failed")

    def reset_action(self):
        if self.verified_driver_id == 0:
            QMessageBox.warning(self, "Error", "Please verify face first")
            return

        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        if not new_password or not confirm_password:
            QMessageBox.warning(self, "Error", "Password fields required")
            return

        if len(new_password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        reset_password_by_driver_id(self.verified_driver_id, new_password)
        QMessageBox.information(self, "Success", "Password reset successful ✅")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ForgotPasswordWindow()
    win.show()
    sys.exit(app.exec())