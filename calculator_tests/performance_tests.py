#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算器性能测试 - 响应时间、吞吐量测试
使用pytest框架
"""

import ctypes
import sys
import os
import time
import statistics
import pytest

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib_loader import library_files, get_lib_dir
from test_interfaces import setup_library_functions, CalcErrorCode


def time_function(func, *args, iterations=1000):
    """测量函数执行时间"""
    times = []
    for _ in range(iterations):
        start_time = time.perf_counter()
        func(*args)
        end_time = time.perf_counter()
        times.append((end_time - start_time) * 1000000)  # 转换为微秒
    return times


# 多库测试固件
@pytest.fixture(params=library_files if library_files else [], scope="function")
def lib(request):
    """为每个库提供实例"""
    lib_file = request.param
    lib_path = os.path.join(get_lib_dir(), lib_file)
    lib = ctypes.CDLL(lib_path)
    setup_library_functions(lib)
    return lib


class TestPerformance:
    """性能测试类"""

    @pytest.mark.parametrize("operation_name,func_name,args", [
        ("加法", "add", (123, 456)),
        ("减法", "subtract", (456, 123)),
        ("乘法", "multiply", (123, 456)),
        ("除法", "divide", (1000, 3)),
        ("平方", "square", (25,)),
        ("立方", "cube", (10,)),
    ])
    def test_operation_performance(self, lib, operation_name, func_name, args):
        """测试运算性能"""
        # 为需要错误参数的操作特殊处理
        if func_name == "divide":
            error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
            actual_args = (args[0], args[1], ctypes.byref(error))
        else:
            actual_args = args
        
        func = getattr(lib, func_name)
        times = time_function(func, *actual_args, iterations=100)
        avg_time = statistics.mean(times)
        
        print(f"📊 {operation_name}: {avg_time:.2f} μs")
        assert avg_time < 10000, f"{operation_name}性能异常: {avg_time:.2f} μs"

    def test_throughput(self, lib):
        """测试吞吐量"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        operations = 1000
        start_time = time.perf_counter()

        for i in range(operations):
            if i % 4 == 0:
                lib.add(i, 1)
            elif i % 4 == 1:
                lib.multiply(i, 2)
            elif i % 4 == 2:
                lib.divide(i + 1, 3, ctypes.byref(error))

        total_time = time.perf_counter() - start_time
        throughput = operations / total_time

        print(f"🚀 吞吐量: {throughput:.0f} 操作/秒")
        assert throughput > 10, f"吞吐量过低: {throughput:.0f} 操作/秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])