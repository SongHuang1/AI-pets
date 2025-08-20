
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QTableWidget, QTableWidgetItem, QHeaderView, 
                              QPushButton, QTabWidget, QProgressBar, QWidget)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import datetime
from .usage_tracker import UsageTracker

class UsageStatsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("电脑使用统计")
        self.setFixedSize(600, 500)

        # 创建使用跟踪器
        self.tracker = UsageTracker()

        # 初始化UI
        self.initUI()

        # 设置定时器定期更新数据
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(5000)  # 每5秒更新一次

    def initUI(self):
        layout = QVBoxLayout()

        # 创建标签页
        self.tab_widget = QTabWidget()

        # 创建总体使用情况标签页
        self.create_overview_tab()

        # 创建应用使用情况标签页
        self.create_apps_tab()

        # 将标签页添加到标签页控件
        self.tab_widget.addTab(self.overview_tab, "总体使用情况")
        self.tab_widget.addTab(self.apps_tab, "应用使用情况")

        # 添加标签页到布局
        layout.addWidget(self.tab_widget)

        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def create_overview_tab(self):
        """创建总体使用情况标签页"""
        self.overview_tab = QWidget()
        layout = QVBoxLayout()

        # 添加标题
        title = QLabel("最近七天电脑使用情况")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        # 创建每日使用时间表格
        self.daily_usage_table = QTableWidget()
        self.daily_usage_table.setColumnCount(2)
        self.daily_usage_table.setHorizontalHeaderLabels(["日期", "使用时间(分钟)"])
        self.daily_usage_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.daily_usage_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.daily_usage_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.daily_usage_table)

        # 添加总使用时间标签
        self.total_usage_label = QLabel("总使用时间: 计算中...")
        self.total_usage_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.total_usage_label)

        # 添加每日使用时间进度条
        layout.addWidget(QLabel("每日使用时间分布:"))
        self.daily_usage_progress = QVBoxLayout()

        # 创建7天的进度条
        for i in range(7):
            progress_layout = QHBoxLayout()
            date_label = QLabel()
            progress_bar = QProgressBar()
            progress_label = QLabel("0 分钟")

            progress_layout.addWidget(date_label)
            progress_layout.addWidget(progress_bar)
            progress_layout.addWidget(progress_label)

            self.daily_usage_progress.addLayout(progress_layout)

        layout.addLayout(self.daily_usage_progress)

        self.overview_tab.setLayout(layout)

    def create_apps_tab(self):
        """创建应用使用情况标签页"""
        self.apps_tab = QWidget()
        layout = QVBoxLayout()

        # 添加标题
        title = QLabel("最近七天应用使用情况")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        # 创建应用使用时间表格
        self.apps_table = QTableWidget()
        self.apps_table.setColumnCount(3)
        self.apps_table.setHorizontalHeaderLabels(["应用名称", "总使用时间(分钟)", "占比"])
        self.apps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.apps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.apps_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.apps_table)

        # 添加刷新按钮
        refresh_button = QPushButton("刷新数据")
        refresh_button.clicked.connect(self.update_data)
        layout.addWidget(refresh_button, alignment=Qt.AlignRight)

        self.apps_tab.setLayout(layout)

    def update_data(self):
        """更新数据显示"""
        # 获取最近七天的使用数据
        recent_usage = self.tracker.get_recent_usage(days=7)

        # 更新总体使用情况标签页
        self.update_overview_tab(recent_usage)

        # 更新应用使用情况标签页
        self.update_apps_tab(recent_usage)

    def update_overview_tab(self, recent_usage):
        """更新总体使用情况标签页"""
        # 更新每日使用时间表格
        self.daily_usage_table.setRowCount(0)
        total_minutes = 0

        # 按日期排序
        sorted_dates = sorted(recent_usage["total_daily_usage"].items(), reverse=True)

        for date, seconds in sorted_dates:
            minutes = seconds / 60
            total_minutes += minutes

            row = self.daily_usage_table.rowCount()
            self.daily_usage_table.insertRow(row)

            # 设置日期
            date_item = QTableWidgetItem(date)
            self.daily_usage_table.setItem(row, 0, date_item)

            # 设置使用时间
            time_item = QTableWidgetItem(f"{minutes:.1f}")
            self.daily_usage_table.setItem(row, 1, time_item)

        # 更新总使用时间标签
        hours = total_minutes / 60
        self.total_usage_label.setText(f"总使用时间: {hours:.1f} 小时 ({total_minutes:.1f} 分钟)")

        # 更新每日进度条
        today = datetime.datetime.now()
        date_format = "%Y-%m-%d"

        for i in range(7):
            date = (today - datetime.timedelta(days=i)).strftime(date_format)
            seconds = recent_usage["total_daily_usage"].get(date, 0)
            minutes = seconds / 60

            # 设置日期标签
            date_label = self.daily_usage_progress.itemAt(i).layout().itemAt(0).widget()
            date_label.setText(date)

            # 设置进度条
            progress_bar = self.daily_usage_progress.itemAt(i).layout().itemAt(1).widget()
            
            # 计算最大分钟数，处理空数据的情况
            if recent_usage["total_daily_usage"].values():
                max_minutes = max(1, max(recent_usage["total_daily_usage"].values()) / 60)
            else:
                max_minutes = 1
            
            progress_bar.setMaximum(int(max_minutes))
            progress_bar.setValue(int(minutes))

            # 设置时间标签
            time_label = self.daily_usage_progress.itemAt(i).layout().itemAt(2).widget()
            time_label.setText(f"{minutes:.1f} 分钟")

    def update_apps_tab(self, recent_usage):
        """更新应用使用情况标签页"""
        # 获取使用时间最多的应用
        top_apps = self.tracker.get_top_apps(limit=10, days=7)

        # 清空表格
        self.apps_table.setRowCount(0)

        # 计算总使用时间，处理空数据的情况
        if top_apps:
            total_seconds = sum(app_data["total_time"] for _, app_data in top_apps)
            total_minutes = total_seconds / 60
        else:
            total_seconds = 0
            total_minutes = 0

        # 添加应用数据到表格
        if not top_apps:
            # 如果没有数据，添加提示信息
            row = self.apps_table.rowCount()
            self.apps_table.insertRow(row)
            no_data_item = QTableWidgetItem("暂无数据，请稍后再试")
            no_data_item.setTextAlignment(Qt.AlignCenter)
            self.apps_table.setItem(row, 0, no_data_item)
            
            # 为每个单元格创建单独的QTableWidgetItem
            time_item = QTableWidgetItem("暂无数据，请稍后再试")
            time_item.setTextAlignment(Qt.AlignCenter)
            self.apps_table.setItem(row, 1, time_item)
            
            percentage_item = QTableWidgetItem("暂无数据，请稍后再试")
            percentage_item.setTextAlignment(Qt.AlignCenter)
            self.apps_table.setItem(row, 2, percentage_item)
        else:
            # 添加应用数据到表格
            for app_name, app_data in top_apps:
                row = self.apps_table.rowCount()
                self.apps_table.insertRow(row)

                # 设置应用名称
                name_item = QTableWidgetItem(app_name)
                self.apps_table.setItem(row, 0, name_item)

                # 设置使用时间
                minutes = app_data["total_time"] / 60
                time_item = QTableWidgetItem(f"{minutes:.1f}")
                self.apps_table.setItem(row, 1, time_item)

                # 设置占比
                if total_seconds > 0:
                    percentage = (app_data["total_time"] / total_seconds) * 100
                    percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
                else:
                    percentage_item = QTableWidgetItem("0%")
                self.apps_table.setItem(row, 2, percentage_item)

    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止定时器
        self.update_timer.stop()
        event.accept()
