#!/usr/bin/env python
"""
OpenBookShop 快速诊断脚本
检查 Django 环境、数据库连接、地址数据等
"""

import os
import sys
import subprocess

# 颜色输出
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(status, message):
    """打印格式化的状态"""
    if status == 'ok':
        print(f"{Color.GREEN}✅ {message}{Color.END}")
    elif status == 'error':
        print(f"{Color.RED}❌ {message}{Color.END}")
    elif status == 'warning':
        print(f"{Color.YELLOW}⚠️  {message}{Color.END}")
    else:
        print(f"{Color.BLUE}ℹ️  {message}{Color.END}")

def check_docker():
    """检查 Docker 状态"""
    print("\n" + "="*60)
    print("🐳 Docker 状态检查")
    print("="*60)
    
    try:
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                              capture_output=True, text=True, timeout=5)
        containers = result.stdout.strip().split('\n')
        
        openbookshop_containers = [c for c in containers if 'openbookshop' in c.lower()]
        
        if not openbookshop_containers:
            print_status('warning', "未发现 openbookshop 容器运行")
            return False
        
        print_status('ok', f"发现 {len(openbookshop_containers)} 个容器运行:")
        for container in openbookshop_containers:
            print(f"       - {container}")
        return True
        
    except Exception as e:
        print_status('error', f"Docker 检查失败: {e}")
        return False

def check_backend_logs():
    """检查后端初始化日志"""
    print("\n" + "="*60)
    print("📋 后端初始化日志检查")
    print("="*60)
    
    try:
        result = subprocess.run(
            ['docker', 'logs', 'openbookshop_backend'],
            capture_output=True, text=True, timeout=5
        )
        logs = result.stdout + result.stderr
        
        checks = {
            '✅ 创建收货地址': '地址数据初始化',
            '✅ 初始化仪表板完成': '仪表板数据初始化',
            'Starting Gunicorn': '后端服务启动'
        }
        
        for keyword, description in checks.items():
            if keyword in logs:
                print_status('ok', f"{description} - 已完成")
            else:
                print_status('warning', f"{description} - 未发现")
                
    except Exception as e:
        print_status('error', f"无法获取日志: {e}")

def check_database_addresses():
    """直接连接数据库检查地址"""
    print("\n" + "="*60)
    print("💾 数据库地址数据检查")
    print("="*60)
    
    try:
        result = subprocess.run(
            ['docker', 'exec', 'openbookshop_backend', 'python', 'manage.py', 
             'shell', '-c', 
             'from apps.users.models import User, Address; '
             'customer = User.objects.get(username="customer_test"); '
             'print("\\n✅ 找到用户:", customer.username); '
             '[print(f"  - {addr.name} ({addr.province}{addr.city}) - 默认: {addr.is_default}") '
             'for addr in customer.addresses.all()]'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout
            print(output)
            
            if '张三' in output and '李四' in output:
                print_status('ok', "地址数据完整性确认")
                return True
            else:
                print_status('warning', "部分地址数据缺失")
                return False
        else:
            print_status('warning', result.stderr)
            return False
            
    except Exception as e:
        print_status('error', f"无法检查数据库: {e}")
        return False

def check_api_endpoint():
    """检查 API 端点"""
    print("\n" + "="*60)
    print("🔗 API 端点检查")
    print("="*60)
    
    try:
        import urllib.request
        import json
        
        # 注意: 这个检查需要后端已启动，可能需要认证
        print_status('info', "配置步骤:")
        print("""
  1. 在浏览器中打开: http://127.0.0.1:8080
  2. 登录账户: customer_test / customer123456
  3. 打开浏览器开发者工具 (F12)
  4. 在 Network 标签中查看请求
  5. 查找 GET /api/users/addresses/ 
  6. 检查返回状态码是否为 200
  7. 在 Response 标签中应该看到地址数据
        """)
        
    except Exception as e:
        print_status('error', f"API 检查失败: {e}")

def check_frontend():
    """检查前端状态"""
    print("\n" + "="*60)
    print("🎨 前端状态检查")
    print("="*60)
    
    try:
        result = subprocess.run(
            ['docker', 'exec', 'openbookshop_frontend', 'ps', 'aux'],
            capture_output=True, text=True, timeout=5
        )
        
        if 'nginx' in result.stdout:
            print_status('ok', "前端 Nginx 服务正在运行")
            print_status('info', "访问地址: http://127.0.0.1:8080")
        else:
            print_status('warning', "前端服务状态未知")
            
    except Exception as e:
        print_status('error', f"无法检查前端: {e}")

def print_recommendations():
    """打印建议"""
    print("\n" + "="*60)
    print("💡 建议的后续步骤")
    print("="*60)
    print("""
1️⃣  Pylance 配置:
   - 打开 VS Code 命令面板 (Ctrl+Shift+P)
   - 输入: Python: Select Interpreter
   - 选择: ./openbookshop/backend/venv/Scripts/python.exe
   
2️⃣  查看地址:
   - 访问: http://127.0.0.1:8080
   - 登录: customer_test / customer123456
   - 进入: 个人中心 → 我的地址
   
3️⃣  调试前端:
   - 打开浏览器 F12 开发者工具
   - 在 Network 标签查看 API 调用
   - 在 Console 标签查看错误信息

4️⃣  如果地址仍未显示:
   - 清除浏览器缓存 (Ctrl+Shift+Del)
   - 重新登录
   - 或运行完全重启:
     docker-compose down -v && docker-compose up -d --build
    """)

def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔍 OpenBookShop 快速诊断工具")
    print("="*60)
    
    # 运行所有检查
    has_docker = check_docker()
    
    if has_docker:
        check_backend_logs()
        has_addresses = check_database_addresses()
        check_api_endpoint()
        check_frontend()
    
    # 打印建议
    print_recommendations()
    
    print("\n" + "="*60)
    print("📚 完整指南: PYLANCE_AND_ADDRESS_GUIDE.md")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
