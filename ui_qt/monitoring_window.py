import sys
import os
import cv2
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QUrl
from urllib.parse import quote
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView

from modules.drowsiness_detector import process_frame
from modules.alert_manager import play_alarm, stop_alarm
from database import start_session, end_session, add_alert, start_trip, end_trip


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASSIFIER_PATH = os.path.join(BASE_DIR, "data", "classifier.xml")
LABELS_PATH = os.path.join(BASE_DIR, "data", "labels.npy")
FACE_CASCADE_PATH = os.path.join(BASE_DIR, "models", "haarcascade_frontalface_default.xml")


class MonitoringWindow(QWidget):
    def __init__(self, driver_id=None, driver_name="Driver", current_location="", destination=""):
        super().__init__()

        self.driver_id = int(driver_id) if driver_id is not None else None
        self.driver_name = driver_name
        self.current_location = current_location
        self.destination = destination

        self.setWindowTitle("CDMS - Driver Monitoring")
        self.resize(1200, 650)

        self.cap = None
        self.face_cascade = None
        self.recognizer = None
        self.labels = {}

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.closed_counter = 0
        self.alarm_on = False
        self.monitoring_on = False

        self.session_id = None
        self.trip_id = None
        self.alert_saved = False

        self.driver_verified = False
        self.match_count = 0
        self.failed_count = 0

        self.setStyleSheet("""
            QWidget {
                background-color: #050b1a;
                color: white;
                font-family: Segoe UI;
            }

            QFrame#card {
                background-color: #081226;
                border: 1px solid #1f70c1;
                border-radius: 16px;
            }

            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: white;
            }

            QLabel#status {
                font-size: 18px;
                font-weight: bold;
                color: #ef4444;
            }

            QLabel#mapTitle {
                font-size: 18px;
                font-weight: bold;
                color: #18a0ff;
            }

            QPushButton#startBtn {
                background-color: #0d6efd;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton#endBtn {
                background-color: #ef4444;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(30, 25, 30, 25)
        main.setSpacing(18)

        header = QHBoxLayout()

        title = QLabel(f"Driver Monitoring - {self.driver_name}")
        title.setObjectName("title")

        self.status_label = QLabel("Status: OFF")
        self.status_label.setObjectName("status")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status_label)

        main.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(18)

        camera_card = QFrame()
        camera_card.setObjectName("card")

        camera_layout = QVBoxLayout(camera_card)
        camera_layout.setContentsMargins(18, 18, 18, 18)

        self.camera_label = QLabel("Camera OFF")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumHeight(430)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #020817;
                border: 1px dashed #1f70c1;
                border-radius: 12px;
                color: #9aa7bd;
                font-size: 22px;
            }
        """)

        camera_layout.addWidget(self.camera_label)

        map_card = QFrame()
        map_card.setObjectName("card")
        map_card.setFixedWidth(300)

        map_layout = QVBoxLayout(map_card)
        map_layout.setContentsMargins(14, 14, 14, 14)
        map_layout.setSpacing(12)

        map_title = QLabel("🗺️ Live Road / Map")
        map_title.setObjectName("mapTitle")

        self.map_view = QWebEngineView()
        self.map_view.setMinimumHeight(430)

        self.load_route_map()

        map_layout.addWidget(map_title)
        map_layout.addWidget(self.map_view)

        body.addWidget(camera_card, 4)
        body.addWidget(map_card, 1)

        main.addLayout(body, 1)

        btn_row = QHBoxLayout()

        start_btn = QPushButton("▶ Start Monitoring")
        start_btn.setObjectName("startBtn")
        start_btn.clicked.connect(self.start_monitoring)

        end_btn = QPushButton("■ End Monitoring")
        end_btn.setObjectName("endBtn")
        end_btn.clicked.connect(self.end_monitoring)

        btn_row.addStretch()
        btn_row.addWidget(start_btn)
        btn_row.addWidget(end_btn)

        main.addLayout(btn_row)

    def start_monitoring(self):
        if self.monitoring_on:
            return

        if self.driver_id is None:
            QMessageBox.critical(self, "Error", "Driver ID not found. Please login again.")
            return

        if not os.path.exists(FACE_CASCADE_PATH):
            QMessageBox.critical(self, "Error", f"Face cascade not found:\n{FACE_CASCADE_PATH}")
            return

        if not os.path.exists(CLASSIFIER_PATH):
            QMessageBox.critical(self, "Error", "Face classifier not found. Please register driver first.")
            return

        if not os.path.exists(LABELS_PATH):
            QMessageBox.critical(self, "Error", "Labels file not found. Please register driver again.")
            return

        self.face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(CLASSIFIER_PATH)
        self.labels = np.load(LABELS_PATH, allow_pickle=True).item()

        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Camera not opened")
            return

        try:
            self.session_id = start_session(self.driver_id, self.driver_name)
            self.trip_id = start_trip(
                self.driver_id,
                self.current_location,
                self.destination
            )
        except Exception as e:
            QMessageBox.critical(self, "Session Error", str(e))
            return

        self.monitoring_on = True
        self.alert_saved = False
        self.driver_verified = False
        self.match_count = 0
        self.failed_count = 0

        self.status_label.setText("Status: Active")
        self.status_label.setStyleSheet("color:#22c55e;font-size:18px;font-weight:bold;")

        self.load_route_map()
        self.timer.start(30)

    def draw_clean_overlay(self, frame, status, ear):
        overlay_x = 22
        overlay_y = 32
        line_gap = 25

        status_color = (0, 0, 255) if status == "DROWSY" else (0, 255, 0)

        cv2.putText(
            frame,
            f"Driver: {self.driver_name}",
            (overlay_x, overlay_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Status: {status}",
            (overlay_x, overlay_y + line_gap),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            status_color,
            2
        )

        cv2.putText(
            frame,
            f"EAR: {ear:.2f}",
            (overlay_x, overlay_y + line_gap * 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2
        )

        return frame

    def draw_unauthorized_overlay(self, frame, message="Authorized driver not detected"):
        cv2.rectangle(frame, (8, 5), (620, 75), (0, 0, 0), -1)
        cv2.rectangle(frame, (8, 5), (620, 75), (0, 0, 255), 2)

        cv2.putText(
            frame,
            message,
            (25, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            (0, 0, 255),
            2
        )

        return frame

    def verify_current_driver(self, frame, gray, faces):
        authorized = False
        best_confidence = None
        best_box = None

        found_same_driver = False

        for (x, y, w, h) in faces:
            face_img = gray[y:y + h, x:x + w]
            face_img = cv2.resize(face_img, (200, 200))

            predicted_id, confidence = self.recognizer.predict(face_img)

            print("Predicted:", predicted_id, "Login ID:", self.driver_id, "Confidence:", confidence)

            if int(predicted_id) == int(self.driver_id):
                found_same_driver = True
                best_confidence = confidence
                best_box = (x, y, w, h)

                if confidence < 70:
                    self.match_count += 1
                else:
                    self.match_count = 0
            else:
                if not self.driver_verified:
                    self.match_count = 0

        if self.match_count >= 3:
            self.driver_verified = True
            authorized = True

        if self.driver_verified:
            authorized = True

        if authorized and best_box is not None:
            x, y, w, h = best_box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            label_text = self.driver_name
            if best_confidence is not None:
                label_text = f"{self.driver_name} ({int(best_confidence)})"

            cv2.putText(
                frame,
                label_text,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 255, 0),
                2
            )

        return authorized, frame

    def update_frame(self):
        if self.cap is None:
            return

        ret, frame = self.cap.read()

        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        authorized, frame = self.verify_current_driver(frame, gray, faces)

        if not authorized:
            self.closed_counter = 0
            self.alert_saved = False

            if self.alarm_on:
                stop_alarm()
                self.alarm_on = False

            frame = self.draw_unauthorized_overlay(frame)
            self.show_frame(frame)
            return

        frame, status, ear, self.closed_counter = process_frame(frame, self.closed_counter)

        if status == "DROWSY":
            if not self.alarm_on:
                play_alarm()
                self.alarm_on = True

            if not self.alert_saved and self.session_id is not None:
                try:
                    add_alert(self.session_id, self.driver_id, self.driver_name)
                    self.alert_saved = True
                    print("Alert saved to database")
                except Exception as e:
                    print("Alert save error:", e)

        else:
            if self.alarm_on:
                stop_alarm()
                self.alarm_on = False

            self.alert_saved = False

        frame = self.draw_clean_overlay(frame, status, ear)
        self.show_frame(frame)

    def load_route_map(self):
        import json

        start = self.current_location.strip()
        end = self.destination.strip()

        if not (start and end):
            return

        start_js = json.dumps(start)
        end_js = json.dumps(end)

        ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjcyYTc3YjA5N2ExNTRhYzI5ZDliZWI0ZWY1ZGUzOGNiIiwiaCI6Im11cm11cjY0In0="

        map_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8"/>
            <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

            <style>
                html, body, #map {{
                    margin: 0; padding: 0;
                    width: 100%; height: 100%;
                    background: #020817;
                }}
            </style>
        </head>

        <body>
            <div id="map"></div>

            <script>
                const API_KEY = "{ORS_API_KEY}";
                var map = L.map('map').setView([23.8103, 90.4125], 7);

                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19
                }}).addTo(map);

                async function getCoords(place) {{
                    let url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + encodeURIComponent(place);
                    let res = await fetch(url);
                    let data = await res.json();
                    if (!data || data.length === 0) return null;
                    return [parseFloat(data[0].lat), parseFloat(data[0].lon)];
                }}

                async function drawRoute() {{
                    let startPlace = {start_js};
                    let endPlace = {end_js};

                    let start = await getCoords(startPlace);
                    let end = await getCoords(endPlace);

                    if (!start || !end) {{
                        console.log("Location not found");
                        return;
                    }}

                    L.marker(start).addTo(map).bindPopup("Start");
                    L.marker(end).addTo(map).bindPopup("End");

                    let response = await fetch(
                        "https://api.openrouteservice.org/v2/directions/driving-car/geojson",
                        {{
                            method: "POST",
                            headers: {{
                                "Authorization": API_KEY,
                                "Content-Type": "application/json"
                            }},
                            body: JSON.stringify({{
                                coordinates: [
                                    [start[1], start[0]],
                                    [end[1], end[0]]
                                ]
                            }})
                        }}
                    );

                    let data = await response.json();

                    if (!data.features) {{
                        console.log("Route error:", data);
                        return;
                    }}

                    let coords = data.features[0].geometry.coordinates;
                    let latlngs = coords.map(c => [c[1], c[0]]);

                    let routeLine = L.polyline(latlngs, {{
                        color: "blue",
                        weight: 5
                    }}).addTo(map);

                    map.fitBounds(routeLine.getBounds(), {{padding: [30, 30]}});
                }}

                drawRoute();
            </script>
        </body>
        </html>
        """

        self.map_view.setHtml(map_html)

    def show_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        qt_image = QImage(
            rgb_frame.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qt_image)

        self.camera_label.setPixmap(
            pixmap.scaled(
                self.camera_label.width(),
                self.camera_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def end_monitoring(self):
        self.timer.stop()

        if self.alarm_on:
            stop_alarm()
            self.alarm_on = False

        if self.session_id is not None:
            try:
                end_session(self.session_id)
                end_trip(self.driver_id)
            except Exception as e:
                print("Session end error:", e)

        self.session_id = None
        self.alert_saved = False

        if self.cap:
            self.cap.release()
            self.cap = None

        self.monitoring_on = False
        self.driver_verified = False
        self.match_count = 0
        self.failed_count = 0
        self.closed_counter = 0

        self.status_label.setText("Status: OFF")
        self.status_label.setStyleSheet("color:#ef4444;font-size:18px;font-weight:bold;")

        self.camera_label.clear()
        self.camera_label.setText("Camera OFF")

    def closeEvent(self, event):
        self.end_monitoring()
        event.accept()