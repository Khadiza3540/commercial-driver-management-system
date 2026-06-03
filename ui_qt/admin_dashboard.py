import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QTableWidget,
    QTableWidgetItem, QStackedWidget, QMessageBox,
    QHeaderView, QGridLayout, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QFont

from ui_qt.driver_management_page import DriverManagementPage
from monitoring_management_page import MonitoringManagementPage
from ui_qt.trip_management_page import TripManagementPage
from database import get_all_trips_admin
from ui_qt.alert_management_page import AlertManagementPage
from database import get_all_alerts_admin
from settings_management_page import SettingsManagementPage
from toll_payment_management_page import TollPaymentManagementPage

from database import (
    get_admin_dashboard_stats,
    get_all_drivers_admin,
    get_all_trips_admin,
    get_all_alerts_admin,
    get_monitoring_sessions_admin,
    get_admin_report_summary
)


class DriverReportWindow(QWidget):
    def __init__(self, driver_data):
        super().__init__()

        self.setWindowTitle("Driver Safety Report")
        self.resize(900, 620)

        self.setStyleSheet("""
            QWidget { background:#050b1a; color:white; font-family:Segoe UI; }
            QFrame { background:#071426; border:1px solid #1683ff; border-radius:18px; }
            QLabel#title { font-size:28px; font-weight:900; color:#18a0ff; }
            QLabel#text { font-size:14px; color:#cbd5e1; }
            QPushButton {
                background:#0d6efd; color:white; border:none;
                border-radius:10px; padding:10px; font-weight:bold;
            }
        """)

        d = driver_data
        driver_id, name, username, email, license_no, phone, vehicle, status, authorized, trips, alerts = d

        safety_score = max(0, 100 - (int(alerts) * 5))

        if safety_score >= 80:
            risk = "Safe"
        elif safety_score >= 50:
            risk = "Moderate"
        elif safety_score >= 30:
            risk = "Risky"
        else:
            risk = "High Risk"

        main = QVBoxLayout(self)
        main.setContentsMargins(30, 30, 30, 30)

        card = QFrame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)

        title = QLabel(f"Driver Safety Report - {name}")
        title.setObjectName("title")

        info = QLabel(
            f"Driver ID: {driver_id}\n"
            f"Username: {username}\n"
            f"Email: {email}\n"
            f"License: {license_no}\n"
            f"Phone: {phone}\n"
            f"Vehicle No: {vehicle}\n"
            f"Profile Status: {status}\n"
            f"Authorized: {authorized}\n\n"
            f"Total Trips: {trips}\n"
            f"Total Alerts: {alerts}\n"
            f"Safety Score: {safety_score}%\n"
            f"Risk Level: {risk}\n\n"
            f"Recommendation:\n"
            f"{'This driver needs admin review and safety monitoring.' if safety_score < 50 else 'This driver is currently within acceptable safety range.'}"
        )
        info.setObjectName("text")

        close_btn = QPushButton("Close Report")
        close_btn.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()
        layout.addWidget(close_btn)

        main.addWidget(card)


