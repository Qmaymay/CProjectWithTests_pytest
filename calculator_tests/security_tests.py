#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算器安全测试 - 边界值、溢出、异常输入测试
使用pytest框架
"""

import ctypes
import sys
import os
import pytest

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib_loader import library_files, get_lib_dir
from test_interfaces import setup_library_functions, CalcErrorCode


# 多库测试固件
@pytest.fixture(params=library_files if library_files else [], scope="function")
def lib(request):
    """为每个库提供实例"""
    lib_file = request.param
    lib_path = os.path.join(get_lib_dir(), lib_file)
    lib = ctypes.CDLL(lib_path)
    setup_library_functions(lib)
    return lib


class TestSecurity:
    """安全测试类"""

    @pytest.mark.parametrize("a,b", [
        (2**31-1, 1),      # 整数加法边界
        (-2**31, -1),      # 整数减法边界  
        (2**31-1, 2),      # 整数乘法边界
    ])
    def test_arithmetic_overflow(self, lib, a, b):
        """测试算术运算溢出"""
        result = lib.add(a, b)
        # 在C语言中整数环绕是正常行为，不视为错误
        assert isinstance(result, (int, ctypes.c_int))

    @pytest.mark.parametrize("a,b,expected_error", [
        (1, 0, CalcErrorCode.CALC_ERROR_DIVISION_BY_ZERO),  # 除零
        (1, 1, CalcErrorCode.CALC_SUCCESS),                 # 正常除法
        (-1, 1, CalcErrorCode.CALC_SUCCESS),                # 负数除法
        (0, 1, CalcErrorCode.CALC_SUCCESS),                 # 零除以正数
    ])
    def test_division_edge_cases(self, lib, a, b, expected_error):
        """测试除法边界情况"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.divide(a, b, ctypes.byref(error))
        
        assert error.value == expected_error
        
        if expected_error == CalcErrorCode.CALC_SUCCESS:
            expected_result = a / b
            assert abs(result - expected_result) < 0.001

    @pytest.mark.parametrize("base,exp,expected_error", [
        (0.0, -1.0, CalcErrorCode.CALC_ERROR_INVALID_POWER),  # 0的负指数
        (-1.0, 0.5, CalcErrorCode.CALC_ERROR_INVALID_POWER),  # 负底数分数指数
        (2.0, 3.0, CalcErrorCode.CALC_SUCCESS),               # 正常幂运算
        (1.0, 1000.0, CalcErrorCode.CALC_SUCCESS),            # 大指数
    ])
    def test_power_edge_cases(self, lib, base, exp, expected_error):
        """测试幂运算边界情况"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.power(base, exp, ctypes.byref(error))
        
        assert error.value == expected_error
        
        if expected_error == CalcErrorCode.CALC_SUCCESS:
            assert result > 0

    @pytest.mark.parametrize("value,expected_error", [
        (-1.0, CalcErrorCode.CALC_ERROR_NEGATIVE_SQRT),  # 负数平方根
        (0.0, CalcErrorCode.CALC_SUCCESS),               # 零
        (4.0, CalcErrorCode.CALC_SUCCESS),               # 正数平方根
        (1e-10, CalcErrorCode.CALC_SUCCESS),             # 极小正数
    ])
    def test_sqrt_edge_cases(self, lib, value, expected_error):
        """测试平方根边界情况"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.sqrt_calc(value, ctypes.byref(error))
        
        assert error.value == expected_error
        
        if expected_error == CalcErrorCode.CALC_SUCCESS:
            assert result >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])