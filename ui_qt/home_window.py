import sys
import os


from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


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

        stats.addWidget(create_card("👥", "125", "Total Drivers", "Registered in system", "#3b0f6f"))
        stats.addWidget(create_card("🛡", "24/7", "Monitoring", "Real-time tracking", "#082f68"))
        stats.addWidget(create_card("🔔", "8", "Alerts Today", "Active notifications", "#65350f"))
        stats.addWidget(create_card("📈", "96%", "Safety Score", "Overall performance", "#064e3b"))

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

        print(f"{clicked_btn.text()} tab clicked")

    def open_login(self):
        try:
            from ui_qt.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.showMaximized()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Login Window Error", str(e))

    def open_register(self):
        try:
            from ui_qt.register_window import RegisterWindow
            self.register_window = RegisterWindow()
            self.register_window.showMaximized()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Register Window Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.showMaximized()
    sys.exit(app.exec())