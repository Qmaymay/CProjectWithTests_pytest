#!/usr/bin/env python3
"""
在calculator_tests中运行，但调用根目录的测试脚本
详细调试(quick_test.bat的"增强版")
1, 专门解决PyCharm环境下的路径问题
2, 提供更详细的调试信息
3, 作为批处理文件的备份方案
"""

import subprocess   # 运行外部命令（如调用bat文件）
import sys
import os


def main():
    print("🎯 从calculator_tests调用根目录测试")

    # 获取项目根目录
    """
    abspath(__file__)：找到我自己的绝对位置
    两次dirname：从calculator_tests回到项目根目录
    拼出simple_test.py的完整路径   
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_test_script = os.path.join(project_root, "simple_test.py")


    print(f"项目根目录: {project_root}")
    print(f"测试脚本: {root_test_script}")

    # 总是重新创建测试脚本，确保使用最新版本
    print("🔄 确保使用最新测试脚本...")
    create_simple_test_script(project_root)  # 总是重新创建

    # 调用根目录的测试脚本
    print("\n🔧 调用根目录测试脚本...")
    result = subprocess.run([
        sys.executable,     # 用当前正在运行的Python
        root_test_script    # 要运行的脚本
    ], cwd=project_root)    # 在项目根目录运行

    if result.returncode == 0:
        print("\n🎉 测试完成！")
        return True
    else:
        print("\n💥 测试失败")
        return False


# 造物主函数 - 自动创建缺失的测试脚本
def create_simple_test_script(project_root):
    """如果simple_test.py不存在，创建它"""
    script_content = r'''#!/usr/bin/env python3
"""
最简单的测试脚本 - 使用现有的构建系统
在项目根目录运行
"""

import subprocess
import sys
import os
import glob

def main():
    print("🎯 简单测试开始")

    # 1. 使用现有的build.bat构建
    print("\n1️⃣ 使用build.bat构建...")
    result = subprocess.run("build.bat", shell=True)
    if result.returncode == 0:
        print("✅ 构建成功")
    else:
        print("❌ 构建失败")
        return False

    # 2. 检查库文件是否存在 - 修复路径问题
    build_lib_path = os.path.join("build", "lib")
    if os.path.exists(build_lib_path):
        # 查找实际的库文件
        dll_files = glob.glob(os.path.join(build_lib_path, "calculator_*.dll"))
        if dll_files:
            print(f"✅ 库文件存在: {dll_files[0]}")
        else:
            print(f"❌ 在 {build_lib_path} 中未找到库文件")
            return False
    else:
        print(f"❌ 构建目录不存在: {build_lib_path}")
        return False

    # 3. 运行测试
    print("\n2️⃣ 运行测试...")
    tests_dir = "calculator_tests"
    if os.path.exists(tests_dir):
        result = subprocess.run(
            "python test_runner.py", 
            shell=True, 
            cwd=tests_dir
        )
        if result.returncode == 0:
            print("\n🎉 所有测试通过！")
            return True
        else:
            print("\n💥 测试失败")
            return False
    else:
        print("❌ 测试目录不存在")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''

    script_path = os.path.join(project_root, "simple_test.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    print(f"✅ 已创建: {script_path}")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
