from PySide6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QStackedWidget, QLineEdit
)
from PySide6.QtCore import Qt


class MonitoringManagementPage(QWidget):
    def __init__(self, monitoring_data):
        super().__init__()
        self.monitoring_data = monitoring_data
        self.current_tab = 0

        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(0, 0, 0, 0)
        self.main.setSpacing(14)
        self.main.setAlignment(Qt.AlignTop)

        tab_row = QHBoxLayout()
        tab_row.setSpacing(12)

        self.tab_buttons = []

        tabs = [
            ("📡 Live Monitoring", 0),
            ("🧾 Monitoring History", 1),
        ]

        for text, index in tabs:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(50)
            btn.setObjectName("menuActive" if index == 0 else "menuBtn")
            btn.clicked.connect(lambda checked=False, i=index, b=btn: self.change_tab(i, b))
            self.tab_buttons.append(btn)
            tab_row.addWidget(btn)

        self.main.addLayout(tab_row)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search monitoring session...")
        self.search_box.setFixedHeight(42)
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
        self.search_box.textChanged.connect(self.refresh_current_tab)
        self.main.addWidget(self.search_box)

        self.stack = QStackedWidget()

        self.live_table = self.create_table()
        self.history_table = self.create_table()

        self.stack.addWidget(self.live_table)
        self.stack.addWidget(self.history_table)

        self.main.addWidget(self.stack)

        self.load_all_tables()

    def create_table(self):
        table = QTableWidget()

        table.verticalHeader().setVisible(False)

        table.setSelectionBehavior(QTableWidget.SelectRows)

        table.setEditTriggers(QTableWidget.NoEditTriggers)

        table.horizontalHeader().setStretchLastSection(True)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        table.setMinimumHeight(500)

        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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
                padding:11px;
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

    def filter_rows(self, rows):
        keyword = self.search_box.text().strip().lower()

        if not keyword:
            return rows

        filtered = []
        for row in rows:
            row_text = " ".join(str(x).lower() for x in row)
            if keyword in row_text:
                filtered.append(row)

        return filtered

    def set_table_data(self, table, headers, rows):
        rows = self.filter_rows(rows)

        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            table.setRowHeight(r, 46)

            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                if str(value) == "Online":
                    item.setForeground(Qt.green)
                elif str(value) == "Offline":
                    item.setForeground(Qt.red)
                elif str(value) == "Running":
                    item.setForeground(Qt.green)

                table.setItem(r, c, item)

    def load_all_tables(self):
        self.load_live_table()
        self.load_history_table()

    def load_live_table(self):
        headers = ["Session ID", "Driver", "Date", "Start Time", "End Time", "Status"]

        rows = []
        for m in self.monitoring_data:
            if str(m[5]).lower() == "online":
                rows.append([m[0], m[1], m[2], m[3], m[4], m[5]])

        self.set_table_data(self.live_table, headers, rows)

    def load_history_table(self):
        headers = ["Session ID", "Driver", "Date", "Start Time", "End Time", "Status"]

        rows = []
        for m in self.monitoring_data:
            rows.append([m[0], m[1], m[2], m[3], m[4], m[5]])

        self.set_table_data(self.history_table, headers, rows)

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

        self.refresh_current_tab()

    def refresh_current_tab(self):
        if self.current_tab == 0:
            self.load_live_table()
        else:
            self.load_history_table()