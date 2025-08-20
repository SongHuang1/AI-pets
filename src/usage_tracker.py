
import os
import json
import time
import datetime
import psutil
import threading
from collections import defaultdict
from PySide6.QtCore import QStandardPaths, QTimer

class UsageTracker:
    def __init__(self):
        self.data_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "DesktopPet")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.usage_data_file = os.path.join(self.data_dir, "usage_data.json")
        self.current_process_data_file = os.path.join(self.data_dir, "current_process_data.json")

        self.current_processes = {}
        self.last_update_time = time.time()
        self.load_usage_data()
        self.start_monitoring()

    def load_usage_data(self):
        if os.path.exists(self.usage_data_file):
            with open(self.usage_data_file, 'r') as f:
                self.usage_data = json.load(f)
        else:
            self.usage_data = defaultdict(lambda: {
                "total_time": 0,
                "daily_breakdown": defaultdict(int),
                "last_updated": time.time()
            })

    def save_usage_data(self):
        """保存使用数据到文件"""
        with open(self.usage_data_file, 'w') as f:
            json.dump(self.usage_data, f, indent=4)

    def save_current_process_data(self):
        with open(self.current_process_data_file, 'w') as f:
            json.dump(self.current_processes, f, indent=4)

    def get_active_processes(self):
        processes = {}
        # 忽略的系统进程列表
        ignored_processes = {
            'System', 'System Idle Process', 'csrss.exe', 'lsass.exe', 
            'services.exe', 'svchost.exe', 'wininit.exe', 'audiodg.exe'
        }
        
        for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cpu_times']):
            try:
                proc_info = proc.info
                pid = proc_info['pid']
                proc_name = proc_info['name']
                
                # 跳过系统进程
                if proc_name in ignored_processes:
                    continue
                    
                processes[pid] = {
                    'name': proc_name,
                    'create_time': proc_info['create_time'],
                    'cpu_time': proc_info['cpu_times']
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                print(f"获取进程信息时出错: {e}")
                continue
        return processes

    def update_process_data(self):
        current_time = time.time()
        time_diff = current_time - self.last_update_time

        # 如果时间差非常小（例如小于0.1秒），仍然继续处理
        if time_diff < 0.1:
            time_diff = 0.1
        active_processes = self.get_active_processes()
        for pid, proc_data in active_processes.items():
            if pid in self.current_processes:
                cpu_time_diff = (
                    proc_data['cpu_time'].user - self.current_processes[pid]['cpu_time'].user +
                    proc_data['cpu_time'].system - self.current_processes[pid]['cpu_time'].system
                )

                time_increment = cpu_time_diff
                self.usage_data[proc_data['name']]['total_time'] += time_increment

                today = datetime.datetime.now().strftime("%Y-%m-%d")
                self.usage_data[proc_data['name']]['daily_breakdown'][today] += time_increment
                self.usage_data[proc_data['name']]['last_updated'] = current_time
            else:
                self.current_processes[pid] = {
                    'name': proc_data['name'],
                    'create_time': proc_data['create_time'],
                    'cpu_time': proc_data['cpu_time']
                }
        pids_to_remove = [pid for pid in self.current_processes if pid not in active_processes]
        for pid in pids_to_remove:
            del self.current_processes[pid]

        self.save_usage_data()
        self.save_current_process_data()
        self.last_update_time = current_time

    def start_monitoring(self):
        self.update_process_data()
        
        # 启动后台监控线程
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def _monitoring_loop(self):
        """后台监控循环"""
        while True:
            try:
                self.update_process_data()
                time.sleep(5)  # 每5秒更新一次
            except Exception as e:
                # 只记录特定错误，避免日志过于冗长
                if "audiodg.exe" not in str(e):
                    print(f"监控过程中发生错误: {e}")
                time.sleep(10)  # 出错后等待10秒再重试

    def get_recent_usage(self, days=7):
        result = {
            "total_daily_usage": defaultdict(int),
            "app_usage": {}
        }

        today = datetime.datetime.now()
        date_format = "%Y-%m-%d"

        all_apps = set()
        for app_name, app_data in self.usage_data.items():
            all_apps.add(app_name)

            recent_time = 0
            for i in range(days):
                date = (today - datetime.timedelta(days=i)).strftime(date_format)
                if date in app_data['daily_breakdown']:
                    recent_time += app_data['daily_breakdown'][date]

            if recent_time > 0:
                result["app_usage"][app_name] = {
                    "total_time": recent_time,
                    "daily_breakdown": {}
                }
                for i in range(days):
                    date = (today - datetime.timedelta(days=i)).strftime(date_format)
                    result["app_usage"][app_name]["daily_breakdown"][date] = app_data['daily_breakdown'].get(date, 0)
                    result["total_daily_usage"][date] += app_data['daily_breakdown'].get(date, 0)

        result["total_daily_usage"] = dict(sorted(result["total_daily_usage"].items()))

        return result

    def get_top_apps(self, limit=10, days=7):
        recent_usage = self.get_recent_usage(days)
        sorted_apps = sorted(
            recent_usage["app_usage"].items(), 
            key=lambda x: x[1]["total_time"], 
            reverse=True
        )
        return sorted_apps[:limit]
