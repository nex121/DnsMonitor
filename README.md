# DnsMonitor

# DNS请求监控工具

[![Python 3.7+](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

Windows版实时监控系统DNS请求，识别发起请求的进程信息，支持关键字匹配自动退出功能。

Linux版DNS请求监控工具请看这位仁兄文章：

https://zgao.top/%e5%bc%80%e5%8f%91ko%e5%86%85%e6%a0%b8%e6%a8%a1%e5%9d%97%ef%bc%8c%e6%97%a0%e4%be%9d%e8%b5%96%e5%ae%9e%e7%8e%b0%e7%9b%91%e6%8e%a7dns%e8%af%b7%e6%b1%82%e8%bf%9b%e7%a8%8b/

一键使用
```bash
wget https://zgao.top/download/dns_monitor.tgz && tar xvf dns_monitor.tgz && make && insmod dns_monitor.ko && dmesg -Tw
```

## 功能特性

- 🔍 实时捕获所有出站DNS查询
- 🖥️ 显示发起请求的进程信息（PID、程序路径）
- 🛠️ 自动识别Windows服务（特别是svchost.exe托管的服务）
- 🔔 支持关键字匹配自动退出功能
- 📂 自动处理网络数据包重定向（基于WinDivert）
- ⏱️ 带时间戳的格式化输出

## 安装要求

### 环境要求
- Windows 10/11 或 Windows Server 2016+
- Python 3.7 或更新版本
- 管理员权限（必需）

### 依赖安装
1. 安装Python依赖：
```bash
pip install pydivert psutil dnslib argparse
```

## 使用说明

### 基本用法
```bash
python dns_monitor.py
```

### 带关键字监控模式
```bash
python dns_monitor.py --keyword example.com
```

## 典型输出示例

![image](https://github.com/user-attachments/assets/0cba275a-507e-4705-968a-a9e175d449a8)


![image](https://github.com/user-attachments/assets/e5805d69-79f3-4957-be06-e5bf699e80a1)

## 高级应用

### 打包为可执行文件

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包命令
pyinstaller --console --onefile dns_monitor.py
```
![image](https://github.com/user-attachments/assets/5bc03713-5af5-4cd9-a581-8722106abd7e)

### 后台运行监控
```bash
@echo off
echo 启动DNS监控...
start /B dns_monitor.exe --keyword target-domain.com > log.txt 2>&1
```

