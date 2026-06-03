from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame, QComboBox, QLineEdit
)
from PySide6.QtCore import Qt

from database import (
    get_all_toll_payments_admin,
    mark_toll_payment_paid,
    seed_demo_toll_payments
)


class PaymentGatewayWindow(QWidget):
    def __init__(self, toll_record, on_payment_success):
        super().__init__()
        self.toll_record = toll_record
        self.on_payment_success = on_payment_success

        self.setWindowTitle("CDMS Toll Payment Gateway")
        self.resize(520, 430)

        payment_id, month, location, amount, status, method = toll_record

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
            QLineEdit, QComboBox {
                background:#081226;
                border:1px solid #1f70c1;
                border-radius:12px;
                color:white;
                padding:10px;
                font-size:13px;
            }
            QPushButton {
                background:#0d6efd;
                color:white;
                border:none;
                border-radius:12px;
                font-weight:bold;
                padding:11px;
            }
            QPushButton:hover {
                background:#18a0ff;
            }
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        title = QLabel("💳 Toll Payment Gateway")
        title.setStyleSheet("font-size:26px;font-weight:900;color:white;")

        info = QLabel(
            f"Month: {month}\n"
            f"Toll Location: {location}\n"
            f"Amount: {amount} Taka"
        )
        info.setStyleSheet("font-size:14px;color:#cbd5e1;line-height:1.6;")

        self.method_box = QComboBox()
        self.method_box.addItems(["Card Payment", "Bkash", "Nagad", "Rocket", "Bank Transfer"])

        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Payment reference / transaction ID")

        pay_btn = QPushButton("✅ Confirm Payment")
        pay_btn.clicked.connect(self.confirm_payment)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background:#071426;
                border:1px solid #1f70c1;
                color:white;
            }
            QPushButton:hover {
                background:#0d1f3a;
                border:1px solid #18a0ff;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(self.method_box)
        layout.addWidget(self.reference_input)
        layout.addWidget(pay_btn)
        layout.addWidget(cancel_btn)

        main.addWidget(card)

    def confirm_payment(self):
        payment_id = self.toll_record[0]
        method = self.method_box.currentText()

        mark_toll_payment_paid(payment_id, method)

        QMessageBox.information(
            self,
            "Payment Successful",
            "Toll payment completed successfully."
        )

        self.on_payment_success()
        self.close()


class TollPaymentManagementPage(QWidget):
    def __init__(self):
        super().__init__()

        seed_demo_toll_payments()

        self.payment_windows = []

        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(0, 0, 0, 0)
        self.main.setSpacing(14)
        self.main.setAlignment(Qt.AlignTop)

        self.search_box = QLineEdit()
        self.status_filter = QComboBox()

        self.table = QTableWidget()

        self.build_ui()
        self.refresh_page()

    def build_ui(self):
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        self.search_box.setPlaceholderText("Search by month or toll location...")
        self.search_box.setFixedHeight(42)
        self.search_box.textChanged.connect(self.refresh_page)
        self.search_box.setStyleSheet(self.input_style())

        self.status_filter.addItems(["All Status", "Paid", "Unpaid"])
        self.status_filter.setFixedHeight(42)
        self.status_filter.currentTextChanged.connect(self.refresh_page)
        self.status_filter.setStyleSheet(self.input_style())

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setFixedHeight(42)
        refresh_btn.clicked.connect(self.refresh_page)
        refresh_btn.setStyleSheet(self.button_style())

        top_row.addWidget(self.search_box, 3)
        top_row.addWidget(self.status_filter, 1)
        top_row.addWidget(refresh_btn)

        self.main.addLayout(top_row)

        self.create_table()
        self.main.addWidget(self.table)

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

    def button_style(self):
        return """
            QPushButton {
                background:#071426;
                border:1px solid #1f70c1;
                border-radius:12px;
                color:white;
                padding:0 18px;
                font-size:13px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:#0d1f3a;
                border:1px solid #18a0ff;
                color:#18a0ff;
            }
        """

    def create_table(self):
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumHeight(560)

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

    def filtered_records(self):
        keyword = self.search_box.text().strip().lower()
        status_filter = self.status_filter.currentText().lower()

        records = get_all_toll_payments_admin()
        result = []

        for record in records:
            payment_id, month, location, amount, status, method = record

            searchable = f"{month} {location} {amount} {status} {method}".lower()

            if keyword and keyword not in searchable:
                continue

            if status_filter != "all status" and str(status).lower() != status_filter:
                continue

            result.append(record)

        return result

    def refresh_page(self):
        records = self.filtered_records()

        headers = ["Month", "Toll Location", "Amount", "Payment Status", "Action"]
        self.table.clear()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(records))

        for row, record in enumerate(records):
            payment_id, month, location, amount, status, method = record

            values = [
                month,
                location,
                f"{amount} Taka",
                status
            ]

            self.table.setRowHeight(row, 48)

            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                if str(value).lower() == "paid":
                    item.setForeground(Qt.green)
                elif str(value).lower() == "unpaid":
                    item.setForeground(Qt.red)

                self.table.setItem(row, col, item)

            if str(status).lower() == "paid":
                paid_item = QTableWidgetItem("Paid ✅")
                paid_item.setTextAlignment(Qt.AlignCenter)
                paid_item.setForeground(Qt.green)
                self.table.setItem(row, 4, paid_item)
            else:
                pay_btn = QPushButton("Pay Now")
                pay_btn.setCursor(Qt.PointingHandCursor)
                pay_btn.setStyleSheet("""
                    QPushButton {
                        background:#0d6efd;
                        color:white;
                        border:none;
                        border-radius:10px;
                        font-size:12px;
                        font-weight:bold;
                        padding:8px;
                    }
                    QPushButton:hover {
                        background:#18a0ff;
                    }
                """)
                pay_btn.clicked.connect(
                    lambda checked=False, r=record: self.open_payment_gateway(r)
                )
                self.table.setCellWidget(row, 4, pay_btn)

    def open_payment_gateway(self, record):
        gateway = PaymentGatewayWindow(record, self.refresh_page)
        gateway.show()
        self.payment_windows.append(gateway)
