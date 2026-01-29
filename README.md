# AI-pets
# AI 宠物项目

An AI pet desktop application with cute companions.
一个具有可爱伙伴形象的桌面宠物应用程序。

这是一个使用 Qt for Python (PySide6) 开发的项目，具有可爱的虚拟宠物伴侣，支持多种可爱形象，如小猫、小狗、熊猫、简约风格和超可爱小兔子。

## Features
## 功能特性

- 可爱的虚拟宠物伴侣 (支持小猫、小狗、熊猫、简约风格和超可爱小兔子等形象)
- 桌面置顶显示
- 可拖拽移动
- 丰富的用户设置选项
- 使用时间统计功能
- 呼吸和眨眼动画效果

## Installation
## 安装说明

### Prerequisites
### 系统要求

- Python 3.12+
- conda (推荐使用Anaconda或Miniconda)

### Setup with Virtual Environment
### 使用虚拟环境安装

1. 创建并激活conda虚拟环境：
   ```bash
   conda create -n pet python=3.12
   conda activate pet
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## Usage
## 使用方法

运行应用程序：
```bash
python main.py
```

右键点击宠物窗口可以打开菜单，进行设置、查看使用统计等操作。

## Project Structure
## 项目结构

- `main.py` - 应用程序入口点
- `src/pet_window.py` - 桌面宠物主窗口类
- `src/pet_renderer.py` - 宠物形象渲染器 (包含多种可爱风格)
- `src/setting.py` - 设置管理类
- `src/settings_dialog.py` - 设置对话框
- `src/usage_stats_dialog.py` - 使用统计对话框
- `src/usage_tracker.py` - 使用情况追踪器

## version
## 版本信息

您可以在 `version.md` 文件中查看每个版本的变更内容。