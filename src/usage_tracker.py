
import os
import json
import time
import datetime
import psutil
import threading
import winreg
from collections import defaultdict
from PySide6.QtCore import QStandardPaths, QTimer

class UsageTracker:
    def __init__(self):
        self.data_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "DesktopPet")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.usage_data_file = os.path.join(self.data_dir, "usage_data.json")
        self.current_process_data_file = os.path.join(self.data_dir, "current_process_data.json")

        self.installed_software = self._get_installed_software()

        self.current_processes = {}
        self.last_update_time = time.time()
        self.load_usage_data()
        self.start_monitoring()

    def _get_installed_software(self):
        software_map = {}

        try:
            roots = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            ]

            for root, subkey_path in roots:
                try:
                    with winreg.OpenKey(root, subkey_path) as key:
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]

                                        try:
                                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                            if install_location:
                                                for file in os.listdir(install_location):
                                                    if file.lower().endswith(('.exe', '.bat', '.cmd')):
                                                        exe_name = file.lower()
                                                        software_map[exe_name] = name
                                                        break
                                        except (WindowsError, OSError):
                                            pass

                                        try:
                                            uninstall_string = winreg.QueryValueEx(subkey, "UninstallString")[0]
                                            if uninstall_string:
                                                if ".exe" in uninstall_string:
                                                    exe_path = uninstall_string.split('"')[-1].split('"')[0]
                                                    exe_name = os.path.basename(exe_path).lower()
                                                    if exe_name not in software_map:
                                                        software_map[exe_name] = name
                                        except (WindowsError, OSError):
                                            pass
                                    except (WindowsError, OSError):
                                        pass
                                i += 1
                            except WindowsError:
                                break
                except WindowsError:
                    continue
        except Exception as e:
            print(f"获取已安装软件时出错: {e}")

        return software_map

    def load_usage_data(self):
        if os.path.exists(self.usage_data_file):
            with open(self.usage_data_file, 'r') as f:
                loaded_data = json.load(f)
                self.usage_data = defaultdict(lambda: {
                    "total_time": 0,
                    "daily_breakdown": defaultdict(int),
                    "last_updated": time.time()
                })
                self.usage_data.update(loaded_data)
                for app_name in self.usage_data:
                    if isinstance(self.usage_data[app_name]["daily_breakdown"], dict):
                        self.usage_data[app_name]["daily_breakdown"] = defaultdict(int, self.usage_data[app_name]["daily_breakdown"])
        else:
            self.usage_data = defaultdict(lambda: {
                "total_time": 0,
                "daily_breakdown": defaultdict(int),
                "last_updated": time.time()
            })

    def save_usage_data(self):
        with open(self.usage_data_file, 'w') as f:
            json.dump(self.usage_data, f, indent=4)

    def save_current_process_data(self):
        with open(self.current_process_data_file, 'w') as f:
            json.dump(self.current_processes, f, indent=4)

    def _is_system_process(self, proc_name, exe_path, pid):
        if not exe_path:
            return True

        exe_full_path = os.path.normpath(exe_path).lower()
        system_dirs = [
            os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32'),
            os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'SysWOW64'),
            os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System'),
            os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), 'Windows Defender'),
            os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'), 'Windows Defender')
        ]
        
        for sys_dir in system_dirs:
            if exe_full_path.startswith(sys_dir.lower()):
                return True

        system_keywords = [
            'system', 'windows', 'microsoft', 'svchost', 'csrss', 'lsass', 
            'wininit', 'services', 'smss', 'winlogon', 'rundll32', 'dllhost',
            'audiodg', 'fontdrvhost', 'wudfhost', 'consol', 'powershell',
            'cmd', 'explorer', 'dwm', 'sihost', 'taskhost', 'services'
        ]
        
        additional_system_processes = [
            'wudfhost.exe',  # Windows User Mode Driver Framework Host
            'mbamessagecenter.exe',  # Malwarebytes Message Center
            'mbam.exe',  # Malwarebytes
            'mbamservice.exe',  # Malwarebytes Service
            'mbamtray.exe',  # Malwarebytes Tray
            'mbamupdates.exe',  # Malwarebytes Updates
            'conhost.exe',  # Console Host
            'wininit.exe',  # Windows Initialization
            'csrss.exe',  # Client Server Runtime Process
            'lsass.exe',  # Local Security Authority Subsystem
            'lsm.exe',  # Local Session Manager
            'svchost.exe',  # Host Process for Windows Services
            'services.exe',  # Windows Services
            'smss.exe',  # Windows Session Manager
            'winlogon.exe',  # Windows Logon Application
            'userinit.exe',  # Windows Logon Application
            'explorer.exe',  # Windows Explorer
            'taskmgr.exe',  # Windows Task Manager
            'dwm.exe',  # Desktop Window Manager
            'sihost.exe',  # System Host
            'taskhost.exe',  # Host Process for Windows Tasks
            'taskhostex.exe',  # Host Process for Windows Tasks
            'rundll32.exe',  # Windows Host Process
            'dllhost.exe',  # COM+ Application
            'audiodg.exe',  # Windows Audio Device Graph
            'fontdrvhost.exe',  # Font Driver Host
            'svchost.exe',  # Host Process for Windows Services
            'spoolsv.exe',  # Print Spooler
            'lexbces.exe',  # Lexmark BCES Service
            'lexbces.exe',  # Lexmark BCES Service
            'jusched.exe',  # Java Update Scheduler
            'jucheck.exe',  # Java Update Checker
            'googleupdate.exe',  # Google Update
            'chrome.exe',  # Google Chrome (helper processes)
            'firefox.exe',  # Firefox (helper processes)
            'msedge.exe',  # Microsoft Edge (helper processes)
            'steam.exe',  # Steam (helper processes)
            'discord.exe',  # Discord (helper processes)
        ]
        
        proc_name_lower = proc_name.lower()

        if proc_name_lower in [p.lower() for p in additional_system_processes]:
            return True
        for keyword in system_keywords:
            if keyword in proc_name_lower:
                return True
                
        try:
            cmdline = psutil.Process(pid).cmdline()
            if cmdline and any('system' in arg.lower() or 'windows' in arg.lower() for arg in cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
                
        try:
            parent = psutil.Process(pid).ppid()
            if parent:
                parent_proc = psutil.Process(parent)
                parent_name = parent_proc.name().lower()
                if any(keyword in parent_name for keyword in system_keywords):
                    return True
                    
                try:
                    parent_exe = parent_proc.exe()
                    if parent_exe:
                        parent_exe_path = os.path.normpath(parent_exe).lower()
                        for sys_dir in system_dirs:
                            if parent_exe_path.startswith(sys_dir.lower()):
                                return True
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
        try:
            proc_username = psutil.Process(pid).username()
            if proc_username and ('SYSTEM' in proc_username or 'LOCAL SERVICE' in proc_username or 'NETWORK SERVICE' in proc_username):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
        return False
    
    def get_active_processes(self):
        processes = {}
        must_ignore = {
            'System', 'System Idle Process', 'csrss.exe', 'lsass.exe', 
            'services.exe', 'svchost.exe', 'wininit.exe', 'audiodg.exe'
        }
        
        for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cpu_times', 'exe']):
            try:
                proc_info = proc.info
                pid = proc_info['pid']
                proc_name = proc_info['name']
                exe_path = proc_info.get('exe', '')
                
                software_name = proc_name
                
                if exe_path:
                    exe_file = os.path.basename(exe_path).lower()
                    if exe_file in self.installed_software:
                        software_name = self.installed_software[exe_file]
                    elif exe_file.endswith('.exe'):
                        exe_name_without_ext = exe_file[:-4]
                        if exe_name_without_ext in self.installed_software:
                            software_name = self.installed_software[exe_name_without_ext]

                if proc_name in must_ignore or self._is_system_process(proc_name, exe_path, pid):
                    continue
                    
                processes[pid] = {
                    'name': proc_name,
                    'software_name': software_name,
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

        if time_diff < 0.1:
            time_diff = 0.1
        active_processes = self.get_active_processes()
        for pid, proc_data in active_processes.items():
            if pid in self.current_processes:
                time_increment = (
                    proc_data['cpu_time'].user - self.current_processes[pid]['cpu_time'].user +
                    proc_data['cpu_time'].system - self.current_processes[pid]['cpu_time'].system
                )

                software_name = proc_data.get('software_name', proc_data['name'])
                self.usage_data[software_name]['total_time'] += time_increment

                today = datetime.datetime.now().strftime("%Y-%m-%d")
                self.usage_data[software_name]['daily_breakdown'][today] += time_increment
                self.usage_data[software_name]['last_updated'] = current_time
            else:
                self.current_processes[pid] = {
                    'name': proc_data['name'],
                    'software_name': proc_data.get('software_name', proc_data['name']),
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
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def _monitoring_loop(self):
        while True:
            try:
                self.update_process_data()
                time.sleep(5)
            except Exception as e:
                print(f"监控过程中发生错误: {e}")
                time.sleep(10)

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
            actual_days = days
            
            for i in range(actual_days):
                date = (today - datetime.timedelta(days=i)).strftime(date_format)
                if date in app_data['daily_breakdown']:
                    recent_time += app_data['daily_breakdown'][date]

            if recent_time > 0:
                result["app_usage"][app_name] = {
                    "total_time": recent_time,
                    "daily_breakdown": {}
                }
                for i in range(actual_days):
                    date = (today - datetime.timedelta(days=i)).strftime(date_format)
                    result["app_usage"][app_name]["daily_breakdown"][date] = app_data['daily_breakdown'].get(date, 0)
                    result["total_daily_usage"][date] += app_data['daily_breakdown'].get(date, 0)

        result["total_daily_usage"] = dict(sorted(result["total_daily_usage"].items()))

        return result

    def get_top_apps(self, limit=None, days=1):
        recent_usage = self.get_recent_usage(days)
        sorted_apps = sorted(
            recent_usage["app_usage"].items(), 
            key=lambda x: x[1]["total_time"], 
            reverse=True
        )
        if limit is None or limit >= len(sorted_apps):
            return sorted_apps
        return sorted_apps[:limit]
