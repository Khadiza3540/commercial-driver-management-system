from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFrame,
    QPushButton, QGridLayout
)
from PySide6.QtCore import Qt


class HelpCenterPage(QWidget):
    def __init__(self):
        super().__init__()

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
        hero_layout.setSpacing(10)

        title = QLabel("Help Center")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size:30px;
                font-weight:900;
                color:white;
                border:none;
                background:transparent;
            }
        """)

        subtitle = QLabel("Got a question about CDMS? We’re here to help drivers stay safe.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color:#9aa7bd;
                font-size:14px;
                border:none;
                background:transparent;
            }
        """)

        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)

        self.main.addWidget(hero)

        topic_title = QLabel("Explore all topics")
        topic_title.setStyleSheet("""
            QLabel {
                color:white;
                font-size:20px;
                font-weight:bold;
            }
        """)
        self.main.addWidget(topic_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(22)
        grid.setVerticalSpacing(22)

        grid.addWidget(self.topic_card(
            "🚀",
            "Quick Help",
            "Learn the basic workflow: start monitoring, end monitoring, and check trips.",
            lambda: self.open_detail(
                "🚀 Quick Help",
                "• Go to Monitoring page.\n"
                "• Fill Current Location and Destination.\n"
                "• Click Start Monitoring to open camera monitoring.\n"
                "• Keep your face visible to the camera.\n"
                "• Click End Monitoring to close session and save trip.\n"
                "• Check Trips page to see trip history.\n"
                "• Check Alerts page to see drowsiness alerts."
            )
        ), 0, 0)

        grid.addWidget(self.topic_card(
            "🛡️",
            "Driver Safety Tips",
            "Important safety guidance for commercial drivers during long trips.",
            lambda: self.open_detail(
                "🛡️ Driver Safety Tips",
                "• Stop driving safely if you feel sleepy.\n"
                "• Take short breaks during long-distance trips.\n"
                "• Drink water and stay hydrated.\n"
                "• Avoid driving at night when extremely tired.\n"
                "• Do not ignore drowsiness alerts.\n"
                "• Park safely before resting.\n"
                "• Keep your face clearly visible for monitoring."
            )
        ), 0, 1)

        grid.addWidget(self.topic_card(
            "🛠️",
            "Troubleshooting",
            "Fix common camera, face authorization, alarm, trip, and database problems.",
            lambda: self.open_detail(
                "🛠️ Troubleshooting",
                "Camera not opening:\n"
                "• Check webcam connection.\n"
                "• Close other apps using camera.\n"
                "• Restart the software.\n\n"
                "Face not authorized:\n"
                "• Register driver face again.\n"
                "• Make sure lighting is clear.\n"
                "• Keep face straight to the camera.\n\n"
                "Alarm not playing:\n"
                "• Check speaker volume.\n"
                "• Check alarm file path.\n"
                "• Test alarm sound manually.\n\n"
                "Trip not saving:\n"
                "• Check PostgreSQL connection.\n"
                "• Make sure Start and End Monitoring are used properly."
            )
        ), 0, 2)

        grid.addWidget(self.topic_card(
            "📞",
            "Contact Support",
            "Find developer/admin support information for project issues.",
            lambda: self.open_detail(
                "📞 Contact Support",
                "Developer: Khadiza Akter Konok\n"
                "Project: Commercial Driver Management System\n"
                "Support Type: Project/Admin Support\n\n"
                "For technical issues:\n"
                "• Contact the developer/admin.\n"
                "• Share screenshot of the error.\n"
                "• Mention which page has the problem.\n"
                "• Share terminal error message if available."
            )
        ), 1, 0)

        grid.addWidget(self.topic_card(
            "ℹ️",
            "About CDMS",
            "Understand the purpose and features of the Commercial Driver Management System.",
            lambda: self.open_detail(
                "ℹ️ About CDMS",
                "CDMS is a driver safety monitoring system designed for commercial drivers.\n\n"
                "Main features:\n"
                "• Driver registration and profile management\n"
                "• Face-based driver authorization\n"
                "• Real-time camera monitoring\n"
                "• Drowsiness detection\n"
                "• Alarm alert system\n"
                "• Trip history tracking\n"
                "• Alerts history\n"
                "• Safety analytics dashboard\n"
                "• Driver settings and help center"
            )
        ), 1, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        self.main.addLayout(grid)
        self.main.addStretch()

    def topic_card(self, icon, title_text, body_text, action):
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
        icon_lbl.setStyleSheet("""
            QLabel {
                font-size:30px;
                border:none;
                background:transparent;
            }
        """)

        heading = QLabel(title_text)
        heading.setStyleSheet("""
            QLabel {
                color:white;
                font-size:17px;
                font-weight:bold;
                border:none;
                background:transparent;
            }
        """)

        body = QLabel(body_text)
        body.setWordWrap(True)
        body.setStyleSheet("""
            QLabel {
                color:#9aa7bd;
                font-size:13px;
                border:none;
                background:transparent;
            }
        """)

        see_more = QPushButton("See detail →")
        see_more.clicked.connect(action)
        see_more.setFixedHeight(28)
        see_more.setStyleSheet("""
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
        layout.addWidget(see_more)

        return card

    def open_detail(self, title_text, details):
        self.clear_page()

        back_btn = QPushButton("← Back to Help Center")
        back_btn.clicked.connect(self.load_home)
        back_btn.setFixedHeight(38)
        back_btn.setMaximumWidth(220)
        back_btn.setStyleSheet("""
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

        title = QLabel(title_text)
        title.setStyleSheet("""
            QLabel {
                font-size:30px;
                font-weight:900;
                color:white;
            }
        """)

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

        body = QLabel(details)
        body.setWordWrap(True)
        body.setStyleSheet("""
            QLabel {
                color:#cbd5e1;
                font-size:16px;
                border:none;
                background:transparent;
            }
        """)

        layout.addWidget(body)

        self.main.addWidget(back_btn)
        self.main.addWidget(title)
        self.main.addWidget(card)
        self.main.addStretch()