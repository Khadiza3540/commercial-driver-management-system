from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt


class TripReportPage(QWidget):
    def __init__(self, driver_name, trips):
        super().__init__()

        self.driver_name = driver_name
        self.trips = trips

        self.setWindowTitle(f"Trip Summary - {driver_name}")
        self.showMaximized()

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
                font-size:20px;
                font-weight:900;
                color:#18a0ff;
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
        main.setContentsMargins(30, 24, 30, 24)
        main.setSpacing(16)

        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Driver Trip Summary")
        title.setObjectName("title")

        sub = QLabel(f"👤 {driver_name}  |  Individual trip performance overview")
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

        total = len(trips)
        active = len([t for t in trips if str(t[7]).lower() == "active"])
        completed = len([t for t in trips if str(t[7]).lower() == "completed"])
        failed = len([t for t in trips if str(t[7]).lower() in ["failed", "cancelled"]])
        not_set = len([t for t in trips if str(t[7]).lower() == "not set"])

        cards = QHBoxLayout()
        cards.setSpacing(14)

        cards.addWidget(self.stat_card("🛣", "Total Trips", total, "All records", "#1d4ed8"))
        cards.addWidget(self.stat_card("🚗", "Active", active, "Running now", "#0f766e"))
        cards.addWidget(self.stat_card("✅", "Completed", completed, "Finished trips", "#15803d"))
        cards.addWidget(self.stat_card("⚠️", "Failed / Cancelled", failed, "Problem trips", "#b91c1c"))
        cards.addWidget(self.stat_card("❔", "Not Set", not_set, "No status", "#ca8a04"))

        main.addLayout(cards)

        table_title = QLabel("Trip History")
        table_title.setObjectName("section")
        main.addWidget(table_title)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumHeight(360)

        self.table.setStyleSheet("""
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

        main.addWidget(self.table)
        self.load_table()

    def stat_card(self, icon, title, value, subtitle, color):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(105)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFixedSize(54, 54)
        icon_lbl.setStyleSheet(f"""
            QLabel {{
                background:{color};
                border-radius:14px;
                font-size:24px;
            }}
        """)

        text = QVBoxLayout()
        text.setSpacing(3)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size:12px;color:#cbd5e1;font-weight:bold;")

        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet("font-size:24px;color:white;font-weight:900;")

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("font-size:11px;color:#9aa7bd;")

        text.addWidget(title_lbl)
        text.addWidget(value_lbl)
        text.addWidget(sub_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text)
        layout.addStretch()

        return card

    def load_table(self):
        headers = ["Trip ID", "Start", "Destination", "Date", "Start Time", "End Time", "Status"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.trips))

        for r, t in enumerate(self.trips):
            trip_id, driver, start, destination, date, start_time, end_time, status = t

            row = [
                trip_id,
                start,
                destination,
                date,
                start_time,
                end_time if end_time else "Running",
                status
            ]

            self.table.setRowHeight(r, 44)

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

                self.table.setItem(r, c, item)