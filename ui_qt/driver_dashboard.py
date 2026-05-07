import sys
import os
import requests

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QTextEdit, QLineEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt, QTimer

from ui_qt.settings_page import SettingsPage
from ui_qt.help_center_page import HelpCenterPage
from modules.ai_assistant import ask_ai


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class DriverDashboard(QMainWindow):
    def __init__(self, driver_name="Driver", driver_id=None):
        super().__init__()

        self.driver_name = driver_name
        self.driver_id = driver_id
        self.monitoring_on = True
        self.monitoring_window = None

        self.alerts_table = None
        self.alerts_timer = QTimer()
        self.alerts_timer.timeout.connect(self.refresh_alerts_table)

        self.setWindowTitle("CDMS - Driver Dashboard")
        self.resize(1200, 700)
        self.setMinimumSize(1050, 650)

        central = QWidget()
        self.setCentralWidget(central)

        self.setStyleSheet("""
            QWidget {
                background-color: #050b1a;
                color: white;
                font-family: Segoe UI;
            }
            QLabel { background: transparent; }
            QFrame#sidebar {
                background-color: #050b1a;
                border-right: 1px solid #16345c;
            }
            QLabel#logo {
                color: #18a0ff;
                font-size: 32px;
                font-weight: 900;
            }
            QPushButton#menuBtn {
                background: transparent;
                color: #cbd5e1;
                border: none;
                text-align: left;
                padding: 14px 20px;
                font-size: 15px;
            }
            QPushButton#menuBtn:hover {
                background-color: #0b1830;
                color: #18a0ff;
            }
            QPushButton#menuActive {
                background-color: #0b1830;
                color: #18a0ff;
                border-left: 4px solid #18a0ff;
                text-align: left;
                padding: 14px 20px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton#logoutBtn {
                background: transparent;
                color: #ef4444;
                border: none;
                text-align: left;
                padding: 14px 20px;
                font-size: 15px;
            }
            QLabel#pageTitle {
                color: white;
                font-size: 28px;
                font-weight: 900;
            }
            QLabel#activeStatus {
                color: #22c55e;
                font-size: 15px;
                font-weight: bold;
            }
            QFrame#card, QFrame#bigCard {
                background-color: #081226;
                border: 1px solid #1f70c1;
                border-radius: 14px;
            }
            QLabel#cardNumber {
                color: white;
                font-size: 28px;
                font-weight: 900;
            }
            QLabel#cardTitle {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#cardSub {
                color: #9aa7bd;
                font-size: 12px;
            }
            QLabel#sectionTitle {
                color: white;
                font-size: 21px;
                font-weight: bold;
            }
            QTableWidget {
                background-color: #081226;
                border: 1px solid #1f70c1;
                border-radius: 12px;
                gridline-color: #16345c;
                color: white;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #0b1830;
                color: #18a0ff;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
        """)

        main = QHBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        side = QVBoxLayout(sidebar)
        side.setContentsMargins(14, 25, 14, 25)
        side.setSpacing(12)

        logo_img = QLabel()
        logo_path = os.path.join(ASSETS_DIR, "logo.png")

        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_img.setPixmap(pix)
        else:
            logo_img.setText("🛡")
            logo_img.setStyleSheet("font-size:70px;color:#18a0ff;")

        logo_img.setAlignment(Qt.AlignCenter)

        logo = QLabel("CDMS")
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignCenter)

        side.addWidget(logo_img)
        side.addWidget(logo)
        side.addSpacing(20)

        dashboard_btn = QPushButton("🏠  Dashboard")
        dashboard_btn.setObjectName("menuActive")
        dashboard_btn.clicked.connect(self.show_dashboard_content)

        monitoring_btn = QPushButton("🎥  Monitoring")
        monitoring_btn.setObjectName("menuBtn")
        monitoring_btn.clicked.connect(self.open_monitoring)

        trips_btn = QPushButton("🗺️  Trips")
        trips_btn.setObjectName("menuBtn")
        trips_btn.clicked.connect(self.open_trips)

        alerts_btn = QPushButton("🔔  Alerts")
        alerts_btn.setObjectName("menuBtn")
        alerts_btn.clicked.connect(self.open_alerts)

        profile_btn = QPushButton("👤  Profile")
        profile_btn.setObjectName("menuBtn")
        profile_btn.clicked.connect(self.open_profile)

        settings_btn = QPushButton("⚙️  Settings")
        settings_btn.setObjectName("menuBtn")
        settings_btn.clicked.connect(self.open_settings)

        help_btn = QPushButton("❓  Help Center")
        help_btn.setObjectName("menuBtn")
        help_btn.clicked.connect(self.open_help_center)

        logout_btn = QPushButton("🚪  Logout")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self.logout)

        side.addWidget(dashboard_btn)
        side.addWidget(monitoring_btn)
        side.addWidget(trips_btn)
        side.addWidget(alerts_btn)
        side.addWidget(profile_btn)
        side.addWidget(settings_btn)
        side.addWidget(help_btn)
        side.addStretch()
        side.addWidget(logout_btn)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(25, 30, 18, 25)
        self.content_layout.setSpacing(16)

        self.chat_panel = QFrame()
        self.chat_panel.setObjectName("bigCard")
        self.chat_panel.setFixedWidth(280)

        right = QVBoxLayout(self.chat_panel)
        right.setContentsMargins(20, 22, 20, 22)
        right.setSpacing(12)

        chat_title = QLabel("🤖 Driver Assistant")
        chat_title.setStyleSheet("font-size:18px; font-weight:bold; color:#18a0ff;")

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.chat_box.setStyleSheet("""
            QTextEdit {
                background-color:#071426;
                border:1px solid #1f70c1;
                border-radius:10px;
                padding:10px;
                color:white;
                font-size:13px;
            }
        """)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message...")
        self.chat_input.setFixedHeight(38)
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background-color:#081226;
                border:1px solid #1f70c1;
                border-radius:8px;
                padding-left:10px;
                color:white;
            }
        """)

        send_btn = QPushButton("Send")
        send_btn.setFixedHeight(38)
        send_btn.setFixedWidth(58)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color:#0d6efd;
                border-radius:8px;
                color:white;
                font-weight:bold;
            }
        """)

        chat_row = QHBoxLayout()
        chat_row.addWidget(self.chat_input)
        chat_row.addWidget(send_btn)

        send_btn.clicked.connect(self.send_message)
        self.chat_input.returnPressed.connect(self.send_message)

        right.addWidget(chat_title)
        right.addWidget(self.chat_box, 1)
        right.addLayout(chat_row)

        main.addWidget(sidebar)
        main.addLayout(self.content_layout, 1)
        main.addWidget(self.chat_panel)

        self.show_dashboard_content()

    def clear_content_area(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
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

    def add_back_button(self):
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setFixedHeight(38)
        back_btn.setMaximumWidth(180)
        back_btn.clicked.connect(self.show_dashboard_content)
        back_btn.setStyleSheet("""
            QPushButton {
                background:#0d6efd;
                color:white;
                border:none;
                border-radius:10px;
                font-weight:bold;
                padding:8px 14px;
            }
            QPushButton:hover {
                background:#0b5ed7;
            }
        """)
        self.content_layout.addWidget(back_btn)

    def stop_alerts_refresh(self):
        self.alerts_timer.stop()
        self.alerts_table = None

    def show_dashboard_content(self):
        self.stop_alerts_refresh()
        self.clear_content_area()
        self.chat_panel.show()

        from database import get_dashboard_analytics

        today_trips, today_alerts, last_7_alerts, monthly_trips, top_route, safety_score = get_dashboard_analytics(self.driver_id)
        status_text = "ON" if self.monitoring_on else "OFF"

        header = QHBoxLayout()
        title = QLabel(f"Welcome, {self.driver_name}")
        title.setObjectName("pageTitle")

        self.status_label = QLabel("🟢 Active" if self.monitoring_on else "🔴 OFF")
        self.status_label.setObjectName("activeStatus")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status_label)
        self.content_layout.addLayout(header)

        route_row = QHBoxLayout()

        self.current_location_input = QLineEdit()
        self.current_location_input.setPlaceholderText("Current Location")

        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("Destination")

        detect_btn = QPushButton("📍 Detect")
        detect_btn.clicked.connect(self.detect_location)

        route_row.addWidget(self.current_location_input)
        route_row.addWidget(self.destination_input)
        route_row.addWidget(detect_btn)
        self.content_layout.addLayout(route_row)

        stats = QHBoxLayout()
        stats.setSpacing(14)
        stats.addWidget(self.stat_card("🛡️", f"{safety_score}%", "Safety Score", "Today", "#3b0f6f"))
        stats.addWidget(self.stat_card("🗺️", str(today_trips), "Trips", "Today", "#082f68"))
        stats.addWidget(self.stat_card("🚨", str(today_alerts), "Alerts", "Today", "#65350f"))
        stats.addWidget(self.stat_card("●", status_text, "Status", "Monitoring", "#064e3b"))
        self.content_layout.addLayout(stats)

        analytics_card = QFrame()
        analytics_card.setObjectName("bigCard")

        analytics_layout = QVBoxLayout(analytics_card)
        analytics_layout.setContentsMargins(20, 16, 20, 16)
        analytics_layout.setSpacing(16)

        analytics_title = QLabel("📊 Driver Safety Analytics")
        analytics_title.setObjectName("sectionTitle")
        analytics_layout.addWidget(analytics_title)

        row1 = QHBoxLayout()
        row1.setSpacing(14)

        row2 = QHBoxLayout()
        row2.setSpacing(14)

        def chart_box(title_text, value, subtitle, icon, percent=None, action=None):
            box = QFrame()
            box.setMinimumHeight(150)
            box.setStyleSheet("""
                QFrame {
                    background:#050b1a;
                    border:1px solid #1f70c1;
                    border-radius:14px;
                }
                QFrame:hover {
                    background:#0b1830;
                }
            """)

            layout = QVBoxLayout(box)
            layout.setContentsMargins(16, 14, 16, 14)
            layout.setSpacing(8)

            title_lbl = QLabel(f"{icon}  {title_text}")
            title_lbl.setStyleSheet("""
                QLabel {
                    color:#18a0ff;
                    font-size:13px;
                    font-weight:bold;
                    border:none;
                    background:transparent;
                }
            """)

            value_lbl = QLabel(str(value))
            value_lbl.setAlignment(Qt.AlignCenter)
            value_lbl.setWordWrap(True)
            value_lbl.setStyleSheet("""
                QLabel {
                    color:white;
                    font-size:24px;
                    font-weight:bold;
                    border:none;
                    background:transparent;
                }
            """)

            sub_lbl = QLabel(subtitle)
            sub_lbl.setAlignment(Qt.AlignCenter)
            sub_lbl.setWordWrap(True)
            sub_lbl.setStyleSheet("""
                QLabel {
                    color:#9aa7bd;
                    font-size:12px;
                    border:none;
                    background:transparent;
                }
            """)

            layout.addWidget(title_lbl)
            layout.addStretch()
            layout.addWidget(value_lbl)

            if percent is not None:
                bg = QFrame()
                bg.setFixedHeight(12)
                bg.setStyleSheet("""
                    QFrame {
                        background:#1e293b;
                        border:none;
                        border-radius:6px;
                    }
                """)

                fill = QFrame(bg)
                fill_width = max(8, int(230 * min(percent, 100) / 100))
                fill.setGeometry(0, 0, fill_width, 12)
                fill.setStyleSheet("""
                    QFrame {
                        background:#18a0ff;
                        border:none;
                        border-radius:6px;
                    }
                """)

                layout.addWidget(bg)

            layout.addWidget(sub_lbl)
            layout.addStretch()

            if action:
                box.setCursor(Qt.PointingHandCursor)
                box.mousePressEvent = lambda event: action()

            return box

        row1.addWidget(chart_box(
            "Driver Safety Scorecard",
            f"{safety_score}%",
            "Today safety score based on drowsiness alerts",
            "🛡️",
            safety_score,
            self.show_safety_score_details
        ))

        row1.addWidget(chart_box(
            "Daily Trips",
            today_trips,
            "Total trips recorded today",
            "🗺️",
            min(today_trips * 10, 100),
            self.show_daily_trips_details
        ))

        row1.addWidget(chart_box(
            "Last 7 Days Alerts Trend",
            last_7_alerts,
            "Drowsiness alerts in last 7 days",
            "📈",
            min(last_7_alerts * 10, 100),
            self.show_weekly_alerts_details
        ))

        row2.addWidget(chart_box(
            "Top Routes",
            top_route,
            "Most used route by this driver",
            "📍",
            80,
            self.show_top_route_details
        ))

        row2.addWidget(chart_box(
            "Drowsiness Alerts",
            today_alerts,
            "Today drowsiness alert count",
            "🚨",
            min(today_alerts * 15, 100),
            self.show_drowsiness_alerts_details
        ))

        row2.addWidget(chart_box(
            "Monthly Safety Overview",
            monthly_trips,
            "Trips completed this month",
            "📅",
            min(monthly_trips * 5, 100),
            self.show_monthly_overview_details
        ))

        analytics_layout.addLayout(row1)
        analytics_layout.addLayout(row2)

        self.content_layout.addWidget(analytics_card)
        self.update_status()

    def open_analytics_detail_page(self, title_text, cards):
        self.stop_alerts_refresh()
        self.clear_content_area()
        self.chat_panel.hide()
        self.add_back_button()

        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        self.content_layout.addWidget(title)

        container = QFrame()
        container.setObjectName("bigCard")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        for card_title, value, subtitle, percent in cards:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background:#050b1a;
                    border:1px solid #1f70c1;
                    border-radius:14px;
                }
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 16, 20, 16)
            card_layout.setSpacing(10)

            heading = QLabel(card_title)
            heading.setStyleSheet("color:#18a0ff;font-size:17px;font-weight:bold;border:none;")

            number = QLabel(str(value))
            number.setWordWrap(True)
            number.setStyleSheet("color:white;font-size:30px;font-weight:bold;border:none;")

            sub = QLabel(subtitle)
            sub.setWordWrap(True)
            sub.setStyleSheet("color:#9aa7bd;font-size:14px;border:none;")

            bar_bg = QFrame()
            bar_bg.setFixedHeight(14)
            bar_bg.setStyleSheet("background:#1e293b;border:none;border-radius:7px;")

            bar_fill = QFrame(bar_bg)
            bar_fill.setGeometry(0, 0, max(10, int(600 * min(percent, 100) / 100)), 14)
            bar_fill.setStyleSheet("background:#18a0ff;border:none;border-radius:7px;")

            card_layout.addWidget(heading)
            card_layout.addWidget(number)
            card_layout.addWidget(bar_bg)
            card_layout.addWidget(sub)

            layout.addWidget(card)

        layout.addStretch()
        self.content_layout.addWidget(container)

    def stat_card(self, icon, number, title_text, sub, color):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(110)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        icon_box = QLabel(icon)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setFixedSize(55, 55)
        icon_box.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 12px;
                font-size: 22px;
            }}
        """)

        texts = QVBoxLayout()
        texts.setSpacing(3)

        num = QLabel(number)
        num.setObjectName("cardNumber")

        ttl = QLabel(title_text)
        ttl.setObjectName("cardTitle")

        sb = QLabel(sub)
        sb.setObjectName("cardSub")

        texts.addWidget(num)
        texts.addWidget(ttl)
        texts.addWidget(sb)

        layout.addWidget(icon_box)
        layout.addLayout(texts)

        return card

    def show_safety_score_details(self):
        from database import get_dashboard_analytics

        today_trips, today_alerts, last_7_alerts, monthly_trips, top_route, safety_score = get_dashboard_analytics(self.driver_id)

        self.open_analytics_detail_page(
            "🛡️ Driver Safety Scorecard",
            [
                ("Safety Score", f"{safety_score}%", "Calculated from today's drowsiness alerts.", safety_score),
                ("Today Alerts", today_alerts, "Lower alerts means better safety score.", min(today_alerts * 15, 100)),
            ]
        )

    def show_daily_trips_details(self):
        from database import get_trips

        trips = get_trips(self.driver_id)
        completed = 0
        active = 0

        for trip in trips:
            status = trip[2]
            if status == "Completed":
                completed += 1
            elif status == "Active":
                active += 1

        total = len(trips)

        self.open_analytics_detail_page(
            "🗺️ Daily Trips Analytics",
            [
                ("Total Trips", total, "Total trips recorded for this driver.", min(total * 10, 100)),
                ("Completed Trips", completed, "Trips successfully completed.", min(completed * 10, 100)),
                ("Active Trips", active, "Trips currently active.", min(active * 10, 100)),
            ]
        )

    def show_weekly_alerts_details(self):
        from database import get_dashboard_analytics

        today_trips, today_alerts, last_7_alerts, monthly_trips, top_route, safety_score = get_dashboard_analytics(self.driver_id)

        self.open_analytics_detail_page(
            "📈 Last 7 Days Alerts Trend",
            [
                ("Last 7 Days Alerts", last_7_alerts, "Total drowsiness alerts in the last 7 days.", min(last_7_alerts * 10, 100)),
                ("Risk Level", "High" if last_7_alerts >= 5 else "Normal", "Risk depends on weekly alert count.", min(last_7_alerts * 10, 100)),
            ]
        )

    def show_top_route_details(self):
        from database import get_dashboard_analytics

        today_trips, today_alerts, last_7_alerts, monthly_trips, top_route, safety_score = get_dashboard_analytics(self.driver_id)

        self.open_analytics_detail_page(
            "📍 Top Routes",
            [
                ("Most Used Route", top_route, "Most frequent route from trip history.", 80),
            ]
        )

    def show_drowsiness_alerts_details(self):
        from database import get_alerts

        alerts = get_alerts(self.driver_id)
        total_alerts = len(alerts)

        self.open_analytics_detail_page(
            "🚨 Drowsiness Alerts Analytics",
            [
                ("Total Alerts", total_alerts, "Total alert records for this driver.", min(total_alerts * 10, 100)),
                ("Safety Advice", "Take Rest", "Frequent alerts mean the driver should rest more.", 70 if total_alerts else 20),
            ]
        )

    def show_monthly_overview_details(self):
        from database import get_monthly_profile_stats

        monthly_trips, monthly_alerts, safety_score = get_monthly_profile_stats(self.driver_id)

        self.open_analytics_detail_page(
            "📅 Monthly Safety Overview",
            [
                ("Monthly Trips", monthly_trips, "Trips completed this month.", min(monthly_trips * 5, 100)),
                ("Monthly Alerts", monthly_alerts, "Drowsiness alerts this month.", min(monthly_alerts * 10, 100)),
                ("Monthly Safety Score", f"{safety_score}%", "Monthly safety performance.", safety_score),
            ]
        )

    def open_trips(self):
        from database import get_trips

        self.stop_alerts_refresh()
        self.clear_content_area()
        self.chat_panel.hide()
        self.add_back_button()

        title = QLabel("🚗 Trip History")
        title.setObjectName("pageTitle")
        self.content_layout.addWidget(title)

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Route", "Status", "Date", "Start Time", "End Time", "Action"
        ])

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table.setColumnWidth(0, 420)
        table.setColumnWidth(1, 160)
        table.setColumnWidth(2, 160)
        table.setColumnWidth(3, 170)
        table.setColumnWidth(4, 170)
        table.setColumnWidth(5, 130)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)

        trips = get_trips(self.driver_id)
        table.setRowCount(len(trips))

        for row_index, trip in enumerate(trips):
            start, dest, status, date, start_time, end_time = trip

            values = [
                f"{start} → {dest}",
                status,
                date,
                start_time,
                end_time if end_time else "-",
                "View"
            ]

            for col_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                item.setToolTip(str(value))

                if col_index == 1:
                    if status == "Completed":
                        item.setForeground(QColor("#22c55e"))
                    elif status == "Active":
                        item.setForeground(QColor("#facc15"))
                    else:
                        item.setForeground(QColor("#ef4444"))

                table.setItem(row_index, col_index, item)

        self.content_layout.addWidget(table)

    def open_alerts(self):
        self.alerts_timer.stop()
        self.clear_content_area()
        self.chat_panel.hide()
        self.add_back_button()

        title = QLabel("🚨 Alerts History")
        title.setObjectName("pageTitle")
        self.content_layout.addWidget(title)

        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(4)
        self.alerts_table.setHorizontalHeaderLabels([
            "Driver", "Date", "Time", "Status"
        ])

        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alerts_table.verticalHeader().setVisible(False)
        self.alerts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alerts_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.content_layout.addWidget(self.alerts_table)

        self.refresh_alerts_table()
        self.alerts_timer.start(2000)

    def refresh_alerts_table(self):
        if self.alerts_table is None:
            return

        try:
            from database import get_alerts

            alerts = get_alerts(self.driver_id)
            self.alerts_table.setRowCount(len(alerts))

            for row_index, alert in enumerate(alerts):
                driver_name, date, time = alert

                values = [
                    driver_name,
                    date,
                    time,
                    "Drowsy Alert"
                ]

                for col_index, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)

                    if col_index == 3:
                        item.setForeground(QColor("#ef4444"))

                    self.alerts_table.setItem(row_index, col_index, item)

        except Exception:
            self.alerts_timer.stop()
            self.alerts_table = None

    def detect_location(self):
        try:
            response = requests.get("https://ipinfo.io/json", timeout=5)
            data = response.json()

            city = data.get("city", "")
            region = data.get("region", "")

            location = f"{city}, {region}".strip(", ")
            self.current_location_input.setText(location)

        except Exception:
            QMessageBox.warning(self, "Error", "Location detect failed")

    def open_monitoring(self):
        if self.driver_id is None:
            QMessageBox.warning(self, "Login Required", "Driver ID not found.")
            return

        try:
            from ui_qt.monitoring_window import MonitoringWindow

            self.stop_alerts_refresh()
            self.clear_content_area()
            self.chat_panel.hide()
            self.add_back_button()

            current_location = ""
            destination = ""

            if hasattr(self, "current_location_input"):
                try:
                    current_location = self.current_location_input.text()
                except RuntimeError:
                    current_location = ""

            if hasattr(self, "destination_input"):
                try:
                    destination = self.destination_input.text()
                except RuntimeError:
                    destination = ""

            self.monitoring_widget = MonitoringWindow(
                driver_id=int(self.driver_id),
                driver_name=self.driver_name,
                current_location=current_location,
                destination=destination
            )

            self.content_layout.addWidget(self.monitoring_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_monitoring_closed(self):
        self.monitoring_on = True
        self.update_status()

    def update_status(self):
        try:
            if not hasattr(self, "status_label"):
                return

            if self.monitoring_on:
                self.status_label.setText("🟢 Active")
                self.status_label.setStyleSheet("color:#22c55e;font-size:15px;font-weight:bold;")
            else:
                self.status_label.setText("🔴 OFF")
                self.status_label.setStyleSheet("color:#ef4444;font-size:15px;font-weight:bold;")

        except RuntimeError:
            return

    def logout(self):
        self.monitoring_on = False
        self.update_status()
        self.close()

        from ui_qt.home_window import HomeWindow

        self.home_window = HomeWindow()
        self.home_window.showMaximized()

    def send_message(self):
        user_text = self.chat_input.text().strip()

        if not user_text:
            return

        self.chat_box.append(f"""
        <div style='color:#18a0ff;margin:8px;'>
            <b>You:</b> {user_text}
        </div>
        """)

        self.chat_input.clear()

        self.chat_box.append(f"""
        <div style='color:#ffaa00;margin:8px;'>
            <b>Assistant:</b> Thinking...
        </div>
        """)

        reply = ask_ai(user_text)

        self.chat_box.append(f"""
        <div style='color:white;margin:8px;'>
            <b>Assistant:</b> {reply}
        </div>
        """)

    def open_profile(self):
        self.stop_alerts_refresh()
        self.clear_content_area()
        self.chat_panel.hide()
        self.add_back_button()

        from ui_qt.profile_page import ProfilePage

        page = ProfilePage(self.driver_id)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #050b1a;
            }
        """)

        self.content_layout.addWidget(scroll)

    def open_settings(self):
        self.stop_alerts_refresh()
        self.clear_content_area()
        self.chat_panel.hide()
        self.add_back_button()

        page = SettingsPage(self.driver_id, self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #050b1a;
            }
        """)

        self.content_layout.addWidget(scroll)

    def open_help_center(self):
        self.stop_alerts_refresh()
        self.clear_content_area()
        self.chat_panel.hide()
        self.add_back_button()

        page = HelpCenterPage()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #050b1a;
            }
        """)

        self.content_layout.addWidget(scroll)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DriverDashboard()
    window.showMaximized()
    sys.exit(app.exec())