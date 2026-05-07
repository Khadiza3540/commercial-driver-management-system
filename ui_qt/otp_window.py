from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QMessageBox, QFrame
)
from PySide6.QtCore import Qt

from modules.otp_manager import verify_otp
from ui_qt.driver_dashboard import DriverDashboard


class OTPWindow(QWidget):
    def __init__(self, driver_id, driver_name, driver_email):
        super().__init__()

        self.driver_id = driver_id
        self.driver_name = driver_name
        self.driver_email = driver_email

        self.setWindowTitle("CDMS - OTP Verification")
        self.resize(520, 420)

        self.setStyleSheet("""
            QWidget {
                background-color:#050b1a;
                color:white;
                font-family:Segoe UI;
            }
            QFrame {
                background-color:#071426;
                border:1px solid #1683ff;
                border-radius:18px;
            }
            QLabel {
                background:transparent;
            }
            QLineEdit {
                background-color:#081226;
                border:1px solid #1f70c1;
                border-radius:10px;
                padding:12px;
                color:white;
                font-size:16px;
            }
            QPushButton {
                background-color:#0d6efd;
                color:white;
                border:none;
                border-radius:10px;
                padding:13px;
                font-weight:bold;
                font-size:14px;
            }
            QPushButton:hover {
                background-color:#075ee6;
            }
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(40, 40, 40, 40)

        card = QFrame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(18)

        title = QLabel("🔐 OTP Verification")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:26px;font-weight:900;color:white;")

        msg = QLabel(f"6-digit OTP has been sent to:\n{self.driver_email}")
        msg.setAlignment(Qt.AlignCenter)
        msg.setStyleSheet("color:#9aa7bd;font-size:14px;")

        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Enter 6-digit OTP")
        self.otp_input.setMaxLength(6)
        self.otp_input.setAlignment(Qt.AlignCenter)

        verify_btn = QPushButton("VERIFY OTP")
        verify_btn.clicked.connect(self.verify_action)

        layout.addWidget(title)
        layout.addWidget(msg)
        layout.addWidget(self.otp_input)
        layout.addWidget(verify_btn)

        main.addWidget(card)

    def verify_action(self):
        otp = self.otp_input.text().strip()

        if not otp:
            QMessageBox.warning(self, "OTP Error", "Please enter OTP.")
            return

        if verify_otp(self.driver_email, otp):
            self.dashboard = DriverDashboard(self.driver_name, self.driver_id)
            self.dashboard.showMaximized()
            self.close()
        else:
            QMessageBox.critical(self, "OTP Failed", "Invalid OTP. Please try again.")