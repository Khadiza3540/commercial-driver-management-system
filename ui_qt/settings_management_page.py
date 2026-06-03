from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QLineEdit, QCheckBox, QMessageBox,
    QFileDialog, QStackedWidget
)
from PySide6.QtCore import Qt


class SettingsManagementPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background:#050b1a;
                color:white;
                font-family:Segoe UI;
            }
            QLabel {
                background:transparent;
                border:none;
            }
            QFrame#detailCard {
                background:#071426;
                border:1px solid #1f70c1;
                border-radius:18px;
            }
            QLineEdit {
                background:#081226;
                border:1px solid #1f70c1;
                border-radius:12px;
                padding:10px;
                color:white;
                font-size:13px;
            }
            QLineEdit:focus {
                border:1px solid #18a0ff;
            }
            QCheckBox {
                color:#cbd5e1;
                font-size:14px;
                background:transparent;
            }
            QPushButton#primaryBtn {
                background:#0d6efd;
                border:none;
                color:white;
                border-radius:10px;
                font-size:12px;
                font-weight:bold;
            }
            QPushButton#primaryBtn:hover {
                background:#18a0ff;
            }
            QPushButton#dangerBtn {
                background:#7f1d1d;
                border:1px solid #ef4444;
                color:white;
                border-radius:10px;
                font-size:12px;
                font-weight:bold;
            }
            QPushButton#dangerBtn:hover {
                background:#dc2626;
            }
        """)

        self.stack = QStackedWidget()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.stack)

        self.home_page = QWidget()
        self.detail_page = QWidget()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.detail_page)

        self.build_home_page()
        self.build_detail_page()

    # ================= HOME PAGE =================

    def build_home_page(self):
        layout = QVBoxLayout(self.home_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        section = QLabel("Explore Settings")
        section.setStyleSheet("""
            QLabel {
                font-size:22px;
                font-weight:900;
                color:white;
                background:transparent;
                border:none;
                margin-top:6px;
            }
        """)
        layout.addWidget(section)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)

        cards = [
            ("👤", "Admin Profile", "Update admin name and email.", 0),
            ("🔐", "Security", "Change password and access settings.", 1),
            ("🚨", "Alert Rules", "Set threshold and warning controls.", 2),
            ("🛡️", "Auto Disable", "Control risky driver actions.", 3),
            ("📤", "Export Reports", "Export project reports.", 4),
            ("🧹", "Clear Alerts", "Clear old alert records.", 5),
            ("🌙", "Appearance", "Theme and UI preferences.", 6),
            ("ℹ️", "System Info", "View system configuration.", 7),
        ]

        for i, (icon, title, text, index) in enumerate(cards):
            grid.addWidget(self.topic_button(icon, title, text, index), i // 3, i % 3)

        layout.addLayout(grid)
        layout.addStretch()

    def topic_button(self, icon, title, desc, index):
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(145)
        btn.setMaximumHeight(155)
        btn.setMinimumWidth(0)

        btn.setText(
            f"{icon}\n\n"
            f"{title}\n"
            f"{desc}\n\n"
            f"Open →"
        )

        btn.clicked.connect(lambda checked=False, i=index: self.open_detail(i))

        btn.setStyleSheet("""
            QPushButton {
                background:#071426;
                border:1px solid #1f70c1;
                border-radius:18px;
                color:white;
                text-align:left;
                padding:16px 20px;
                font-size:13px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:#0a1b32;
                border:1px solid #18a0ff;
                color:#18a0ff;
            }
        """)

        return btn

    # ================= DETAIL PAGE =================

    def build_detail_page(self):
        self.detail_layout = QVBoxLayout(self.detail_page)
        self.detail_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_layout.setSpacing(14)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("primaryBtn")
        back_btn.setFixedSize(110, 38)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.detail_layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        self.detail_container = QFrame()
        self.detail_container.setObjectName("detailCard")

        self.detail_content = QVBoxLayout(self.detail_container)
        self.detail_content.setContentsMargins(26, 24, 26, 24)
        self.detail_content.setSpacing(14)

        self.detail_layout.addWidget(self.detail_container)
        self.detail_layout.addStretch()

    def clear_detail_content(self):
        while self.detail_content.count():
            item = self.detail_content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def open_detail(self, index):
        self.clear_detail_content()

        pages = [
            self.admin_profile_content,
            self.security_content,
            self.alert_rules_content,
            self.auto_disable_content,
            self.export_reports_content,
            self.clear_alerts_content,
            self.appearance_content,
            self.system_info_content,
        ]

        pages[index]()
        self.stack.setCurrentIndex(1)

    def add_detail_header(self, title, subtitle):
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            QLabel {
                font-size:28px;
                font-weight:900;
                color:#18a0ff;
                background:transparent;
                border:none;
            }
        """)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setWordWrap(True)
        sub_lbl.setStyleSheet("""
            QLabel {
                font-size:14px;
                color:#9aa7bd;
                background:transparent;
                border:none;
            }
        """)

        self.detail_content.addWidget(title_lbl)
        self.detail_content.addWidget(sub_lbl)

    # ================= DETAIL CONTENT =================

    def admin_profile_content(self):
        self.add_detail_header("👤 Admin Profile", "Update admin profile information.")

        name = QLineEdit()
        name.setPlaceholderText("Admin Name")

        email = QLineEdit()
        email.setPlaceholderText("Admin Email")

        save = QPushButton("💾 Save")
        save.setObjectName("primaryBtn")
        save.setFixedSize(110, 38)
        save.clicked.connect(lambda: self.info("Profile updated successfully."))

        self.detail_content.addWidget(name)
        self.detail_content.addWidget(email)
        self.detail_content.addWidget(save)

    def security_content(self):
        self.add_detail_header("🔐 Security", "Change admin password.")

        old_pass = QLineEdit()
        old_pass.setPlaceholderText("Current Password")
        old_pass.setEchoMode(QLineEdit.Password)

        new_pass = QLineEdit()
        new_pass.setPlaceholderText("New Password")
        new_pass.setEchoMode(QLineEdit.Password)

        confirm_pass = QLineEdit()
        confirm_pass.setPlaceholderText("Confirm Password")
        confirm_pass.setEchoMode(QLineEdit.Password)

        show_pass = QCheckBox("Show password")

        def toggle():
            mode = QLineEdit.Normal if show_pass.isChecked() else QLineEdit.Password
            old_pass.setEchoMode(mode)
            new_pass.setEchoMode(mode)
            confirm_pass.setEchoMode(mode)

        show_pass.stateChanged.connect(toggle)

        save = QPushButton("🔄 Change")
        save.setObjectName("primaryBtn")
        save.setFixedSize(120, 38)
        save.clicked.connect(lambda: self.info("Password changed successfully."))

        self.detail_content.addWidget(old_pass)
        self.detail_content.addWidget(new_pass)
        self.detail_content.addWidget(confirm_pass)
        self.detail_content.addWidget(show_pass)
        self.detail_content.addWidget(save)

    def alert_rules_content(self):
        self.add_detail_header("🚨 Alert Rules", "Configure alert threshold and warning rules.")

        threshold = QLineEdit()
        threshold.setPlaceholderText("Safety threshold percentage. Example: 30")

        high_risk = QCheckBox("Mark driver as high risk after repeated alerts")
        warning = QCheckBox("Enable warning before disabling driver")
        notify = QCheckBox("Enable admin notification for risky alerts")

        save = QPushButton("💾 Save")
        save.setObjectName("primaryBtn")
        save.setFixedSize(110, 38)
        save.clicked.connect(lambda: self.info("Alert rules updated."))

        self.detail_content.addWidget(threshold)
        self.detail_content.addWidget(high_risk)
        self.detail_content.addWidget(warning)
        self.detail_content.addWidget(notify)
        self.detail_content.addWidget(save)

    def auto_disable_content(self):
        self.add_detail_header("🛡 Auto Disable", "Control automatic disabling for risky drivers.")

        enable = QCheckBox("Enable auto-disable below safety threshold")
        review = QCheckBox("Require admin review before reactivation")
        log = QCheckBox("Keep system log for disabled profiles")

        save = QPushButton("💾 Save")
        save.setObjectName("primaryBtn")
        save.setFixedSize(110, 38)
        save.clicked.connect(lambda: self.info("Auto-disable settings saved."))

        self.detail_content.addWidget(enable)
        self.detail_content.addWidget(review)
        self.detail_content.addWidget(log)
        self.detail_content.addWidget(save)

    def export_reports_content(self):
        self.add_detail_header("📤 Export Reports", "Export report files for documentation.")

        export_btn = QPushButton("📄 Export")
        export_btn.setObjectName("primaryBtn")
        export_btn.setFixedSize(120, 38)
        export_btn.clicked.connect(self.export_report)

        self.detail_content.addWidget(export_btn)

    def clear_alerts_content(self):
        self.add_detail_header("🧹 Clear Alerts", "Clear old alert records from interface only.")

        clear_btn = QPushButton("🗑 Clear")
        clear_btn.setObjectName("dangerBtn")
        clear_btn.setFixedSize(110, 38)
        clear_btn.clicked.connect(lambda: self.info("Old alerts cleared from interface."))

        self.detail_content.addWidget(clear_btn)

    def appearance_content(self):
        self.add_detail_header("🌙 Appearance", "Manage interface preferences.")

        dark = QCheckBox("Dark blue theme")
        compact = QCheckBox("Compact table rows")
        notifications = QCheckBox("Enable UI notifications")
        auto_refresh = QCheckBox("Enable auto refresh indicators")

        dark.setChecked(True)

        save = QPushButton("💾 Save")
        save.setObjectName("primaryBtn")
        save.setFixedSize(110, 38)
        save.clicked.connect(lambda: self.info("Appearance saved."))

        self.detail_content.addWidget(dark)
        self.detail_content.addWidget(compact)
        self.detail_content.addWidget(notifications)
        self.detail_content.addWidget(auto_refresh)
        self.detail_content.addWidget(save)

    def system_info_content(self):
        self.add_detail_header("ℹ️ System Info", "Current CDMS configuration.")

        info = QLabel(
            "CDMS Version: 2.0\n\n"
            "System Type: Commercial Driver Monitoring System\n\n"
            "Database: PostgreSQL\n\n"
            "Interface: PySide6 Desktop Application\n\n"
            "Theme: Dark Blue Admin Dashboard\n\n"
            "Safety Threshold: 30%\n\n"
            "Auto Disable: Supported\n\n"
            "Toll Payment: Integrated"
        )
        info.setStyleSheet("""
            QLabel {
                font-size:15px;
                color:#cbd5e1;
                background:transparent;
                border:none;
            }
        """)

        self.detail_content.addWidget(info)

    # ================= HELPERS =================

    def export_report(self):
        QFileDialog.getSaveFileName(self, "Export Report", "", "PDF Files (*.pdf)")
        self.info("Report export process completed.")

    def info(self, message):
        QMessageBox.information(self, "Settings", message)
