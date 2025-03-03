import pydivert
import psutil
import time
import argparse
import signal
from dnslib import DNSRecord
import subprocess

# 全局标志用于控制循环退出
exit_flag = False
pid_cache = {}


def signal_handler(sig, frame):
    global exit_flag
    print("\n检测到Ctrl+C，正在退出...")
    exit_flag = True


signal.signal(signal.SIGINT, signal_handler)


def find_process_by_local_port(port, protocol="udp"):
    """根据本地端口查找对应的进程ID"""
    try:
        for conn in psutil.net_connections(kind=protocol):
            if conn.laddr and conn.laddr.port == port:
                return conn.pid
    except Exception as e:
        print(f"查询端口时出错: {e}")
    return None


def get_process_info(pid):
    """通过PID获取进程信息（带缓存）"""
    if pid in pid_cache:
        return pid_cache[pid]

    try:
        proc = psutil.Process(pid)
        exe_path = proc.exe()
        service_info = ""

        if "svchost.exe" in exe_path:
            try:
                services = get_service_name_by_pid(pid)
                service_info = f" | 服务: {services}" if services else ""
            except Exception as e:
                service_info = f" | 服务查询失败: {e}"

        result = (exe_path, service_info)
        pid_cache[pid] = result
        return result
    except psutil.NoSuchProcess:
        return ("进程已退出", "")
    except Exception as e:
        return (f"信息获取失败: {e}", "")


def get_service_name_by_pid(pid):
    """通过PID查询Windows服务名称"""
    try:
        cmd = f"Get-WmiObject Win32_Service | Where-Object {{ $_.ProcessId -eq {pid} }} | Select-Object -ExpandProperty DisplayName"
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        services = result.stdout.strip().split('\n')
        return ", ".join(filter(None, services)) if services else "无关联服务"
    except subprocess.CalledProcessError as e:
        return f"PowerShell错误: {e.stderr.strip()}"
    except Exception as e:
        return f"常规错误: {str(e)}"


def should_exit(domain, keyword):
    """检查域名是否包含关键字"""
    return keyword and keyword.lower() in domain.lower()


def main():
    parser = argparse.ArgumentParser(description="DNS请求监控工具")
    parser.add_argument("--keyword", type=str, help="匹配的关键字，匹配后程序退出")
    args = parser.parse_args()

    filter_str = "outbound and udp.DstPort == 53"
    print(f"启动抓包，过滤条件：{filter_str}")
    if args.keyword:
        print(f"监控关键字: {args.keyword}，匹配后程序将退出")

    with pydivert.WinDivert(filter_str) as w:
        while not exit_flag:
            try:
                packet = w.recv()
            except pydivert.WinDivertException as e:
                if not exit_flag:
                    print(f"捕获数据包时出错: {e}")
                continue

            src_port = packet.src_port
            pid = find_process_by_local_port(src_port) or "未知"

            # 获取进程信息
            exe_path, service_info = ("未知", "") if pid == "未知" else get_process_info(pid)

            # 解析DNS查询
            try:
                dns = DNSRecord.parse(packet.payload)
                domain = str(dns.questions[0].qname) if dns.questions else "无域名信息"
            except Exception as e:
                domain = f"解析失败: {str(e)}"

            output = (
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] DNS请求: "
                f"源端口 {src_port}, 域名: {domain}, "
                f"PID: {pid}, 程序路径: {exe_path}{service_info}"
            )
            print(output)

            # 关键字匹配检查
            if should_exit(domain, args.keyword):
                print(f"\n检测到关键字 '{args.keyword}' 在域名 '{domain}' 中")
                print("触发退出的进程信息：")
                print(output)
                return

            # 重新发送数据包
            try:
                packet.recalculate_checksums()
                w.send(packet)
            except Exception as e:
                print(f"发送数据包失败: {e}")


if __name__ == '__main__':
    main()
    print("程序已安全退出")
