#!/usr/bin/env python3
"""
统一测试运行器 - 使用pytest
"""

import sys
import os
import subprocess
import pytest
from lib_loader import executable_files, get_lib_dir


# 添加项目根目录到路径，确保可以导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_executable_tests():
    """运行可执行文件测试"""
    if not executable_files:
        return False

    lib_dir = get_lib_dir()
    passed = 0

    for exe_file in executable_files:
        exe_path = os.path.join(lib_dir, exe_file)
        try:
            subprocess.run([exe_path], timeout=2, cwd=lib_dir, check=True, 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            passed += 1
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, Exception):
            pass

    return passed == len(executable_files)


def main():
    # 运行pytest测试
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [
        "test_interfaces.py",
        "security_tests.py", 
        "performance_tests.py"
    ]
    
    existing_test_files = [
        os.path.join(test_dir, f) for f in test_files 
        if os.path.exists(os.path.join(test_dir, f))
    ]
    
    if not existing_test_files:
        return 1

    # 运行pytest
    pytest_args = ["-v", "--tb=short"] + existing_test_files
    pytest_exit_code = pytest.main(pytest_args)
    
    # 运行可执行文件测试
    executable_passed = run_executable_tests()
    
    # 返回最终结果
    return 0 if (pytest_exit_code == 0 and executable_passed) else 1


if __name__ == "__main__":
    sys.exit(main())