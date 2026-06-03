from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QComboBox, QPushButton, QStackedWidget
)
from PySide6.QtCore import Qt
from ui_qt.trip_report_page import TripReportPage


class TripManagementPage(QWidget):
    def __init__(self, trips):
        super().__init__()
        self.trips = trips
        self.current_tab = 0

        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(0, 0, 0, 0)
        self.main.setSpacing(14)
        self.main.setAlignment(Qt.AlignTop)

        self.search_box = QLineEdit()
        self.status_filter = QComboBox()
        self.tab_buttons = []

        self.all_trip_table = self.create_table()
        self.summary_table = self.create_table()
        self.active_table = self.create_table()
        self.completed_table = self.create_table()
        self.failed_table = self.create_table()

        self.stack = QStackedWidget()

        self.build_ui()
        self.refresh_page()

    def build_ui(self):
        cards = QGridLayout()
        cards.setSpacing(14)

        self.total_card = self.stat_card("🛣", "Today Trips", "0", "Today only")
        self.active_card = self.stat_card("🚗", "Today Active", "0", "Currently running")
        self.completed_card = self.stat_card("✅", "Today Completed", "0", "Finished today")
        self.failed_card = self.stat_card("⚠️", "Today Failed", "0", "Problem today")

        cards.addWidget(self.total_card, 0, 0)
        cards.addWidget(self.active_card, 0, 1)
        cards.addWidget(self.completed_card, 0, 2)
        cards.addWidget(self.failed_card, 0, 3)

        self.main.addLayout(cards)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self.search_box.setPlaceholderText("Search by driver, start location or destination...")
        self.search_box.setFixedHeight(42)
        self.search_box.textChanged.connect(self.refresh_page)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background:#071426;
                border:1px solid #1f70c1;
                border-radius:12px;
                color:white;
                padding:0 14px;
                font-size:13px;
            }
            QLineEdit:focus {
                border:1px solid #18a0ff;
            }
        """)

        self.status_filter.addItems(["All Status", "Active", "Completed", "Failed", "Cancelled", "Not Set"])
        self.status_filter.setFixedHeight(42)
        self.status_filter.currentTextChanged.connect(self.refresh_page)
        self.status_filter.setStyleSheet("""
            QComboBox {
                background:#071426;
                border:1px solid #1f70c1;
                border-radius:12px;
                color:white;
                padding:0 14px;
                font-size:13px;
            }
            QComboBox::drop-down {
                border:none;
            }
        """)

        filter_row.addWidget(self.search_box, 3)
        filter_row.addWidget(self.status_filter, 1)

        self.main.addLayout(filter_row)

        tab_row = QHBoxLayout()
        tab_row.setSpacing(12)

        tabs = [
            ("📋 All Trips", 0),
            ("👤 Driver Summary", 1),
            ("🚗 Active Trips", 2),
            ("✅ Completed Trips", 3),
            ("⚠️ Failed Trips", 4),
        ]

        for text, index in tabs:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(46)
            btn.setObjectName("menuActive" if index == 0 else "menuBtn")
            btn.clicked.connect(lambda checked=False, i=index, b=btn: self.change_tab(i, b))
            self.tab_buttons.append(btn)
            tab_row.addWidget(btn)

        self.main.addLayout(tab_row)

        self.summary_table.cellDoubleClicked.connect(self.open_driver_trip_report)

        self.stack.addWidget(self.all_trip_table)
        self.stack.addWidget(self.summary_table)
        self.stack.addWidget(self.active_table)
        self.stack.addWidget(self.completed_table)
        self.stack.addWidget(self.failed_table)

        self.main.addWidget(self.stack)

    def stat_card(self, icon, title, value, subtitle):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(105)
        card.setMaximumHeight(120)
        card.setStyleSheet("""
            QFrame#card {
                background:#071426;
                border:1px solid #1f70c1;
                border-radius:16px;
            }
            QLabel {
                background:transparent;
            }
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFixedSize(58, 58)
        icon_lbl.setStyleSheet("""
            QLabel {
                background:#0d1f3a;
                border-radius:15px;
                font-size:26px;
            }
        """)

        text = QVBoxLayout()
        text.setSpacing(3)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size:13px;color:#cbd5e1;font-weight:bold;background:transparent;")

        value_lbl = QLabel(value)
        value_lbl.setObjectName("value")
        value_lbl.setStyleSheet("font-size:26px;color:white;font-weight:900;background:transparent;")

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("font-size:12px;color:#9aa7bd;background:transparent;")

        text.addWidget(title_lbl)
        text.addWidget(value_lbl)
        text.addWidget(sub_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text)
        layout.addStretch()

        return card

    def create_table(self):
        table = QTableWidget()
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setMinimumHeight(520)

        table.setStyleSheet("""
            QTableWidget {
                background-color:#081226;
                border:1px solid #1f70c1;
                border-radius:14px;
                gridline-color:#17365f;
                color:white;
                font-size:13px;
                selection-background-color:#0d6efd;
            }
            QHeaderView::section {
                background-color:#0d1f3a;
                color:white;
                padding:10px;
                border:none;
                font-weight:bold;
                font-size:13px;
            }
            QTableWidget::item {
                padding:8px;
                border-bottom:1px solid #10284a;
            }
        """)
        return table

    def normalize_trip(self, trip):
        trip_id, driver, start, destination, date, start_time, end_time, status = trip

        return (
            trip_id,
            driver or "Unknown Driver",
            start or "Not provided",
            destination or "Not provided",
            date or "Not provided",
            start_time or "Not provided",
            end_time or "",
            status or "Not Set"
        )

    def filtered_trips(self):
        keyword = self.search_box.text().strip().lower()
        status_filter = self.status_filter.currentText().lower()

        result = []

        for trip in self.trips:
            t = self.normalize_trip(trip)

            trip_id, driver, start, destination, date, start_time, end_time, status = t
            searchable = f"{trip_id} {driver} {start} {destination} {date} {status}".lower()

            if keyword and keyword not in searchable:
                continue

            if status_filter != "all status" and status.lower() != status_filter:
                continue

            result.append(t)

        return result

    def today_trips(self, trips):
        today = datetime.now().strftime("%d-%m-%Y")
        return [t for t in trips if str(t[4]) == today]

    def refresh_page(self):
        trips = self.filtered_trips()
        today_trips = self.today_trips(trips)

        total = len(today_trips)
        active = len([t for t in today_trips if str(t[7]).lower() == "active"])
        completed = len([t for t in today_trips if str(t[7]).lower() == "completed"])
        failed = len([t for t in today_trips if str(t[7]).lower() in ["failed", "cancelled"]])

        self.set_card_value(self.total_card, total)
        self.set_card_value(self.active_card, active)
        self.set_card_value(self.completed_card, completed)
        self.set_card_value(self.failed_card, failed)

        self.load_all_trip_table(trips)
        self.load_summary_table(trips)
        self.load_active_table(trips)
        self.load_completed_table(trips)
        self.load_failed_table(trips)

    def set_card_value(self, card, value):
        label = card.findChild(QLabel, "value")
        if label:
            label.setText(str(value))

    def load_all_trip_table(self, trips):
        rows = []

        for t in trips:
            trip_id, driver, start, destination, date, start_time, end_time, status = t
            duration = "Running" if str(status).lower() == "active" else "Completed"

            rows.append([
                trip_id, driver, start, destination, date,
                start_time, end_time if end_time else "Running",
                duration, status
            ])

        self.set_table_data(
            self.all_trip_table,
            ["Trip ID", "Driver", "Start", "Destination", "Date", "Start Time", "End Time", "Duration", "Status"],
            rows
        )

    def load_summary_table(self, trips):
        summary = {}

        for t in trips:
            _, driver, _, _, _, _, _, status = t
            status_l = str(status).lower()

            if driver not in summary:
                summary[driver] = {
                    "total": 0,
                    "active": 0,
                    "completed": 0,
                    "failed": 0,
                    "not_set": 0,
                    "last": status
                }

            summary[driver]["total"] += 1
            summary[driver]["last"] = status

            if status_l == "active":
                summary[driver]["active"] += 1
            elif status_l == "completed":
                summary[driver]["completed"] += 1
            elif status_l in ["failed", "cancelled"]:
                summary[driver]["failed"] += 1
            else:
                summary[driver]["not_set"] += 1

        rows = []
        for driver, data in summary.items():
            rows.append([
                driver,
                data["total"],
                data["active"],
                data["completed"],
                data["failed"],
                data["not_set"],
                data["last"],
                "View Summary"
            ])

        self.set_table_data(
            self.summary_table,
            ["Driver", "Total Trips", "Active", "Completed", "Failed / Cancelled", "Not Set", "Last Status", "View Summary"],
            rows
        )

    def load_active_table(self, trips):
        rows = []

        for t in trips:
            if str(t[7]).lower() == "active":
                trip_id, driver, start, destination, date, start_time, end_time, status = t
                rows.append([trip_id, driver, start, destination, date, start_time, end_time if end_time else "Running", status])

        self.set_table_data(
            self.active_table,
            ["Trip ID", "Driver", "Start", "Destination", "Date", "Start Time", "End Time", "Status"],
            rows
        )

    def load_completed_table(self, trips):
        rows = []

        for t in trips:
            if str(t[7]).lower() == "completed":
                trip_id, driver, start, destination, date, start_time, end_time, status = t
                rows.append([trip_id, driver, start, destination, date, start_time, end_time if end_time else "Not provided", status])

        self.set_table_data(
            self.completed_table,
            ["Trip ID", "Driver", "Start", "Destination", "Date", "Start Time", "End Time", "Status"],
            rows
        )

    def load_failed_table(self, trips):
        rows = []

        for t in trips:
            if str(t[7]).lower() in ["failed", "cancelled"]:
                trip_id, driver, start, destination, date, start_time, end_time, status = t
                rows.append([trip_id, driver, start, destination, date, start_time, end_time if end_time else "Not provided", status])

        self.set_table_data(
            self.failed_table,
            ["Trip ID", "Driver", "Start", "Destination", "Date", "Start Time", "End Time", "Status"],
            rows
        )

    def open_driver_trip_report(self, row, col):
        if self.current_tab != 1:
            return

        if col != 7:
            return

        driver_name = self.summary_table.item(row, 0).text()

        driver_trips = [
            t for t in self.filtered_trips()
            if str(t[1]) == driver_name
        ]

        self.trip_report_window = TripReportPage(driver_name, driver_trips)
        self.trip_report_window.show()

    def change_tab(self, index, clicked_btn):
        self.current_tab = index
        self.stack.setCurrentIndex(index)

        for btn in self.tab_buttons:
            btn.setObjectName("menuBtn")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        clicked_btn.setObjectName("menuActive")
        clicked_btn.style().unpolish(clicked_btn)
        clicked_btn.style().polish(clicked_btn)

    def set_table_data(self, table, headers, rows):
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            table.setRowHeight(r, 44)

            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                if str(value) == "Active":
                    item.setForeground(Qt.cyan)
                elif str(value) == "Completed":
                    item.setForeground(Qt.green)
                elif str(value) in ["Failed", "Cancelled"]:
                    item.setForeground(Qt.red)
                elif str(value) == "Not Set":
                    item.setForeground(Qt.yellow)

                table.setItem(r, c, item)