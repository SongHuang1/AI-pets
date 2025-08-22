
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QTableWidget, QTableWidgetItem, QHeaderView, 
                              QPushButton, QTabWidget, QProgressBar, QWidget, QScrollArea)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import datetime
from .usage_tracker import UsageTracker

class UsageStatsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("电脑使用统计")
        self.setFixedSize(600, 500)
        self.tracker = UsageTracker()

        self.initUI()
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(5000)
        self.update_data()

    def initUI(self):
        layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.create_overview_tab()
        self.create_apps_tab()
        self.tab_widget.addTab(self.overview_tab, "总体使用情况")
        self.tab_widget.addTab(self.apps_tab, "应用使用情况")
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def create_overview_tab(self):
        self.overview_tab = QWidget()
        layout = QVBoxLayout()

        title = QLabel("最近七天电脑使用情况")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        self.daily_usage_table = QTableWidget()
        self.daily_usage_table.setColumnCount(2)
        self.daily_usage_table.setHorizontalHeaderLabels(["日期", "使用时间(分钟)"])
        self.daily_usage_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.daily_usage_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.daily_usage_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.daily_usage_table)

        self.total_usage_label = QLabel("总使用时间: 计算中...")
        self.total_usage_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.total_usage_label)

        layout.addWidget(QLabel("每日使用时间分布:"))
        self.daily_usage_progress = QVBoxLayout()

        for i in range(7):
            progress_layout = QHBoxLayout()
            date_label = QLabel()
            progress_bar = QProgressBar()
            progress_bar.setTextVisible(False)
            progress_bar.setFormat("")
            progress_label = QLabel("0 分钟")

            progress_layout.addWidget(date_label)
            progress_layout.addWidget(progress_bar)
            progress_layout.addWidget(progress_label)

            self.daily_usage_progress.addLayout(progress_layout)

        layout.addLayout(self.daily_usage_progress)

        self.overview_tab.setLayout(layout)

    def create_apps_tab(self):
        self.apps_tab = QWidget()
        layout = QVBoxLayout()
        title = QLabel("当天应用使用情况")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        self.apps_table = QTableWidget()
        self.apps_table.setColumnCount(3)
        self.apps_table.setHorizontalHeaderLabels(["应用名称", "总使用时间(分钟)", "占比"])
        self.apps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.apps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.apps_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.apps_table)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(scroll_area)

        self.apps_tab.setLayout(layout)

    def update_data(self):
        recent_usage = self.tracker.get_recent_usage(days=7)
        self.update_overview_tab(recent_usage)
        self.update_apps_tab(recent_usage)

    def update_overview_tab(self, recent_usage):
        self.daily_usage_table.setRowCount(0)
        total_minutes = 0
        sorted_dates = sorted(recent_usage["total_daily_usage"].items(), reverse=True)

        for date, seconds in sorted_dates:
            minutes = seconds / 60
            total_minutes += minutes
            row = self.daily_usage_table.rowCount()
            self.daily_usage_table.insertRow(row)
            date_item = QTableWidgetItem(date)
            self.daily_usage_table.setItem(row, 0, date_item)

            time_item = QTableWidgetItem(f"{minutes:.1f}")
            self.daily_usage_table.setItem(row, 1, time_item)
        hours = total_minutes / 60
        self.total_usage_label.setText(f"总使用时间: {hours:.1f} 小时 ({total_minutes:.1f} 分钟)")

        today = datetime.datetime.now()
        date_format = "%Y-%m-%d"

        for i in range(7):
            date = (today - datetime.timedelta(days=i)).strftime(date_format)
            seconds = recent_usage["total_daily_usage"].get(date, 0)
            minutes = seconds / 60

            date_label = self.daily_usage_progress.itemAt(i).layout().itemAt(0).widget()
            date_label.setText(date)

            progress_bar = self.daily_usage_progress.itemAt(i).layout().itemAt(1).widget()
            
            if recent_usage["total_daily_usage"].values():
                max_minutes = max(recent_usage["total_daily_usage"].values()) / 60
                max_minutes = max(1, max_minutes)
            else:
                max_minutes = 1
            
            progress_bar.setMaximum(int(max_minutes))
            progress_bar.setValue(int(minutes))
            progress_bar.setTextVisible(False)

            time_label = self.daily_usage_progress.itemAt(i).layout().itemAt(2).widget()
            time_label.setFixedWidth(60)
            time_label.setText(f"{minutes:.1f} 分钟")
            time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def update_apps_tab(self, recent_usage):
        top_apps = self.tracker.get_top_apps(limit=None, days=1)
        self.apps_table.setRowCount(0)
        if top_apps:
            total_seconds = sum(app_data["total_time"] for _, app_data in top_apps)
            total_minutes = total_seconds / 60
        else:
            total_seconds = 0
            total_minutes = 0

        if not top_apps:
            row = self.apps_table.rowCount()
            self.apps_table.insertRow(row)
            no_data_item = QTableWidgetItem("暂无数据，请稍后再试")
            no_data_item.setTextAlignment(Qt.AlignCenter)
            self.apps_table.setItem(row, 0, no_data_item)
            
            time_item = QTableWidgetItem("暂无数据，请稍后再试")
            time_item.setTextAlignment(Qt.AlignCenter)
            self.apps_table.setItem(row, 1, time_item)
            
            percentage_item = QTableWidgetItem("暂无数据，请稍后再试")
            percentage_item.setTextAlignment(Qt.AlignCenter)
            self.apps_table.setItem(row, 2, percentage_item)
        else:
            for app_name, app_data in top_apps:
                row = self.apps_table.rowCount()
                self.apps_table.insertRow(row)

                name_item = QTableWidgetItem(app_name)
                self.apps_table.setItem(row, 0, name_item)
                minutes = app_data["total_time"] / 60
                time_item = QTableWidgetItem(f"{minutes:.1f}")
                self.apps_table.setItem(row, 1, time_item)
                if total_seconds > 0:
                    percentage = (app_data["total_time"] / total_seconds) * 100
                    percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
                else:
                    percentage_item = QTableWidgetItem("0%")
                self.apps_table.setItem(row, 2, percentage_item)

    def closeEvent(self, event):
        self.update_timer.stop()
        event.accept()
