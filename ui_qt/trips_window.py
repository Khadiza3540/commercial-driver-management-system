import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from database import get_trips


class TripsWindow(QWidget):
    def __init__(self, driver_id):
        super().__init__()

        self.driver_id = driver_id

        self.setWindowTitle("CDMS - Trip History")
        self.resize(1100, 650)

        self.setStyleSheet("""
            QWidget {
                background-color: #050b1a;
                color: white;
                font-family: Segoe UI;
            }

            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: white;
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(18)

        title = QLabel("🚗 Trip History")
        title.setObjectName("title")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Route",
            "Status",
            "Date",
            "Start Time",
            "End Time",
            "Action"
        ])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        layout.addWidget(self.table)

        self.load_trips()

    def load_trips(self):
        trips = get_trips(self.driver_id)

        self.table.setRowCount(len(trips))

        for row_index, trip in enumerate(trips):
            start, dest, status, date, start_time, end_time = trip

            route_text = f"{start} → {dest}"
            action_text = "View"

            values = [
                route_text,
                status,
                date,
                start_time,
                end_time if end_time else "-",
                action_text
            ]

            for col_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                if col_index == 1:
                    if status == "Completed":
                        item.setForeground(QColor("#22c55e"))
                    elif status == "Active":
                        item.setForeground(QColor("#facc15"))
                    else:
                        item.setForeground(QColor("#ef4444"))

                self.table.setItem(row_index, col_index, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TripsWindow(driver_id=1)
    win.showMaximized()
    sys.exit(app.exec())