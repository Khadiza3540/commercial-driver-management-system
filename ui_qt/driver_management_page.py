from PySide6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QStackedWidget, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt
from ui_qt.driver_report_page import DriverReportPage
from database import (
    update_driver_status,
    get_all_drivers_admin,
    authorize_driver
)


class DriverManagementPage(QWidget):
    def __init__(self, drivers):
        super().__init__()
        self.drivers = drivers
        self.current_tab = 0

        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(0, 0, 0, 0)
        self.main.setSpacing(14)
        self.main.setAlignment(Qt.AlignTop)

        tab_row = QHBoxLayout()
        tab_row.setSpacing(12)

        self.tab_buttons = []

        tabs = [
            ("⏳ Pending Approval", 0),
            ("✅ Active Drivers", 1),
            ("⛔ Disabled Drivers", 2),
            ("🛡 Driver Safety Report", 3),
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
        self.search_box.setPlaceholderText("Search driver by name, email, phone or vehicle...")
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

        self.pending_table = self.create_table()
        self.active_table = self.create_table()
        self.disabled_table = self.create_table()
        self.safety_table = self.create_table()

        self.stack.addWidget(self.pending_table)
        self.stack.addWidget(self.active_table)
        self.stack.addWidget(self.disabled_table)
        self.stack.addWidget(self.safety_table)

        self.main.addWidget(self.stack)

        self.pending_table.cellDoubleClicked.connect(self.handle_pending_action)
        self.active_table.cellDoubleClicked.connect(self.handle_active_action)
        self.disabled_table.cellDoubleClicked.connect(self.handle_disabled_action)
        self.safety_table.cellDoubleClicked.connect(self.open_selected_driver_report)

        self.load_all_tables()

    def create_table(self):
        table = QTableWidget()
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setMinimumHeight(500)

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

    def filtered_drivers(self, status=None, approval=None):
        keyword = self.search_box.text().strip().lower()
        result = []

        for d in self.drivers:
            # d = id, name, username, email, license, phone, vehicle_no, status, is_authorized, trips, alerts
            searchable = f"{d[1]} {d[2]} {d[3]} {d[4]} {d[5]} {d[6]}".lower()

            if status and str(d[7]).lower() != status:
                continue

            if approval == "pending" and bool(d[8]) is True:
                continue

            if approval == "approved" and bool(d[8]) is False:
                continue

            if keyword and keyword not in searchable:
                continue

            result.append(d)

        return result

    def set_table_data(self, table, headers, rows):
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            table.setRowHeight(r, 46)

            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                value_text = str(value)

                if value_text in ["Safe", "Active", "Approved ✅", "Open Report", "Enable Driver"]:
                    item.setForeground(Qt.green)
                elif value_text in ["Moderate", "Risky", "Pending Approval", "Approve Driver"]:
                    item.setForeground(Qt.yellow)
                elif value_text in ["High Risk", "Disabled", "Disable Driver"]:
                    item.setForeground(Qt.red)

                table.setItem(r, c, item)

    def load_all_tables(self):
        self.load_pending_table()
        self.load_active_table()
        self.load_disabled_table()
        self.load_safety_table()

    def load_pending_table(self):
        rows = [
            [
                d[0], d[1], d[2], d[3], d[4], d[5], d[6],
                "Pending Approval", "Approve Driver"
            ]
            for d in self.filtered_drivers(approval="pending")
        ]

        self.set_table_data(
            self.pending_table,
            ["ID", "Name", "Username", "Email", "License", "Phone", "Vehicle", "Approval Status", "Admin Action"],
            rows
        )

    def load_active_table(self):
        rows = [
            [
                d[0], d[1], d[2], d[3], d[5], d[6], d[9], d[10],
                "Approved ✅", "Disable Driver"
            ]
            for d in self.filtered_drivers(status="active", approval="approved")
        ]

        self.set_table_data(
            self.active_table,
            ["ID", "Name", "Username", "Email", "Phone", "Vehicle", "Trips", "Alerts", "Approval", "Admin Action"],
            rows
        )

    def load_disabled_table(self):
        rows = [
            [
                d[0], d[1], d[2], d[3], d[5], d[6], d[9], d[10],
                "Approved ✅" if bool(d[8]) else "Pending Approval",
                "Enable Driver"
            ]
            for d in self.filtered_drivers(status="disabled")
        ]

        self.set_table_data(
            self.disabled_table,
            ["ID", "Name", "Username", "Email", "Phone", "Vehicle", "Trips", "Alerts", "Approval", "Admin Action"],
            rows
        )

    def load_safety_table(self):
        rows = []

        for d in self.filtered_drivers():
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

            approval = "Approved ✅" if bool(d[8]) else "Pending Approval"

            rows.append([
                d[0], d[1], d[6], d[9], alerts,
                f"{score}%", risk, d[7], approval, "Open Report"
            ])

        self.set_table_data(
            self.safety_table,
            ["ID", "Driver", "Vehicle", "Trips", "Alerts", "Safety Score", "Risk Level", "Status", "Approval", "View Report"],
            rows
        )

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
        self.drivers = get_all_drivers_admin()

        if self.current_tab == 0:
            self.load_pending_table()
        elif self.current_tab == 1:
            self.load_active_table()
        elif self.current_tab == 2:
            self.load_disabled_table()
        else:
            self.load_safety_table()

    def handle_pending_action(self, row, col):
        if col != 8:
            return

        driver_id = int(self.pending_table.item(row, 0).text())
        driver_name = self.pending_table.item(row, 1).text()

        confirm = QMessageBox.question(
            self,
            "Approve Driver",
            f"Do you want to approve {driver_name}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            authorize_driver(driver_id)
            update_driver_status(driver_id, "Active")

            QMessageBox.information(
                self,
                "Approved",
                f"{driver_name} has been approved successfully."
            )

            self.drivers = get_all_drivers_admin()
            self.load_all_tables()

    def handle_active_action(self, row, col):
        if col != 9:
            return

        driver_id = int(self.active_table.item(row, 0).text())
        update_driver_status(driver_id, "Disabled")

        self.drivers = get_all_drivers_admin()
        self.load_all_tables()

    def handle_disabled_action(self, row, col):
        if col != 9:
            return

        driver_id = int(self.disabled_table.item(row, 0).text())
        update_driver_status(driver_id, "Active")

        self.drivers = get_all_drivers_admin()
        self.load_all_tables()

    def open_selected_driver_report(self, row, col):
        if self.current_tab != 3:
            return

        driver_id = int(self.safety_table.item(row, 0).text())

        selected_driver = None
        for d in self.drivers:
            if int(d[0]) == driver_id:
                selected_driver = d
                break

        if selected_driver:
            self.report_window = DriverReportPage(selected_driver)
            self.report_window.show()
