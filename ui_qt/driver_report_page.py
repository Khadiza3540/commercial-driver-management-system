from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFrame, QGridLayout
)
from PySide6.QtCore import Qt


class DriverReportPage(QWidget):
    def __init__(self, driver_data):
        super().__init__()

        self.setWindowTitle("Driver Safety Report")
        self.resize(1400, 780)

        d = driver_data
        driver_id, name, username, email, license_no, phone, vehicle, status, authorized, trips, alerts = d

        trips = int(trips)
        alerts = int(alerts)
        score = max(0, 100 - alerts * 5)

        if str(status).lower() == "disabled":
            risk = "Disabled"
            risk_color = "#ef4444"
            recommendation = "Driver account is currently disabled. Admin can enable this profile after review."
            status_subtitle = "Driver login is currently blocked"
            status_color = "#ef4444"
        elif score >= 80:
            risk = "Safe"
            risk_color = "#22c55e"
            recommendation = "Driver is performing safely. No immediate action required."
            status_subtitle = "Driver is currently active"
            status_color = "#15803d"
        elif score >= 50:
            risk = "Moderate"
            risk_color = "#f59e0b"
            recommendation = "Driver should be monitored regularly for safety improvement."
            status_subtitle = "Driver is currently active"
            status_color = "#15803d"
        elif score >= 30:
            risk = "Risky"
            risk_color = "#f97316"
            recommendation = "Warning recommended. Admin should review recent alerts."
            status_subtitle = "Driver is currently active"
            status_color = "#15803d"
        else:
            risk = "High Risk"
            risk_color = "#ef4444"
            recommendation = "Driver should be disabled until admin review and approval."
            status_subtitle = "Auto disable recommended"
            status_color = "#ef4444"

        self.setStyleSheet("""
            QWidget {
                background:#050b1a;
                color:white;
                font-family:Segoe UI;
            }

            QLabel {
                background:transparent;
            }

            QFrame#card {
                background:#071426;
                border:1px solid #1f70c1;
                border-radius:18px;
            }

            QLabel#title {
                font-size:30px;
                font-weight:900;
                color:white;
            }

            QLabel#section {
                font-size:18px;
                font-weight:900;
                color:#18a0ff;
            }

            QLabel#label {
                font-size:13px;
                color:#9aa7bd;
            }

            QLabel#value {
                font-size:13px;
                color:white;
                font-weight:bold;
            }

            QLabel#muted {
                font-size:13px;
                color:#9aa7bd;
            }

            QPushButton {
                background:#2563eb;
                color:white;
                border:none;
                border-radius:12px;
                font-size:14px;
                font-weight:bold;
            }

            QPushButton:hover {
                background:#18a0ff;
            }
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(30, 22, 30, 22)
        main.setSpacing(12)

        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(5)

        title = QLabel("Driver Safety Report")
        title.setObjectName("title")

        sub = QLabel(f"👤 {name}    |    🚘 Vehicle: {vehicle}    |    🛡 Risk Level: {risk}")
        sub.setObjectName("muted")

        title_box.addWidget(title)
        title_box.addWidget(sub)

        close_btn = QPushButton("✕ Close")
        close_btn.setFixedSize(110, 42)
        close_btn.clicked.connect(self.close)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(close_btn)

        main.addLayout(header)

        top = QHBoxLayout()
        top.setSpacing(16)

        # ================= PROFILE CARD =================
        profile_card = QFrame()
        profile_card.setObjectName("card")
        profile_card.setMinimumHeight(250)
        profile_card.setMaximumHeight(250)

        profile_layout = QVBoxLayout(profile_card)
        profile_layout.setContentsMargins(24, 18, 24, 18)
        profile_layout.setSpacing(14)

        profile_title = QLabel("👤 Driver Profile")
        profile_title.setObjectName("section")
        profile_layout.addWidget(profile_title)

        profile_grid = QGridLayout()
        profile_grid.setHorizontalSpacing(26)
        profile_grid.setVerticalSpacing(10)

        profile_items = [
            ("Driver ID", driver_id),
            ("Name", name),
            ("Username", username),
            ("Email", email),
            ("License", license_no),
            ("Phone", phone),
            ("Vehicle No", vehicle),
            ("Status", status),
            ("Authorized", authorized),
        ]

        for i, (label, value) in enumerate(profile_items):
            row = i // 2
            col = (i % 2) * 2

            label_widget = QLabel(str(label))
            label_widget.setObjectName("label")

            value_widget = QLabel(str(value))
            value_widget.setObjectName("value")
            value_widget.setWordWrap(True)

            profile_grid.addWidget(label_widget, row, col)
            profile_grid.addWidget(value_widget, row, col + 1)

        profile_layout.addLayout(profile_grid)
        profile_layout.addStretch()

        # ================= SCORE CARD =================
        score_card = QFrame()
        score_card.setObjectName("card")
        score_card.setMinimumHeight(250)
        score_card.setMaximumHeight(250)
        score_card.setMinimumWidth(420)

        score_layout = QVBoxLayout(score_card)
        score_layout.setContentsMargins(24, 16, 24, 16)
        score_layout.setSpacing(6)
        score_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        score_title = QLabel("🛡 Safety Score")
        score_title.setObjectName("section")
        score_title.setAlignment(Qt.AlignCenter)

        score_box = QLabel(f"{score}%")
        score_box.setAlignment(Qt.AlignCenter)
        score_box.setFixedSize(130, 130)
        score_box.setStyleSheet(f"""
            QLabel {{
                background:#050b1a;
                border:12px solid {risk_color};
                border-radius:65px;
                color:white;
                font-size:28px;
                font-weight:900;
            }}
        """)

        risk_badge = QLabel(risk)
        risk_badge.setAlignment(Qt.AlignCenter)
        risk_badge.setFixedSize(125, 34)
        risk_badge.setStyleSheet(f"""
            QLabel {{
                background:{risk_color};
                color:white;
                border-radius:10px;
                font-size:15px;
                font-weight:900;
            }}
        """)

        score_layout.addWidget(score_title, alignment=Qt.AlignCenter)
        score_layout.addSpacing(2)
        score_layout.addWidget(score_box, alignment=Qt.AlignCenter)
        score_layout.addSpacing(4)
        score_layout.addWidget(risk_badge, alignment=Qt.AlignCenter)

        top.addWidget(profile_card, 2)
        top.addWidget(score_card, 1)

        main.addLayout(top)

        # ================= STATS =================
        stats = QHBoxLayout()
        stats.setSpacing(16)

        stats.addWidget(self.stat_card("🛣", "Total Trips", trips, "All time trips completed", "#1d4ed8"))
        stats.addWidget(self.stat_card("🚨", "Total Alerts", alerts, "Total alerts generated", "#be123c"))
        stats.addWidget(self.stat_card("✅", "Current Status", status, status_subtitle, status_color))

        main.addLayout(stats)

        # ================= RECOMMENDATION =================
        rec_card = QFrame()
        rec_card.setObjectName("card")
        rec_card.setMinimumHeight(125)
        rec_card.setMaximumHeight(145)

        rec_layout = QVBoxLayout(rec_card)
        rec_layout.setContentsMargins(24, 16, 24, 16)
        rec_layout.setSpacing(8)

        rec_title = QLabel("⭐ Admin Recommendation")
        rec_title.setObjectName("section")

        rec_text = QLabel(f"ℹ  {recommendation}")
        rec_text.setWordWrap(True)
        rec_text.setStyleSheet("""
            QLabel {
                background:#11183a;
                border-left:4px solid #8b5cf6;
                border-radius:12px;
                padding:10px 14px;
                color:white;
                font-size:13px;
            }
        """)

        rec_layout.addWidget(rec_title)
        rec_layout.addWidget(rec_text)

        main.addWidget(rec_card)
        main.addStretch()

    def stat_card(self, icon, title, value, subtitle, color):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(105)
        card.setMaximumHeight(120)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(16)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFixedSize(58, 58)
        icon_lbl.setStyleSheet(f"""
            QLabel {{
                background:{color};
                border-radius:15px;
                font-size:26px;
            }}
        """)

        text = QVBoxLayout()
        text.setSpacing(3)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size:13px;color:#cbd5e1;font-weight:bold;background:transparent;")

        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet("font-size:24px;color:white;font-weight:900;background:transparent;")

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("font-size:12px;color:#9aa7bd;background:transparent;")

        text.addWidget(title_lbl)
        text.addWidget(value_lbl)
        text.addWidget(sub_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text)
        layout.addStretch()

        return card