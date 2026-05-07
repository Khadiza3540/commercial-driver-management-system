import os
import shutil

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLineEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from database import (
    get_driver_profile,
    update_driver_profile,
    update_driver_photo,
    get_monthly_profile_stats
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PROFILE_DIR = os.path.join(ASSETS_DIR, "profiles")
os.makedirs(PROFILE_DIR, exist_ok=True)


class ProfilePage(QWidget):
    def __init__(self, driver_id):
        super().__init__()

        self.driver_id = driver_id
        self.photo_path = None
        self.edit_mode = False
        self.inputs = {}

        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(25, 10, 25, 10)
        self.main.setSpacing(12)

        self.load_ui()

    def clear_layout(self):
        while self.main.count():
            item = self.main.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_child_layout(item.layout())

    def clear_child_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_child_layout(item.layout())

    def load_ui(self):
        self.clear_layout()
        self.inputs = {}

        data = get_driver_profile(self.driver_id)

        title = QLabel("👤 Driver Profile")
        title.setStyleSheet("font-size:28px;font-weight:bold;color:white;")
        self.main.addWidget(title)

        if not data:
            msg = QLabel("No profile data found")
            msg.setStyleSheet("color:#ef4444;font-size:18px;")
            self.main.addWidget(msg)
            return

        name, license_no, phone, vehicle, address, dob, photo = data
        self.photo_path = photo

        total_trips, total_alerts, safety_score = get_monthly_profile_stats(self.driver_id)

        card = QFrame()
        card.setMinimumHeight(720)
        card.setStyleSheet("""
            QFrame {
                background-color:#081226;
                border:1px solid #1f70c1;
                border-radius:18px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 14, 30, 14)
        card_layout.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(35)

        avatar_box = QVBoxLayout()
        avatar_box.setSpacing(8)

        self.avatar = QLabel("👤")
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setFixedSize(105, 105)
        self.avatar.setStyleSheet("""
            QLabel {
                background:#0b1830;
                border:2px solid #1f70c1;
                border-radius:52px;
                font-size:40px;
            }
        """)

        if photo and os.path.exists(photo):
            pix = QPixmap(photo).scaled(
                105, 105,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            self.avatar.setPixmap(pix)

        upload_btn = QPushButton("📷 Upload Photo")
        upload_btn.clicked.connect(self.upload_photo)
        upload_btn.setFixedHeight(42)
        upload_btn.setMinimumWidth(170)
        upload_btn.setStyleSheet("""
            QPushButton {
                background:#0d6efd;
                color:white;
                border:none;
                border-radius:12px;
                font-size:15px;
                font-weight:bold;
                padding:10px 18px;
                text-align:center;
            }

            QPushButton:hover {
                background:#0b5ed7;
            }
        """)

        avatar_box.addWidget(self.avatar, alignment=Qt.AlignCenter)
        avatar_box.addWidget(upload_btn, alignment=Qt.AlignHCenter)

        name_box = QVBoxLayout()
        name_box.setSpacing(8)

        name_lbl = QLabel(str(name))
        name_lbl.setStyleSheet("""
            QLabel {
                font-size:28px;
                font-weight:bold;
                color:white;
                border:none;
                background:transparent;
            }
        """)

        sub_lbl = QLabel(f"License: {license_no}   |   Vehicle: {vehicle}")
        sub_lbl.setStyleSheet("""
            QLabel {
                font-size:14px;
                color:#cbd5e1;
                border:none;
                background:transparent;
            }
        """)

        badge = QLabel("✅ Active Driver   •   Verified Account")
        badge.setFixedHeight(30)
        badge.setMaximumWidth(350)
        badge.setStyleSheet("""
            QLabel {
                background:#064e3b;
                color:#86efac;
                border:1px solid #1f70c1;
                border-radius:15px;
                padding-left:14px;
                padding-right:14px;
                font-size:13px;
                font-weight:bold;
            }
        """)

        name_box.addSpacing(12)
        name_box.addWidget(name_lbl)
        name_box.addSpacing(10)
        name_box.addWidget(sub_lbl)
        name_box.addSpacing(10)
        name_box.addWidget(badge)
        name_box.addStretch()

        top.addLayout(avatar_box)
        top.addLayout(name_box)
        top.addStretch()

        card_layout.addLayout(top)

        def stat_card(title, value, icon):
            box = QFrame()
            box.setFixedHeight(78)
            box.setStyleSheet("""
                QFrame {
                    background:#050b1a;
                    border:1px solid #1f70c1;
                    border-radius:14px;
                }
            """)

            lay = QVBoxLayout(box)
            lay.setContentsMargins(14, 8, 14, 8)

            v = QLabel(f"{icon}  {value}")
            v.setStyleSheet("""
                QLabel {
                    font-size:22px;
                    font-weight:bold;
                    color:white;
                    border:none;
                    background:transparent;
                }
            """)

            t = QLabel(title)
            t.setStyleSheet("""
                QLabel {
                    font-size:13px;
                    color:#9aa7bd;
                    border:none;
                    background:transparent;
                }
            """)

            lay.addWidget(v)
            lay.addWidget(t)
            return box

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        stats_row.addWidget(stat_card("Monthly Trips", str(total_trips), "📊"))
        stats_row.addWidget(stat_card("Monthly Alerts", str(total_alerts), "🚨"))
        stats_row.addWidget(stat_card("Safety Score", f"{safety_score}%", "🛡️"))
        card_layout.addLayout(stats_row)

        performance = QFrame()
        performance.setFixedHeight(65)
        performance.setStyleSheet("""
            QFrame {
                background:#050b1a;
                border:1px dashed #1f70c1;
                border-radius:14px;
            }
        """)

        perf_layout = QVBoxLayout(performance)
        perf_layout.setContentsMargins(18, 10, 18, 10)

        perf_title = QLabel(f"Safety Performance - {safety_score}%")
        perf_title.setStyleSheet("""
            QLabel {
                font-size:14px;
                font-weight:bold;
                color:white;
                border:none;
                background:transparent;
            }
        """)

        progress_bg = QFrame()
        progress_bg.setFixedHeight(12)
        progress_bg.setStyleSheet("""
            QFrame {
                background:#1e293b;
                border:none;
                border-radius:6px;
            }
        """)

        progress_layout = QHBoxLayout(progress_bg)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(0)

        progress_fill = QFrame()
        progress_fill.setFixedWidth(max(10, int(700 * safety_score / 100)))
        progress_fill.setStyleSheet("""
            QFrame {
                background:#22c55e;
                border:none;
                border-radius:6px;
            }
        """)

        progress_layout.addWidget(progress_fill)
        progress_layout.addStretch()

        perf_layout.addWidget(perf_title)
        perf_layout.addWidget(progress_bg)
        card_layout.addWidget(performance)

        details_box = QWidget()
        details_layout = QVBoxLayout(details_box)
        details_layout.setContentsMargins(0, 8, 0, 8)
        details_layout.setSpacing(14)

        def add_row(label, key, value):
            row = QHBoxLayout()
            row.setSpacing(22)

            label_widget = QLabel(label)
            label_widget.setFixedWidth(230)
            label_widget.setFixedHeight(34)
            label_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label_widget.setStyleSheet("""
                QLabel {
                    color:#18a0ff;
                    font-weight:bold;
                    font-size:15px;
                    border:none;
                    background:transparent;
                }
            """)

            input_box = QLineEdit(str(value) if value else "")
            input_box.setReadOnly(True)
            input_box.setFixedHeight(34)
            input_box.setStyleSheet("""
                QLineEdit {
                    background:#071426;
                    border:1px solid #1f70c1;
                    border-radius:10px;
                    padding-left:14px;
                    color:white;
                    font-size:15px;
                }
            """)

            self.inputs[key] = input_box
            row.addWidget(label_widget)
            row.addWidget(input_box, 1)
            details_layout.addLayout(row)

        add_row("👤 Full Name", "name", name)
        add_row("🪪 License Number", "license", license_no)
        add_row("📞 Phone Number", "phone", phone)
        add_row("🚗 Vehicle Number", "vehicle", vehicle)
        add_row("📍 Address", "address", address)
        add_row("🎂 Date of Birth", "dob", dob)

        card_layout.addWidget(details_box)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.edit_btn = QPushButton("✏️ Edit Profile")
        self.edit_btn.clicked.connect(self.toggle_edit)
        self.edit_btn.setFixedHeight(42)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background:#0d6efd;
                color:white;
                border:none;
                border-radius:12px;
                padding:8px 22px;
                font-weight:bold;
                font-size:14px;
            }
        """)

        btn_row.addWidget(self.edit_btn)
        card_layout.addLayout(btn_row)

        self.main.addWidget(card)


    def toggle_edit(self):
        self.edit_mode = not self.edit_mode

        for box in self.inputs.values():
            box.setReadOnly(not self.edit_mode)

        if self.edit_mode:
            self.edit_btn.setText("💾 Save Profile")
        else:
            try:
                update_driver_profile(
                    self.driver_id,
                    self.inputs["name"].text(),
                    self.inputs["license"].text(),
                    self.inputs["phone"].text(),
                    self.inputs["vehicle"].text(),
                    self.inputs["address"].text(),
                    self.inputs["dob"].text()
                )
                QMessageBox.information(self, "Success", "Profile updated successfully")
                self.load_ui()
            except Exception as e:
                QMessageBox.critical(self, "Update Error", str(e))

    def upload_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Profile Photo",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if not file_path:
            return

        ext = os.path.splitext(file_path)[1]
        new_path = os.path.join(PROFILE_DIR, f"driver_{self.driver_id}{ext}")

        try:
            shutil.copy(file_path, new_path)
            update_driver_photo(self.driver_id, new_path)
            QMessageBox.information(self, "Success", "Profile photo updated")
            self.load_ui()
        except Exception as e:
            QMessageBox.critical(self, "Photo Error", str(e))