class StatMiniChart(QFrame):
    def __init__(self, title, value, total, accent, chart_type="donut", sub=""):
        super().__init__()
        self.title = title
        self.value = int(value) if str(value).isdigit() else value
        self.total = max(1, int(total)) if str(total).isdigit() else 1
        self.accent = accent
        self.chart_type = chart_type
        self.sub = sub
        self.setObjectName("card")
        self.setMinimumHeight(230)
        self.setMaximumHeight(230)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        painter.setPen(QColor("#c4c9d8"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
        painter.drawText(20, 28, self.title)

        painter.setPen(QColor("#8f9bad"))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(20, 48, self.sub)

        if self.chart_type == "donut":
            size = min(w, h) - 82
            x = (w - size) // 2
            y = 58
            percent = max(0, min(100, int((int(self.value) / self.total) * 100)))

            pen_bg = QPen(QColor("#10284a"), 16)
            pen_bg.setCapStyle(Qt.RoundCap)
            painter.setPen(pen_bg)
            painter.drawArc(x, y, size, size, 0, 360 * 16)

            pen_fg = QPen(QColor(self.accent), 16)
            pen_fg.setCapStyle(Qt.RoundCap)
            painter.setPen(pen_fg)
            painter.drawArc(x, y, size, size, 90 * 16, -int(360 * 16 * percent / 100))

            painter.setPen(QColor("white"))
            painter.setFont(QFont("Segoe UI", 24, QFont.Bold))
            painter.drawText(x, y + size // 2 - 8, size, 35, Qt.AlignCenter, str(self.value))

            painter.setPen(QColor("#8f9bad"))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(x, y + size // 2 + 23, size, 25, Qt.AlignCenter, f"{percent}%")

        elif self.chart_type == "bar":
            max_value = max(1, self.total)
            bar_w = max(18, (w - 90) // 6)
            gap = 16
            base_y = h - 35
            start_x = 35
            values = [self.value, max(0, max_value - int(self.value)), self.value + 1, max(1, self.value // 2), self.value + 2]

            painter.setPen(QColor("#8f9bad"))
            painter.setFont(QFont("Segoe UI", 8))
            labels = ["Now", "Left", "Avg", "Low", "High"]

            for i, v in enumerate(values):
                bh = int((v / max(max(values), 1)) * 95)
                x = start_x + i * (bar_w + gap)
                painter.setBrush(QColor(self.accent))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(x, base_y - bh, bar_w, bh, 7, 7)
                painter.setPen(QColor("#8f9bad"))
                painter.drawText(x - 3, base_y + 16, bar_w + 10, 18, Qt.AlignCenter, labels[i])

            painter.setPen(QColor("white"))
            painter.setFont(QFont("Segoe UI", 22, QFont.Bold))
            painter.drawText(w - 95, 86, 75, 38, Qt.AlignRight, str(self.value))


class DriverRiskChart(QFrame):
    def __init__(self, drivers):
        super().__init__()
        self.drivers = drivers
        self.setObjectName("card")
        self.setMinimumHeight(270)
        self.setMaximumHeight(270)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 14, QFont.Bold))
        painter.drawText(22, 32, "Driver Safety Risk")

        painter.setPen(QColor("#8f9bad"))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(22, 52, "Based on alert count and safety score")

        safe = moderate = risky = high = 0
        for d in self.drivers:
            alerts = int(d[10])
            score = max(0, 100 - alerts * 5)
            if score >= 80:
                safe += 1
            elif score >= 50:
                moderate += 1
            elif score >= 30:
                risky += 1
            else:
                high += 1

        data = [
            ("Safe", safe, "#18a0ff"),
            ("Moderate", moderate, "#0d6efd"),
            ("Risky", risky, "#f59e0b"),
            ("High", high, "#ef4444"),
        ]

        total = max(1, sum(v for _, v, _ in data))
        x, y, size = 55, 75, 130
        start = 90 * 16

        for label, value, color in data:
            span = -int((value / total) * 360 * 16)
            painter.setBrush(QColor(color))
            painter.setPen(Qt.NoPen)
            painter.drawPie(x, y, size, size, start, span)
            start += span

        painter.setBrush(QColor("#071426"))
        painter.drawEllipse(x + 34, y + 34, size - 68, size - 68)

        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 22, QFont.Bold))
        painter.drawText(x, y + 48, size, 35, Qt.AlignCenter, str(total))
        painter.setPen(QColor("#8f9bad"))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(x, y + 78, size, 20, Qt.AlignCenter, "Drivers")

        lx = 230
        ly = 86
        for label, value, color in data:
            painter.setBrush(QColor(color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(lx, ly, 14, 14, 4, 4)
            painter.setPen(QColor("#c4c9d8"))
            painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
            painter.drawText(lx + 24, ly + 13, f"{label}: {value}")
            ly += 30


class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CDMS - Admin Dashboard")
        self.resize(1450, 850)
        self.setMinimumSize(1150, 700)

        self.setStyleSheet("""
            QWidget {
                background-color: #050b1a;
                color: white;
                font-family: Segoe UI;
            }

            QFrame#sidebar {
                background-color: #071426;
                border-right: 1px solid #1683ff;
            }

            QLabel#logo {
                color: #18a0ff;
                font-size: 28px;
                font-weight: 900;
            }

            QLabel#logoSub {
                color: #9aa7bd;
                font-size: 11px;
            }

            QPushButton#menuBtn {
                background-color: transparent;
                color: #c4c9d8;
                border: none;
                text-align: left;
                padding: 13px 18px;
                font-size: 14px;
                border-radius: 12px;
            }

            QPushButton#menuBtn:hover {
                background-color: #0d1f3a;
                color: #18a0ff;
            }

            QPushButton#menuActive {
                background-color: #0d1f3a;
                color: #18a0ff;
                border: 1px solid #18a0ff;
                text-align: left;
                padding: 13px 18px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 12px;
            }

            QPushButton#actionBtn {
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 10px;
                font-size: 12px;
                font-weight: bold;
            }

            QLabel#title {
                font-size: 30px;
                font-weight: 900;
                color: white;
            }

            QLabel#subTitle {
                font-size: 13px;
                color: #9aa7bd;
            }

            QFrame#card {
                background-color: #071426;
                border: 1px solid #1f70c1;
                border-radius: 18px;
            }

            QFrame#card:hover {
                border: 1px solid #18a0ff;
                background-color: #0a1b32;
            }

            QLabel#cardNumber {
                font-size: 24px;
                font-weight: 900;
                color: white;
            }

            QLabel#cardTitle {
                font-size: 13px;
                color: #c4c9d8;
                font-weight: bold;
            }

            QLabel#cardSub {
                font-size: 11px;
                color: #8f9bad;
            }

            QTableWidget {
                background-color: #081226;
                border: 1px solid #1f70c1;
                border-radius: 14px;
                gridline-color: #17365f;
                color: white;
                font-size: 13px;
                selection-background-color: #0d6efd;
                selection-color: white;
            }

            QHeaderView::section {
                background-color: #0d1f3a;
                color: white;
                padding: 11px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }

            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #10284a;
            }

            QLabel#pageTitle {
                font-size: 24px;
                font-weight: 900;
                color: white;
            }

            QLabel#pageSub {
                font-size: 13px;
                color: #9aa7bd;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(270)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 25, 18, 25)
        sidebar_layout.setSpacing(10)

        logo = QLabel("🛡  CDMS")
        logo.setObjectName("logo")
        logo.setStyleSheet("""
            background: transparent;
            color: #18a0ff;
            font-size: 28px;
            font-weight: 900;
        """)

        sub_logo = QLabel("Admin Management Panel")
        sub_logo.setObjectName("logoSub")
        sub_logo.setStyleSheet("""
            background: transparent;
            color: #9aa7bd;
            font-size: 11px;
        """)

        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(sub_logo)
        sidebar_layout.addSpacing(24)

        self.menu_buttons = []

        menu_items = [
            ("📊  Dashboard", 0),
            ("👥  Drivers", 1),
            ("📡  Monitoring", 2),
            ("🛣  Trips", 3),
            ("🚨  Alerts", 4),
            ("💳  Toll Payments", 5),
            ("⚙️  Settings", 6),
            ("🚪  Logout", 7),
        ]

        for text, index in menu_items:
            btn = QPushButton(text)
            btn.setObjectName("menuActive" if index == 0 else "menuBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, i=index, b=btn: self.change_page(i, b))
            self.menu_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        content = QVBoxLayout()
        content.setContentsMargins(24, 20, 24, 20)
        content.setSpacing(18)

        header_row = QHBoxLayout()

        title_box = QVBoxLayout()
        self.header_title = QLabel("Admin Dashboard")
        self.header_title.setObjectName("title")

        self.header_sub = QLabel("Centralized driver monitoring, safety reports, toll payments and analytics")
        self.header_sub.setObjectName("subTitle")

        title_box.addWidget(self.header_title)
        title_box.addWidget(self.header_sub)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setFixedSize(120, 40)
        refresh_btn.setObjectName("menuActive")
        refresh_btn.clicked.connect(self.refresh_dashboard)

        header_row.addLayout(title_box)
        header_row.addStretch()
        header_row.addWidget(refresh_btn)

        content.addLayout(header_row)

        self.pages = QStackedWidget()
        self.pages.setMinimumWidth(0)
        self.pages.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)

        self.drivers = get_all_drivers_admin()
        self.trips_data = get_all_trips_admin()
        self.alerts_data = get_all_alerts_admin()
        self.monitoring_data = get_monitoring_sessions_admin()

        self.pages.addWidget(self.create_dashboard_page())
        self.pages.addWidget(DriverManagementPage(self.drivers))
        self.pages.addWidget(MonitoringManagementPage(self.monitoring_data))
        self.pages.addWidget(TripManagementPage(get_all_trips_admin()))
        self.pages.addWidget(AlertManagementPage(get_all_alerts_admin()))
        self.pages.addWidget(TollPaymentManagementPage())
        self.pages.addWidget(SettingsManagementPage())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)

        scroll.setStyleSheet("""
            QScrollArea {
                background:#050b1a;
                border:none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: rgba(24, 160, 255, 90);
                border-radius: 4px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #18a0ff;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            QScrollBar:horizontal {
                height:0px;
                background:transparent;
            }
            QScrollBar::handle:horizontal {
                background:transparent;
            }
        """)

        scroll.setWidget(self.pages)
        content.addWidget(scroll)

        main_layout.addWidget(sidebar)
        main_layout.addLayout(content)

    def create_card(self, icon, title, value, sub, accent):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(115)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(54, 54)
        icon_label.setStyleSheet(f"""
            background-color: {accent};
            border-radius: 14px;
            font-size: 23px;
        """)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)

        num = QLabel(str(value))
        num.setObjectName("cardNumber")

        lbl = QLabel(title)
        lbl.setObjectName("cardTitle")

        sub_lbl = QLabel(sub)
        sub_lbl.setObjectName("cardSub")

        text_box.addWidget(num)
        text_box.addWidget(lbl)
        text_box.addWidget(sub_lbl)

        layout.addWidget(icon_label)
        layout.addLayout(text_box)
        layout.addStretch()

        return card

    def create_table(self, headers, rows):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setMinimumHeight(330)

        for row, data in enumerate(rows):
            table.setRowHeight(row, 42)
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, item)

        return table

    def create_table_page(self, title, subtitle, headers, rows):
        page = QWidget()
        page.setMinimumWidth(0)
        page.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(14)

        page_title = QLabel(title)
        page_title.setObjectName("pageTitle")

        page_sub = QLabel(subtitle)
        page_sub.setObjectName("pageSub")

        table = self.create_table(headers, rows)

        layout.addWidget(page_title)
        layout.addWidget(page_sub)
        layout.addWidget(table)

        return page

    def create_dashboard_page(self):
        page = QWidget()
        page.setMinimumWidth(0)
        page.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        page.setStyleSheet("background:#050b1a;")

        layout = QVBoxLayout(page)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 12, 0)

        total_drivers, active_drivers, running_trips, today_alerts, safety_score, online_monitoring = get_admin_dashboard_stats()

        pending = len([d for d in self.drivers if str(d[7]).lower() == "pending"])
        disabled = len([d for d in self.drivers if str(d[7]).lower() == "disabled"])
        total_alerts = len(self.alerts_data)

        graph_grid = QGridLayout()
        graph_grid.setSpacing(10)

        graph_grid.addWidget(
            StatMiniChart("Drivers", total_drivers, max(total_drivers, 1), "#18a0ff", "donut", "Total driver profiles"),
            0, 0
        )
        graph_grid.addWidget(
            StatMiniChart("Active Drivers", active_drivers, max(total_drivers, 1), "#0d6efd", "donut", "Approved drivers"),
            0, 1
        )
        graph_grid.addWidget(
            StatMiniChart("Online Monitoring", online_monitoring, max(total_drivers, 1), "#6d28d9", "donut", "Live sessions"),
            0, 2
        )

        graph_grid.addWidget(
            StatMiniChart("Pending Drivers", pending, max(total_drivers, 1), "#f59e0b", "bar", "Waiting for approval"),
            1, 0
        )
        graph_grid.addWidget(
            StatMiniChart("Trips Overview", running_trips, max(running_trips + 3, 5), "#18a0ff", "bar", "Driver trip activity"),
            1, 1
        )
        graph_grid.addWidget(
            StatMiniChart("Safety Alerts", total_alerts, max(total_alerts + 3, 5), "#ef4444", "bar", "All warning events"),
            1, 2
        )

        layout.addLayout(graph_grid)

        bottom_grid = QGridLayout()
        bottom_grid.setSpacing(10)

        bottom_grid.addWidget(DriverRiskChart(self.drivers), 0, 0, 1, 2)
        bottom_grid.addWidget(
            StatMiniChart("Disabled Drivers", disabled, max(total_drivers, 1), "#082f68", "donut", "Blocked profiles"),
            0, 2
        )

        layout.addLayout(bottom_grid)
        layout.addStretch()

        return page

    def create_safety_reports_page(self):
        rows = []
        for d in self.drivers:
            alerts = int(d[10])
            score = max(0, 100 - alerts * 5)

            if score >= 80:
                risk = "Safe"
            elif score >= 50:
                risk = "Moderate"
            elif score >= 30:
                risk = "Risky"
            else:
                risk = "High Risk"

            rows.append([d[0], d[1], d[6], d[9], alerts, f"{score}%", risk, d[7]])

        return self.create_table_page(
            "Safety Reports",
            "Driver-wise safety score, alert count and risk level.",
            ["ID", "Driver", "Vehicle", "Trips", "Alerts", "Safety Score", "Risk Level", "Status"],
            rows
        )

    def create_toll_payments_page(self):
        rows = [
            ["TP-001", "Demo Driver", "Dhaka Toll Plaza", "250", "Pending", "Trip Based"],
            ["TP-002", "Demo Driver", "Expressway Toll", "180", "Paid", "Cash"],
        ]

        return self.create_table_page(
            "Toll Payments",
            "Toll payment history for driver trips. This module is mainly driver-side, admin can review all toll records.",
            ["Payment ID", "Driver", "Toll Location", "Amount", "Status", "Method"],
            rows
        )

    def create_analytics_page(self):
        page = QWidget()
        page.setMinimumWidth(0)
        page.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(14)

        title = QLabel("Driver Analytics")
        title.setObjectName("pageTitle")

        sub = QLabel("Click a driver row and press View Selected Driver Report to open individual safety analytics.")
        sub.setObjectName("pageSub")

        self.analytics_table = self.create_table(
            ["ID", "Name", "Vehicle", "Trips", "Alerts", "Safety Score", "Risk Level", "Status"],
            self.get_analytics_rows()
        )

        btn = QPushButton("📈 View Selected Driver Report")
        btn.setObjectName("menuActive")
        btn.setFixedHeight(42)
        btn.clicked.connect(self.open_selected_driver_report)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addWidget(self.analytics_table)
        layout.addWidget(btn)

        return page

    def get_analytics_rows(self):
        rows = []
        for d in self.drivers:
            alerts = int(d[10])
            score = max(0, 100 - alerts * 5)

            if score >= 80:
                risk = "Safe"
            elif score >= 50:
                risk = "Moderate"
            elif score >= 30:
                risk = "Risky"
            else:
                risk = "High Risk"

            rows.append([d[0], d[1], d[6], d[9], alerts, f"{score}%", risk, d[7]])
        return rows

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(26)

        title = QLabel("Settings")
        title.setObjectName("pageTitle")

        sub = QLabel("System configuration options for admin control.")
        sub.setObjectName("pageSub")

        settings_card = QFrame()
        settings_card.setObjectName("card")
        settings_card.setMinimumHeight(300)

        card_layout = QVBoxLayout(settings_card)
        card_layout.setContentsMargins(25, 22, 25, 22)

        text = QLabel(
            "⚙️ Camera Settings\n\n"
            "🚨 Safety Threshold: 30%\n\n"
            "📧 Email Alert: Enabled\n\n"
            "⛔ Auto Disable Low Safety Driver: Planned\n\n"
            "🎨 Theme: Dark Blue\n\n"
            "🔐 Role-Based Access Control: Admin / Driver"
        )
        text.setStyleSheet("color:#c4c9d8;font-size:15px;line-height:2;")

        card_layout.addWidget(text)
        card_layout.addStretch()

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addWidget(settings_card)
        layout.addStretch()

        return page

    def open_selected_driver_report(self):
        row = self.analytics_table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Select Driver", "Please select a driver from the analytics table.")
            return

        driver_id = int(self.analytics_table.item(row, 0).text())

        selected_driver = None
        for d in self.drivers:
            if int(d[0]) == driver_id:
                selected_driver = d
                break

        if selected_driver is None:
            QMessageBox.warning(self, "Error", "Driver not found.")
            return

        self.report_window = DriverReportWindow(selected_driver)
        self.report_window.showMaximized()

    def change_page(self, index, clicked_btn):
        if "Logout" in clicked_btn.text():
            self.logout()
            return

        self.pages.setCurrentIndex(index)
        self.header_title.show()
        self.header_sub.show()
        page_titles = {
            0: ("Admin Dashboard", "Centralized driver monitoring system."),
            1: ("Driver Management", "Manage pending, active, disabled drivers and safety-risk profiles."),
            2: ("Monitoring Management", "View current online monitoring sessions and previous monitoring history."),
            3: ("Trip Management", "Track active and completed trips with route and timing details."),
            4: ("Alert Management", "Monitor all drowsiness alerts, warning history and risky driving events."),
            5: ("Toll Payments", "Review driver toll payment history."),
            6: ("Settings", "System configuration options for admin control.")
        }

        if index in page_titles:
            self.header_title.setText(page_titles[index][0])
            self.header_sub.setText(page_titles[index][1])

        for btn in self.menu_buttons:
            btn.setObjectName("menuBtn")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        clicked_btn.setObjectName("menuActive")
        clicked_btn.style().unpolish(clicked_btn)
        clicked_btn.style().polish(clicked_btn)

    def refresh_dashboard(self):
        self.new_dashboard = AdminDashboard()
        self.new_dashboard.showMaximized()
        self.close()

    def logout(self):
        from ui_qt.home_window import HomeWindow

        self.home_window = HomeWindow()
        self.home_window.showMaximized()

        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = AdminDashboard()
    window.showMaximized()

    sys.exit(app.exec())