from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFrame, QPushButton,
    QLineEdit, QMessageBox, QComboBox, QCheckBox, QGridLayout
)
from PySide6.QtCore import Qt

from database import reset_password_by_driver_id


class SettingsPage(QWidget):
    def __init__(self, driver_id, dashboard=None):
        super().__init__()
        self.driver_id = driver_id
        self.dashboard = dashboard

        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(45, 25, 45, 25)
        self.main.setSpacing(18)

        self.load_home()

    def clear_page(self):
        while self.main.count():
            item = self.main.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def load_home(self):
        self.clear_page()

        hero = QFrame()
        hero.setFixedHeight(135)
        hero.setStyleSheet("""
            QFrame {
                background:#081226;
                border:1px solid #1f70c1;
                border-radius:22px;
            }
        """)

        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("⚙️ Driver Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:30px;font-weight:900;color:white;border:none;background:transparent;")

        subtitle = QLabel("Manage driver account, monitoring, alerts, and system preferences.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color:#9aa7bd;font-size:14px;border:none;background:transparent;")

        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)

        self.main.addWidget(hero)

        section_title = QLabel("Settings options")
        section_title.setStyleSheet("color:white;font-size:20px;font-weight:bold;")
        self.main.addWidget(section_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(22)
        grid.setVerticalSpacing(22)

        grid.addWidget(self.setting_card(
            "👤", "Profile Settings",
            "Go to profile page to update driver information, photo, license, and vehicle data.",
            self.open_profile_settings
        ), 0, 0)

        grid.addWidget(self.setting_card(
            "🔐", "Change Password",
            "Update your login password securely using a new password and confirmation.",
            self.open_change_password
        ), 0, 1)

        grid.addWidget(self.setting_card(
            "🔊", "Alarm Sound Settings",
            "Enable or disable drowsiness alarm sound during live monitoring.",
            self.open_alarm_settings
        ), 0, 2)

        grid.addWidget(self.setting_card(
            "👁️", "Drowsiness Sensitivity",
            "Choose low, medium, or high detection sensitivity for drowsiness alerts.",
            self.open_sensitivity_settings
        ), 1, 0)

        grid.addWidget(self.setting_card(
            "🔔", "Alert Notifications",
            "Control alert notification visibility and warning messages.",
            self.open_notification_settings
        ), 1, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        self.main.addLayout(grid)
        self.main.addStretch()

    def setting_card(self, icon, title_text, body_text, action):
        card = QFrame()
        card.setMinimumHeight(190)
        card.setStyleSheet("""
            QFrame {
                background:#081226;
                border:1px solid #1f70c1;
                border-radius:18px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size:30px;border:none;background:transparent;")

        heading = QLabel(title_text)
        heading.setStyleSheet("color:white;font-size:17px;font-weight:bold;border:none;background:transparent;")

        body = QLabel(body_text)
        body.setWordWrap(True)
        body.setStyleSheet("color:#9aa7bd;font-size:13px;border:none;background:transparent;")

        btn = QPushButton("Open →")
        btn.clicked.connect(action)
        btn.setFixedHeight(28)
        btn.setStyleSheet("""
            QPushButton {
                background:transparent;
                color:#18a0ff;
                border:none;
                text-align:left;
                font-size:12px;
                font-weight:bold;
                padding-left:0px;
            }
            QPushButton:hover {
                color:white;
            }
        """)

        layout.addWidget(icon_lbl)
        layout.addWidget(heading)
        layout.addWidget(body)
        layout.addStretch()
        layout.addWidget(btn)

        return card

    def back_button(self):
        btn = QPushButton("← Back to Settings")
        btn.clicked.connect(self.load_home)
        btn.setFixedHeight(38)
        btn.setMaximumWidth(220)
        btn.setStyleSheet("""
            QPushButton {
                background:#0d6efd;
                color:white;
                border:none;
                border-radius:10px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:#0b5ed7;
            }
        """)
        return btn

    def detail_card(self, title_text):
        self.clear_page()

        self.main.addWidget(self.back_button())

        title = QLabel(title_text)
        title.setStyleSheet("font-size:30px;font-weight:900;color:white;")
        self.main.addWidget(title)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background:#081226;
                border:1px solid #1f70c1;
                border-radius:18px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        self.main.addWidget(card)
        return layout

    def open_profile_settings(self):
        layout = self.detail_card("👤 Profile Settings")

        info = QLabel(
            "Profile information is managed from the Profile page.\n\n"
            "You can update:\n"
            "• Full name\n"
            "• License number\n"
            "• Phone number\n"
            "• Vehicle number\n"
            "• Address\n"
            "• Date of birth\n"
            "• Profile photo"
        )
        info.setStyleSheet("color:#cbd5e1;font-size:16px;border:none;background:transparent;")
        layout.addWidget(info)

        open_btn = QPushButton("Go to Profile Page")
        open_btn.setFixedHeight(42)
        open_btn.clicked.connect(self.go_profile_page)
        open_btn.setStyleSheet("""
            QPushButton {
                background:#0d6efd;
                color:white;
                border:none;
                border-radius:10px;
                font-weight:bold;
            }
        """)
        layout.addWidget(open_btn)
        layout.addStretch()

    def go_profile_page(self):
        if self.dashboard:
            self.dashboard.open_profile()
        else:
            QMessageBox.information(self, "Profile", "Open Profile page from sidebar.")

    def open_change_password(self):
        layout = self.detail_card("🔐 Change Password")

        self.new_pass = QLineEdit()
        self.new_pass.setPlaceholderText("New Password")
        self.new_pass.setEchoMode(QLineEdit.Password)

        self.confirm_pass = QLineEdit()
        self.confirm_pass.setPlaceholderText("Confirm Password")
        self.confirm_pass.setEchoMode(QLineEdit.Password)

        for box in [self.new_pass, self.confirm_pass]:
            box.setFixedHeight(42)
            box.setStyleSheet("""
                QLineEdit {
                    background:#071426;
                    border:1px solid #1f70c1;
                    border-radius:10px;
                    padding-left:14px;
                    color:white;
                    font-size:14px;
                }
            """)
            layout.addWidget(box)

        save_btn = QPushButton("💾 Save Password")
        save_btn.clicked.connect(self.save_password)
        save_btn.setFixedHeight(42)
        save_btn.setStyleSheet("""
            QPushButton {
                background:#0d6efd;
                color:white;
                border:none;
                border-radius:10px;
                font-weight:bold;
            }
        """)

        layout.addWidget(save_btn)
        layout.addStretch()

    def save_password(self):
        p1 = self.new_pass.text().strip()
        p2 = self.confirm_pass.text().strip()

        if not p1 or not p2:
            QMessageBox.warning(self, "Error", "Please fill both password fields.")
            return

        if len(p1) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
            return

        if p1 != p2:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        reset_password_by_driver_id(self.driver_id, p1)
        QMessageBox.information(self, "Success", "Password updated successfully.")
        self.load_home()

    def open_alarm_settings(self):
        layout = self.detail_card("🔊 Alarm Sound Settings")

        alarm_check = QCheckBox("Enable alarm sound during drowsiness detection")
        alarm_check.setChecked(True)
        alarm_check.setStyleSheet("font-size:16px;color:white;border:none;background:transparent;")

        note = QLabel("This setting controls whether the alarm sound should play when drowsiness is detected.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#9aa7bd;font-size:14px;border:none;background:transparent;")

        layout.addWidget(alarm_check)
        layout.addWidget(note)
        layout.addStretch()

    def open_sensitivity_settings(self):
        layout = self.detail_card("👁️ Drowsiness Sensitivity")

        combo = QComboBox()
        combo.addItems(["Low", "Medium", "High"])
        combo.setCurrentText("Medium")
        combo.setFixedHeight(42)
        combo.setStyleSheet("""
            QComboBox {
                background:#071426;
                border:1px solid #1f70c1;
                border-radius:10px;
                color:white;
                padding-left:12px;
                font-size:14px;
            }
        """)

        note = QLabel(
            "Low: fewer alerts\n"
            "Medium: balanced detection\n"
            "High: more sensitive drowsiness detection"
        )
        note.setStyleSheet("color:#9aa7bd;font-size:14px;border:none;background:transparent;")

        layout.addWidget(combo)
        layout.addWidget(note)
        layout.addStretch()

    def open_notification_settings(self):
        layout = self.detail_card("🔔 Alert Notifications")

        notify_check = QCheckBox("Enable alert notifications")
        notify_check.setChecked(True)
        notify_check.setStyleSheet("font-size:16px;color:white;border:none;background:transparent;")

        note = QLabel("Alert notifications help the driver and system admin track drowsiness events.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#9aa7bd;font-size:14px;border:none;background:transparent;")

        layout.addWidget(notify_check)
        layout.addWidget(note)
        layout.addStretch()