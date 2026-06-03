import sys
import os

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMessageBox,
    QGridLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class InfoPage(QWidget):
    def __init__(self, title, content):
        super().__init__()

        self.setWindowTitle(title)
        self.resize(1100, 700)
        self.setMinimumSize(1000, 650)

        self.setStyleSheet("""
            QWidget {
                background-color: #050b1a;
                color: white;
                font-family: Segoe UI;
            }

            QLabel {
                background: transparent;
            }

            QPushButton#backBtn {
                background-color: transparent;
                color: #18a0ff;
                border: 1px solid #18a0ff;
                border-radius: 10px;
                padding: 9px 14px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton#backBtn:hover {
                background-color: #0d6efd;
                color: white;
            }

            QFrame#heroCard, QFrame#infoCard {
                background-color: #071426;
                border: 1px solid #1683ff;
                border-radius: 18px;
            }

            QFrame#infoCard:hover {
                border: 1px solid #18a0ff;
                background-color: #0a1b32;
            }

            QLabel#pageTitle {
                color: #18a0ff;
                font-size: 30px;
                font-weight: 900;
            }

            QLabel#pageSub {
                color: #cbd5e1;
                font-size: 14px;
            }

            QLabel#mainIcon {
                font-size: 72px;
            }

            QLabel#icon {
                font-size: 28px;
            }

            QLabel#cardTitle {
                color: white;
                font-size: 15px;
                font-weight: bold;
            }

            QLabel#cardText {
                color: #aab6cc;
                font-size: 12px;
            }
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(14)

        back_btn = QPushButton("← Back to Home")
        back_btn.setObjectName("backBtn")
        back_btn.setFixedSize(155, 42)
        back_btn.clicked.connect(self.close)
        main.addWidget(back_btn)

        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        hero_card.setFixedHeight(190)

        hero_layout = QHBoxLayout(hero_card)
        hero_layout.setContentsMargins(28, 22, 28, 22)
        hero_layout.setSpacing(22)

        left = QVBoxLayout()
        left.setSpacing(10)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("pageTitle")

        sub_lbl = QLabel(self.get_subtitle(title))
        sub_lbl.setObjectName("pageSub")
        sub_lbl.setWordWrap(True)

        left.addStretch()
        left.addWidget(title_lbl)
        left.addWidget(sub_lbl)
        left.addStretch()

        visual = QLabel(self.get_main_icon(title))
        visual.setObjectName("mainIcon")
        visual.setAlignment(Qt.AlignCenter)
        visual.setFixedSize(240, 130)
        visual.setStyleSheet("""
            QLabel {
                background-color: #081226;
                border: 1px solid #1f70c1;
                border-radius: 18px;
            }
        """)

        hero_layout.addLayout(left, 2)
        hero_layout.addWidget(visual, 1)

        main.addWidget(hero_card)

        grid = QGridLayout()
        grid.setSpacing(12)

        cards = self.get_cards(title)

        for i, item in enumerate(cards):
            grid.addWidget(
                self.create_info_card(item[0], item[1], item[2]),
                i // 3,
                i % 3
            )

        main.addLayout(grid)
        main.addStretch()

    def get_main_icon(self, title):
        if "About" in title:
            return "🛡"
        elif "Features" in title:
            return "⚙️"
        elif "Modules" in title:
            return "📦"
        elif "Contact" in title:
            return "📞"
        return "🚗"

    def get_subtitle(self, title):
        if "About" in title:
            return "CDMS is an AI-powered commercial driver monitoring system designed to improve driver safety, reduce fatigue risk, and support smart transportation management."
        elif "Features" in title:
            return "Explore the core features of the system including monitoring, drowsiness detection, face authentication, smart alerts, trips, and reports."
        elif "Modules" in title:
            return "The system is divided into organized modules for driver registration, monitoring, alerts, trips, AI assistant, and admin management."
        elif "Contact" in title:
            return "Project and developer information for the Commercial Driver Management System."
        return ""

    def create_info_card(self, icon, title, text):
        card = QFrame()
        card.setObjectName("infoCard")
        card.setFixedHeight(125)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 13, 18, 13)
        layout.setSpacing(5)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("icon")
        icon_lbl.setFixedHeight(30)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("cardTitle")

        text_lbl = QLabel(text)
        text_lbl.setObjectName("cardText")
        text_lbl.setWordWrap(True)

        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(text_lbl)
        layout.addStretch()

        return card

    def get_cards(self, title):
        if "About" in title:
            return [
                ("🚗", "Driver Safety", "Improves commercial driver safety through monitoring and detection."),
                ("😴", "Fatigue Detection", "Detects sleepy driving behavior using computer vision logic."),
                ("📊", "Management Control", "Provides centralized control for drivers, trips, alerts, and reports."),
                ("🧑", "Face Verification", "Verifies registered drivers before system access."),
                ("🛣", "Trip Tracking", "Stores trip records, status, destination, and history."),
                ("🤖", "AI Assistance", "Supports safety-focused driver interaction using AI assistant.")
            ]

        elif "Features" in title:
            return [
                ("📡", "Real-Time Monitoring", "Live driver activity monitoring with session tracking."),
                ("😴", "Drowsiness Detection", "Detects fatigue signs using eye activity and alert logic."),
                ("🧑", "Face Authentication", "Secures login through registered driver verification."),
                ("🚨", "Smart Alerts", "Generates alert records during risky driving conditions."),
                ("🛣", "Trip Management", "Manages active trips, completed trips, and route history."),
                ("📈", "Reports & Analytics", "Shows safety score, alert summary, and trip statistics.")
            ]

        elif "Modules" in title:
            return [
                ("01", "Driver Registration", "Stores driver information and captures face dataset."),
                ("02", "Driver Dashboard", "Displays profile, monitoring, trips, alerts, and assistant."),
                ("03", "Drowsiness Detector", "Detects sleepy state using computer vision."),
                ("04", "Trip Manager", "Handles route, destination, status, and trip history."),
                ("05", "Alert Manager", "Stores drowsiness alerts and safety warnings."),
                ("06", "Admin Panel", "Manages all drivers, alerts, trips, reports, and analytics.")
            ]

        elif "Contact" in title:
            return [
                ("👩‍💻", "Developer", "Khadiza Akter Konok"),
                ("🎓", "Department", "Computer Science & Engineering"),
                ("🛠", "Technology", "Python, PySide6, PostgreSQL, OpenCV, dlib, AI API"),
                ("📌", "Project Type", "AI-Based Driver Safety & Monitoring Platform"),
                ("📦", "Version", "Version 1.0"),
                ("🛡", "System", "Commercial Driver Management System")
            ]


        return []


class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CDMS - Driver Management System")
        self.resize(1200, 700)
        self.setMinimumSize(1000, 650)
        self.nav_buttons = []

        central = QWidget()
        self.setCentralWidget(central)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #050b1a;
                color: white;
                font-family: Segoe UI;
            }

            QLabel {
                background: transparent;
            }

            QLabel#brandText {
                color: #18a0ff;
                font-size: 28px;
                font-weight: 900;
            }

            QLabel#brandSub {
                color: #c4c9d8;
                font-size: 11px;
            }

            QPushButton#navActive {
                color: #18a0ff;
                font-size: 13px;
                font-weight: bold;
                background: transparent;
                border: none;
                border-bottom: 2px solid #18a0ff;
                padding: 8px 4px;
            }

            QPushButton#navItem {
                color: #c4c9d8;
                font-size: 13px;
                background: transparent;
                border: none;
                padding: 8px 4px;
            }

            QPushButton#navItem:hover {
                color: #18a0ff;
            }

            QLabel#heroTitle, QLabel#heroTitleBlue {
                font-size: 34px;
                font-weight: 900;
            }

            QLabel#heroTitle {
                color: white;
            }

            QLabel#heroTitleBlue {
                color: #2f8cff;
            }

            QLabel#heroDesc {
                color: #c6cedd;
                font-size: 13px;
            }

            QPushButton#loginBtn {
                background-color: transparent;
                color: white;
                border: 1px solid #1aa7ff;
                border-radius: 9px;
                font-size: 12px;
                font-weight: bold;
                padding: 7px 12px;
            }

            QPushButton#loginBtn:hover {
                background-color: #0d6efd;
            }

            QPushButton#registerBtn {
                background-color: transparent;
                color: white;
                border: 1px solid #1f70c1;
                border-radius: 9px;
                font-size: 12px;
                font-weight: bold;
                padding: 7px 12px;
            }

            QPushButton#registerBtn:hover {
                background-color: #0d6efd;
            }

            QFrame#statCard {
                background-color: rgba(8, 18, 38, 185);
                border: 1px solid rgba(30, 90, 155, 150);
                border-radius: 16px;
            }

            QFrame#statCard:hover {
                border: 1px solid #18a0ff;
            }

            QLabel#statNumber {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }

            QLabel#statTitle {
                color: white;
                font-size: 13px;
                font-weight: bold;
            }

            QLabel#statSub {
                color: #9aa7bd;
                font-size: 11px;
            }

            QLabel#footer {
                color: #8f9bad;
                font-size: 12px;
            }
        """)

        main = QVBoxLayout(central)
        main.setContentsMargins(30, 20, 30, 15)
        main.setSpacing(12)

        # ================= HEADER =================
        header = QHBoxLayout()
        header.setSpacing(14)

        logo_label = QLabel()
        logo_path = os.path.join(ASSETS_DIR, "logo.png")

        if os.path.exists(logo_path):
            logo_pix = QPixmap(logo_path).scaled(
                95, 95,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            logo_label.setPixmap(logo_pix)
        else:
            logo_label.setText("🛡")
            logo_label.setStyleSheet("font-size:38px;color:#18a0ff;")

        brand_box = QHBoxLayout()
        brand_box.setSpacing(6)
        brand_box.addWidget(logo_label)

        brand_text_box = QVBoxLayout()
        brand_text_box.setSpacing(0)

        brand = QLabel("CDMS")
        brand.setObjectName("brandText")

        brand_sub = QLabel("Commercial Driver Management System")
        brand_sub.setObjectName("brandSub")

        brand_text_box.addWidget(brand)
        brand_text_box.addWidget(brand_sub)

        brand_box.addLayout(brand_text_box)
        header.addLayout(brand_box)
        header.addStretch()

        # ================= NAVBAR =================
        nav = QHBoxLayout()
        nav.setSpacing(28)

        for text, active in [
            ("Home", True),
            ("About", False),
            ("Features", False),
            ("Modules", False),
            ("Contact", False),

        ]:
            btn = QPushButton(text)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName("navActive" if active else "navItem")
            btn.clicked.connect(lambda checked=False, b=btn: self.set_active_nav(b))
            self.nav_buttons.append(btn)
            nav.addWidget(btn)

        header.addLayout(nav)
        header.addStretch()

        # ================= TOP BUTTONS =================
        top_btn_layout = QHBoxLayout()
        top_btn_layout.setSpacing(10)

        login_btn = QPushButton("👤  Login")
        login_btn.setObjectName("loginBtn")
        login_btn.setFixedHeight(38)
        login_btn.setFixedWidth(105)

        register_btn = QPushButton("👥  Register")
        register_btn.setObjectName("registerBtn")
        register_btn.setFixedHeight(38)
        register_btn.setFixedWidth(125)

        top_btn_layout.addWidget(login_btn)
        top_btn_layout.addWidget(register_btn)
        header.addLayout(top_btn_layout)



        main.addLayout(header)

        # ================= HERO =================
        hero = QHBoxLayout()
        hero.setSpacing(26)

        left = QVBoxLayout()
        left.setSpacing(12)

        title1 = QLabel("Smart Driver Safety")
        title1.setObjectName("heroTitle")

        title2 = QLabel("& Monitoring System")
        title2.setObjectName("heroTitleBlue")

        underline = QLabel("━━━━")
        underline.setStyleSheet("color:#18a0ff;font-size:16px;font-weight:bold;")

        desc = QLabel(
            "A modern desktop application for driver registration, face authentication,\n"
            "drowsiness detection, real-time monitoring, alerts and trip management."
        )
        desc.setObjectName("heroDesc")
        desc.setWordWrap(True)

        left.addStretch()
        left.addWidget(title1)
        left.addWidget(title2)
        left.addWidget(underline)
        left.addSpacing(6)
        left.addWidget(desc)
        left.addStretch()

        right = QVBoxLayout()
        hero_img = QLabel()
        hero_img.setAlignment(Qt.AlignCenter)

        hero_path = os.path.join(ASSETS_DIR, "hero.png")

        if os.path.exists(hero_path):
            hero_pix = QPixmap(hero_path).scaled(
                480, 320,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            hero_img.setPixmap(hero_pix)
        else:
            hero_img.setText("Driver Monitoring Visual")
            hero_img.setStyleSheet("""
                color:#18a0ff;
                font-size:18px;
                border:1px solid #1f3f67;
                border-radius:16px;
                padding:100px;
            """)

        right.addStretch()
        right.addWidget(hero_img)
        right.addStretch()

        hero.addLayout(left, 1)
        hero.addLayout(right, 1)
        main.addLayout(hero, stretch=1)

        # ================= STAT CARDS =================
        stats = QHBoxLayout()
        stats.setSpacing(16)

        def create_card(icon, number, title, sub, accent):
            card = QFrame()
            card.setObjectName("statCard")
            card.setMinimumHeight(110)

            layout = QHBoxLayout(card)
            layout.setContentsMargins(20, 18, 20, 18)
            layout.setSpacing(16)

            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(58, 58)
            icon_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {accent};
                    border-radius: 14px;
                    font-size: 24px;
                }}
            """)

            text_box = QVBoxLayout()
            text_box.setSpacing(4)

            num = QLabel(number)
            num.setObjectName("statNumber")

            title_lbl = QLabel(title)
            title_lbl.setObjectName("statTitle")

            sub_lbl = QLabel(sub)
            sub_lbl.setObjectName("statSub")

            text_box.addStretch()
            text_box.addWidget(num)
            text_box.addWidget(title_lbl)
            text_box.addWidget(sub_lbl)
            text_box.addStretch()

            layout.addWidget(icon_label)
            layout.addLayout(text_box)
            layout.addStretch()

            return card

        stats.addWidget(create_card("👥", "500+", "Registered Drivers", "Commercial driver profiles", "#3b0f6f"))
        stats.addWidget(create_card("🛡", "24/7", "Live Monitoring", "Real-time safety tracking", "#082f68"))
        stats.addWidget(create_card("🔔", "AI", "Smart Alerts", "Drowsiness detection system", "#65350f"))
        stats.addWidget(create_card("📈", "98%", "Safety Accuracy", "AI monitoring performance", "#064e3b"))

        main.addLayout(stats)

        footer = QLabel("Developed by Khadiza Akter Konok   |   Version 1.0")
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignCenter)
        main.addWidget(footer)

        login_btn.clicked.connect(self.open_login)
        register_btn.clicked.connect(self.open_register)

    def set_active_nav(self, clicked_btn):
        for btn in self.nav_buttons:
            btn.setObjectName("navItem")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        clicked_btn.setObjectName("navActive")
        clicked_btn.style().unpolish(clicked_btn)
        clicked_btn.style().polish(clicked_btn)

        page = clicked_btn.text()

        if page == "Home":
            return

        if page == "About":
            content = (
                "Commercial Driver Management System (CDMS) is an AI-powered desktop application "
                "designed to improve commercial driver safety through real-time monitoring, "
                "drowsiness detection, face authentication, trip management, alert tracking, "
                "and centralized admin control.\n\n"
                "The system helps transport organizations manage drivers efficiently and reduce "
                "fatigue-related risks using computer vision and intelligent monitoring."
            )
            self.info_page = InfoPage("About CDMS", content)
            self.info_page.showMaximized()

        elif page == "Features":
            content = (
                "• Real-Time Driver Monitoring\n\n"
                "• AI-Based Drowsiness Detection\n\n"
                "• Face Authentication and Verification\n\n"
                "• Smart Alert System\n\n"
                "• Trip Management\n\n"
                "• Driver Dashboard\n\n"
                "• Admin Management Panel\n\n"
                "• Reports and Analytics"
            )
            self.info_page = InfoPage("Key Features", content)
            self.info_page.showMaximized()

        elif page == "Modules":
            content = (
                "01. Driver Registration Module\n\n"
                "02. Login and OTP Verification Module\n\n"
                "03. Face Recognition Module\n\n"
                "04. Drowsiness Detection Module\n\n"
                "05. Trip Management Module\n\n"
                "06. Alert Management Module\n\n"
                "07. AI Driver Assistant Module\n\n"
                "08. Admin Dashboard Module"
            )
            self.info_page = InfoPage("System Modules", content)
            self.info_page.showMaximized()

        elif page == "Contact":
            content = (
                "Developer: Khadiza Akter Konok\n\n"
                "Project: Commercial Driver Management System\n\n"
                "Technology: Python, PySide6, PostgreSQL, OpenCV, dlib, AI API\n\n"
                "System Type: AI-Based Driver Safety & Monitoring Platform\n\n"
                "Version: 1.0"
            )
            self.info_page = InfoPage("Contact & Project Info", content)
            self.info_page.showMaximized()



    def open_login(self):
        try:
            from ui_qt.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.showMaximized()

        except Exception as e:
            QMessageBox.critical(self, "Login Window Error", str(e))

    def open_register(self):
        try:
            from ui_qt.register_window import RegisterWindow
            self.register_window = RegisterWindow()
            self.register_window.showMaximized()
        except Exception as e:
            QMessageBox.critical(self, "Register Window Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.showMaximized()
    sys.exit(app.exec())