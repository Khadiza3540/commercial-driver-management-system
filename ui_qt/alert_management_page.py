from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QComboBox, QPushButton, QStackedWidget,
    QMessageBox
)
from PySide6.QtCore import Qt

from database import get_driver_report_by_name
from ui_qt.driver_report_page import DriverReportPage


class AlertManagementPage(QWidget):
    def __init__(self, alerts):
        super().__init__()

        self.alerts = alerts
        self.report_windows = []

        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(0, 0, 0, 0)
        self.main.setSpacing(14)
        self.main.setAlignment(Qt.AlignTop)

        self.search_box = QLineEdit()
        self.severity_filter = QComboBox()

        self.tab_buttons = []

        self.all_table = self.create_table()
        self.today_table = self.create_table()
        self.high_risk_table = self.create_table()
        self.drowsiness_table = self.create_table()

        self.stack = QStackedWidget()

        self.build_ui()
        self.refresh_page()

    # ================= UI =================

    def build_ui(self):
        cards = QGridLayout()
        cards.setSpacing(14)

        self.total_card = self.stat_card("🚨", "Total Alerts", "0", "All alert records")
        self.today_card = self.stat_card("📅", "Today Alerts", "0", "Today only")
        self.drowsy_card = self.stat_card("😴", "Drowsiness", "0", "Primary alert")
        self.high_card = self.stat_card("⚠️", "High Risk", "0", "Dangerous alerts")

        cards.addWidget(self.total_card, 0, 0)
        cards.addWidget(self.today_card, 0, 1)
        cards.addWidget(self.drowsy_card, 0, 2)
        cards.addWidget(self.high_card, 0, 3)

        self.main.addLayout(cards)

        # ================= FILTER =================

        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self.search_box.setPlaceholderText(
            "Search by driver, severity or date..."
        )
        self.search_box.setFixedHeight(42)
        self.search_box.textChanged.connect(self.refresh_page)
        self.search_box.setStyleSheet(self.input_style())

        self.severity_filter.addItems([
            "All Severity",
            "Drowsiness",
            "High",
            "Moderate",
            "Low"
        ])

        self.severity_filter.setFixedHeight(42)
        self.severity_filter.currentTextChanged.connect(self.refresh_page)
        self.severity_filter.setStyleSheet(self.input_style())

        filter_row.addWidget(self.search_box, 3)
        filter_row.addWidget(self.severity_filter, 1)

        self.main.addLayout(filter_row)

        # ================= TABS =================

        tab_row = QHBoxLayout()
        tab_row.setSpacing(12)

        tabs = [
            ("📋 All Alerts", 0),
            ("📅 Today", 1),
            ("⚠️ High Risk", 2),
            ("😴 Drowsiness", 3),
        ]

        for text, index in tabs:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(46)

            if index == 0:
                btn.setStyleSheet(self.active_btn_style())
            else:
                btn.setStyleSheet(self.normal_btn_style())

            btn.clicked.connect(
                lambda checked=False, i=index, b=btn:
                self.change_tab(i, b)
            )

            self.tab_buttons.append(btn)
            tab_row.addWidget(btn)

        self.main.addLayout(tab_row)

        # ================= STACK =================

        self.stack.addWidget(self.all_table)
        self.stack.addWidget(self.today_table)
        self.stack.addWidget(self.high_risk_table)
        self.stack.addWidget(self.drowsiness_table)

        self.main.addWidget(self.stack)

    # ================= STYLE =================

    def input_style(self):
        return """
            QLineEdit, QComboBox {
                background:#071426;
                border:1px solid #1f70c1;
                border-radius:12px;
                color:white;
                padding:0 14px;
                font-size:13px;
            }

            QLineEdit:focus, QComboBox:focus {
                border:1px solid #18a0ff;
            }

            QComboBox::drop-down {
                border:none;
            }
        """

    def active_btn_style(self):
        return """
            QPushButton {
                background:#0d6efd;
                color:white;
                border:none;
                border-radius:12px;
                font-size:13px;
                font-weight:bold;
            }
        """

    def normal_btn_style(self):
        return """
            QPushButton {
                background:#071426;
                color:#cbd5e1;
                border:1px solid #1f70c1;
                border-radius:12px;
                font-size:13px;
                font-weight:bold;
            }

            QPushButton:hover {
                background:#0d1f3a;
            }
        """

    # ================= CARD =================

    def stat_card(self, icon, title, value, subtitle):
        card = QFrame()
        card.setObjectName("card")

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
        title_lbl.setStyleSheet("""
            font-size:13px;
            color:#cbd5e1;
            font-weight:bold;
        """)

        value_lbl = QLabel(value)
        value_lbl.setObjectName("value")

        value_lbl.setStyleSheet("""
            font-size:26px;
            color:white;
            font-weight:900;
        """)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("""
            font-size:12px;
            color:#9aa7bd;
        """)

        text.addWidget(title_lbl)
        text.addWidget(value_lbl)
        text.addWidget(sub_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text)
        layout.addStretch()

        return card

    # ================= TABLE =================

    def create_table(self):
        table = QTableWidget()

        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        table.setMinimumHeight(520)

        table.cellDoubleClicked.connect(
            lambda row, col, t=table: self.open_report(t, row)
        )

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

    # ================= DATA =================

    def normalize_alert(self, alert):
        alert_id, driver, severity, date, time, session = alert

        return (
            alert_id,
            driver or "Unknown Driver",
            severity or "Drowsiness",
            date or "Not provided",
            time or "Not provided",
            "View Report"
        )

    def filtered_alerts(self):
        keyword = self.search_box.text().strip().lower()
        severity_filter = self.severity_filter.currentText().lower()

        result = []

        for alert in self.alerts:
            a = self.normalize_alert(alert)

            alert_id, driver, severity, date, time, action = a

            searchable = f"""
                {alert_id}
                {driver}
                {severity}
                {date}
                {time}
            """.lower()

            if keyword and keyword not in searchable:
                continue

            if severity_filter != "all severity":
                if severity.lower() != severity_filter:
                    continue

            result.append(a)

        return result

    def today_alerts(self, alerts):
        today = datetime.now().strftime("%d-%m-%Y")

        return [
            a for a in alerts
            if str(a[3]) == today
        ]

    # ================= REFRESH =================

    def refresh_page(self):
        alerts = self.filtered_alerts()

        today_alerts = self.today_alerts(alerts)

        total = len(alerts)

        today = len(today_alerts)

        drowsy = len([
            a for a in alerts
            if str(a[2]).lower() == "drowsiness"
        ])

        high = len([
            a for a in alerts
            if str(a[2]).lower() in [
                "high",
                "critical",
                "high risk"
            ]
        ])

        self.set_card_value(self.total_card, total)
        self.set_card_value(self.today_card, today)
        self.set_card_value(self.drowsy_card, drowsy)
        self.set_card_value(self.high_card, high)

        self.load_all_table(alerts)
        self.load_today_table(alerts)
        self.load_high_risk_table(alerts)
        self.load_drowsiness_table(alerts)

    def set_card_value(self, card, value):
        label = card.findChild(QLabel, "value")

        if label:
            label.setText(str(value))

    # ================= TABLE LOAD =================

    def load_all_table(self, alerts):
        self.set_table_data(self.all_table, alerts)

    def load_today_table(self, alerts):
        self.set_table_data(
            self.today_table,
            self.today_alerts(alerts)
        )

    def load_high_risk_table(self, alerts):
        rows = [
            a for a in alerts
            if str(a[2]).lower() in [
                "high",
                "critical",
                "high risk"
            ]
        ]

        self.set_table_data(
            self.high_risk_table,
            rows
        )

    def load_drowsiness_table(self, alerts):
        rows = [
            a for a in alerts
            if str(a[2]).lower() == "drowsiness"
        ]

        self.set_table_data(
            self.drowsiness_table,
            rows
        )

    # ================= TAB =================

    def change_tab(self, index, clicked_btn):
        self.stack.setCurrentIndex(index)

        for btn in self.tab_buttons:
            btn.setStyleSheet(self.normal_btn_style())

        clicked_btn.setStyleSheet(
            self.active_btn_style()
        )

    # ================= TABLE DATA =================

    def set_table_data(self, table, rows):
        headers = [
            "Alert ID",
            "Driver",
            "Severity",
            "Date",
            "Time",
            "Action"
        ]

        table.clear()

        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            table.setRowHeight(r, 44)

            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                if str(value).lower() in [
                    "high",
                    "critical",
                    "high risk"
                ]:
                    item.setForeground(Qt.red)

                elif str(value).lower() == "drowsiness":
                    item.setForeground(Qt.cyan)

                elif str(value).lower() == "view report":
                    item.setForeground(Qt.green)

                table.setItem(r, c, item)

    # ================= OPEN REPORT =================

    def open_report(self, table, row):
        try:
            driver_item = table.item(row, 1)

            if not driver_item:
                return

            driver_name = driver_item.text()

            driver_data = get_driver_report_by_name(driver_name)

            if not driver_data:
                QMessageBox.warning(
                    self,
                    "Not Found",
                    "Driver report not found."
                )
                return

            report = DriverReportPage(driver_data)

            report.show()

            self.report_windows.append(report)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )