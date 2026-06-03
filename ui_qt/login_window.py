import sys
import os
import database

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from database import check_login_with_role, is_waiting_for_approval
from ui_qt.driver_dashboard import DriverDashboard
from modules.otp_manager import send_otp
from ui_qt.otp_window import OTPWindow


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CDMS Login")
        self.resize(1100, 650)
        self.setMinimumSize(950, 560)

        self.setStyleSheet("""
            QWidget {
                background-color: #050b1a;
                color: white;
                font-family: Segoe UI;
            }

            QFrame#mainCard {
                background-color: #071426;
                border: 1px solid #1683ff;
                border-radius: 22px;
            }

            QFrame#rightPanel {
                background-color: #071426;
                border-top-right-radius: 22px;
                border-bottom-right-radius: 22px;
            }

            QLabel {
                background: transparent;
            }

            QLabel#loginIcon {
                background-color: #0b1d3a;
                border: 1px solid #1f70c1;
                border-radius: 14px;
                font-size: 32px;
            }

            QLabel#title {
                font-size: 28px;
                font-weight: 900;
                color: white;
            }

            QLabel#titleBlue {
                font-size: 28px;
                font-weight: 900;
                color: #18a0ff;
            }

            QLabel#subtitle {
                color: #9aa7bd;
                font-size: 13px;
            }

            QLineEdit {
                background-color: #081226;
                border: 1px solid #1f70c1;
                border-radius: 10px;
                padding: 13px 15px;
                color: white;
                font-size: 13px;
            }

            QLineEdit:focus {
                border: 1px solid #18a0ff;
            }

            QCheckBox {
                color: white;
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

            QPushButton#forgotBtn {
                color: #18a0ff;
                background: transparent;
                border: none;
                font-size: 12px;
                text-align: right;
            }

            QPushButton#forgotBtn:hover {
                color: white;
            }

            QPushButton#loginBtn {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton#loginBtn:hover {
                background-color: #075ee6;
            }

            QLabel#footer {
                color: #7f8ca6;
                font-size: 12px;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(45, 35, 45, 35)

        main_card = QFrame()
        main_card.setObjectName("mainCard")

        main = QHBoxLayout(main_card)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # LEFT IMAGE PANEL
        left_img = QLabel()
        left_img.setAlignment(Qt.AlignCenter)
        left_img.setMinimumWidth(540)
        left_img.setMaximumWidth(620)

        img_path = os.path.join(ASSETS_DIR, "login_left.png")

        if os.path.exists(img_path):
            pix = QPixmap(img_path)
            left_img.setPixmap(pix)
            left_img.setScaledContents(True)
        else:
            left_img.setText("CDMS Login Visual")
            left_img.setStyleSheet("color:#18a0ff;font-size:22px;")

        # RIGHT LOGIN PANEL
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")

        right = QVBoxLayout(right_panel)
        right.setContentsMargins(55, 55, 55, 45)
        right.setSpacing(16)

        title_row = QHBoxLayout()

        login_icon = QLabel("👤")
        login_icon.setObjectName("loginIcon")
        login_icon.setAlignment(Qt.AlignCenter)
        login_icon.setFixedSize(58, 58)

        title_box = QVBoxLayout()
        title_line = QHBoxLayout()

        title = QLabel("Driver")
        title.setObjectName("title")

        title_blue = QLabel("Login")
        title_blue.setObjectName("titleBlue")

        title_line.addWidget(title)
        title_line.addWidget(title_blue)
        title_line.addStretch()

        subtitle = QLabel("Enter username and password to access your account")
        subtitle.setObjectName("subtitle")

        title_box.addLayout(title_line)
        title_box.addWidget(subtitle)

        title_row.addWidget(login_icon)
        title_row.addSpacing(14)
        title_row.addLayout(title_box)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setFixedHeight(50)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(50)

        option_row = QHBoxLayout()

        remember = QCheckBox("Remember me")

        forgot = QPushButton("Forgot Password?")
        forgot.setObjectName("forgotBtn")
        forgot.setCursor(Qt.PointingHandCursor)
        forgot.setFlat(True)
        forgot.clicked.connect(self.open_forgot_password)

        option_row.addWidget(remember)
        option_row.addStretch()
        option_row.addWidget(forgot)

        login_btn = QPushButton("LOGIN")
        login_btn.setObjectName("loginBtn")
        login_btn.setFixedHeight(52)

        footer = QLabel("🛡  Secure • Reliable • Safe Driving")
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignCenter)

        right.addStretch()
        right.addLayout(title_row)
        right.addSpacing(22)
        right.addWidget(self.username)
        right.addWidget(self.password)
        right.addLayout(option_row)
        right.addSpacing(12)
        right.addWidget(login_btn)
        right.addStretch()
        right.addWidget(footer)

        main.addWidget(left_img, 1)
        main.addWidget(right_panel, 1)

        outer.addWidget(main_card)

        login_btn.clicked.connect(self.login_action)

    def login_action(self):
        from PySide6.QtWidgets import QMessageBox

        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter username and password")
            return

        result = check_login_with_role(username, password)

        if result:
            driver_id, driver_name, driver_email, role = result

            # ================= ADMIN LOGIN =================
            if role == "admin":
                from ui_qt.admin_dashboard import AdminDashboard

                for widget in QApplication.topLevelWidgets():
                    if widget.__class__.__name__ == "HomeWindow":
                        widget.hide()

                self.admin_dashboard = AdminDashboard()
                self.admin_dashboard.showMaximized()

                self.close()
                return

            # ================= DRIVER LOGIN WITH OTP =================
            if not driver_email:
                QMessageBox.warning(self, "2FA Error", "No email found for this driver.")
                return

            print("OTP SEND STARTED:", driver_email)

            otp_sent = send_otp(driver_email)

            print("OTP SENT RESULT:", otp_sent)

            if not otp_sent:
                QMessageBox.critical(self, "OTP Error", "Failed to send OTP. Check Brevo API.")
                return

            self.otp_window = OTPWindow(driver_id, driver_name, driver_email)
            self.otp_window.showMaximized()

            self.hide()

        else:
            if is_waiting_for_approval(username):
                QMessageBox.information(
                    self,
                    "Approval Required",
                    "Your account has been registered successfully, but it is waiting for Admin approval."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Login Failed",
                    "Incorrect username or password"
                )

    def open_forgot_password(self):
        from ui_qt.forgot_password_window import ForgotPasswordWindow
        self.forgot_window = ForgotPasswordWindow()
        self.forgot_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.showMaximized()
    sys.exit(app.exec())
