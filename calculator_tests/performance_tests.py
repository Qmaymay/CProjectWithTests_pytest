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
        times.append((end_time - start_time) * 1000000)
    return times



# 多库测试固件
@pytest.fixture(params=library_files if library_files else [], scope="function")
def lib(request):
    """为每个库提供实例"""
    lib_file = request.param
    lib_path = os.path.join(get_lib_dir(), lib_file)

     # 文件不存在时直接报错，因为这是配置问题
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"测试库文件不存在: {lib_path}")
    
    lib = ctypes.CDLL(lib_path)
    setup_library_functions(lib)
    return lib


class TestPerformance:
    """性能测试类 - 精简版"""
    
    # 性能阈值（微秒）
    THRESHOLDS = {
        "add": 1000, "subtract": 1000, "multiply": 2000, "divide": 5000,
        "square": 1500, "cube": 2000, "sqrt_calc": 8000, "power": 10000, 
        "trig_calc": 20000
    }
    
    # 核心测试操作
    CORE_TESTS = [
        ("add", (100, 200)),
        ("multiply", (50, 60)), 
        ("divide", (100, 3)),
        ("sqrt_calc", (16.0,)),
        ("power", (2.0, 3.0)),
        ("trig_calc", (30.0, "degrees", "sin")),
    ]


    def test_basic_performance(self, lib):
        """基础性能测试 - 最终精简版"""
        print(f"\n🔍 性能测试: current_lib")
        
        for name, args, needs_error in [
            ("add", (100, 200), False),
            ("multiply", (50, 60), False),
            ("divide", (100, 3), True),
            ("sqrt_calc", (16.0,), True),
            ("power", (2.0, 3.0), True),
            ("trig_calc", (30.0, b"degrees", b"sin"), True),  # 直接使用字节字符串
        ]:
            error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
            actual_args = (*args, ctypes.byref(error)) if needs_error else args
            
            func = getattr(lib, name)
            times = time_function(func, *actual_args, iterations=100)
            avg_time = statistics.mean(times)
            
            if needs_error and error.value != CalcErrorCode.CALC_SUCCESS:
                print(f"  ⚠️ {name}: 错误码 {error.value}")
                continue
            
            threshold = self.THRESHOLDS[name]
            status = "✅" if avg_time < threshold else "❌"
            print(f"  {status} {name}: {avg_time:.2f} μs")
            assert avg_time < threshold, f"{name}性能异常"
        
        print("\n🎯 性能测试完成")



    def test_throughput(self, lib):
        """吞吐量测试"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        operations = 1000
        start_time = time.perf_counter()

        # 可配置的操作序列
        operations_sequence = [
            lambda i: lib.add(i, 1),                                           # 加法
            lambda i: lib.multiply(i, 2),                                      # 乘法  
            lambda i: lib.divide(i + 1, 3, ctypes.byref(error)),               # 除法
            lambda i: lib.sqrt_calc(i + 1, ctypes.byref(error)),               # 平方根
            lambda i: lib.power(2.0, 3.0, ctypes.byref(error)),                # 幂运算
            lambda i: lib.trig_calc(i % 360, b"degrees", b"sin", ctypes.byref(error)),  # 正弦
        ]

        # 执行操作序列
        for i in range(operations):
            op_func = operations_sequence[i % len(operations_sequence)]
            op_func(i)

        total_time = time.perf_counter() - start_time
        throughput = operations / total_time
        
        print(f"🚀 吞吐量: {throughput:.0f} 操作/秒 (混合{len(operations_sequence)}种操作)")
        assert throughput > 10, f"吞吐量过低: {throughput:.0f} 操作/秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])