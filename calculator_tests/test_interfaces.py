#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ctypes
import sys
import os
import pytest

from test_version import get_test_version
from lib_loader import library_files, get_lib_dir


class CalcErrorCode(ctypes.c_int):
    CALC_SUCCESS = 0
    CALC_ERROR_DIVISION_BY_ZERO = -1
    CALC_ERROR_NEGATIVE_SQRT = -2
    CALC_ERROR_INVALID_POWER = -3
    CALC_ERROR_INVALID_TRIG = -4
    CALC_ERROR_INVALID_INPUT = -5
    CALC_ERROR_TANGENT_UNDEFINED = -6


def setup_library_functions(lib):
    """为库设置函数原型 - 使用正确的类型"""
    # 基本运算
    lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.add.restype = ctypes.c_int

    lib.subtract.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.subtract.restype = ctypes.c_int

    lib.multiply.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.multiply.restype = ctypes.c_int

    # 除法和高级运算
    lib.divide.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(CalcErrorCode)]
    lib.divide.restype = ctypes.c_double  # 根据你的C头文件，应该返回double

    lib.square.argtypes = [ctypes.c_int]
    lib.square.restype = ctypes.c_int

    lib.cube.argtypes = [ctypes.c_int]
    lib.cube.restype = ctypes.c_int

    lib.sqrt_calc.argtypes = [ctypes.c_double, ctypes.POINTER(CalcErrorCode)]
    lib.sqrt_calc.restype = ctypes.c_double

    lib.power.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.POINTER(CalcErrorCode)]
    lib.power.restype = ctypes.c_double

     # 添加三角函数原型
    lib.trig_calc.argtypes = [
        ctypes.c_double,           # input
        ctypes.c_char_p,           # angle_mode  
        ctypes.c_char_p,           # func
        ctypes.POINTER(CalcErrorCode)  # error
    ]
    lib.trig_calc.restype = ctypes.c_double


# 多库测试固件
@pytest.fixture(params=library_files if library_files else [])
def lib(request):
    """为每个库提供实例"""
    lib_file = request.param
    lib_path = os.path.join(get_lib_dir(), lib_file)

    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"测试库文件不存在: {lib_path}")
    
    # 加载动态库 使用CDLL（根据你的C库编译设置）—— 把C库变成Python对象
    lib = ctypes.CDLL(lib_path)

    # 配置接口——告诉Python如何与C函数交互
    setup_library_functions(lib)
    return lib

def test_fixture_debug(lib):
    """调试fixture是否正常工作"""
    print(f"lib类型: {type(lib)}")
    print(f"lib属性: {dir(lib)}")
    # 检查是否有C库函数
    if hasattr(lib, 'add'):
        print("✅ fixture工作正常")
    else:
        print("❌ fixture有问题")

class TestBasicOperations: 
# 基本运算测试 ---------------------------------------------------
    def test_add(self, lib):
        """测试加法"""
        result = lib.add(10, 5)
        assert result == 15


    def test_subtract(self, lib):
        """测试减法"""
        result = lib.subtract(10, 5)
        assert result == 5


    def test_multiply(self, lib):
        """测试乘法"""
        result = lib.multiply(10, 5)
        assert result == 50

    def test_square(self, lib):
        """测试平方"""
        result = lib.square(5)
        assert result == 25


    def test_cube(self, lib):
        """测试立方"""
        result = lib.cube(3)
        assert result == 27


# 除法测试 ---------------------------------------------------
class TestDivideFunction:     
    @pytest.mark.parametrize("a,b,expected", [
        (10, 5, 2.0),    # 基础整数除法
        (1, 2, 0.5),     # 小数结果
        (-10, 2, -5.0),  # 负数除法
    ])
    def test_divide_success(self, lib, a, b, expected):
        """测试除法成功情况"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.divide(a, b, ctypes.byref(error))
        
        print(f"✅ {a}/{b} = {result}")
        assert error.value == CalcErrorCode.CALC_SUCCESS
        assert abs(result - expected) < 0.0001

    @pytest.mark.parametrize("a,b", [
        (10, 0),    # 正数除零
        (-5, 0),    # 负数除零
        (0, 0),     # 零除零
    ])
    def test_divide_errors(self, lib, a, b):
        """测试除法错误处理"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.divide(a, b, ctypes.byref(error))
        
        print(f"❌ {a}/{b} = {result}, 错误码: {error.value}")
        assert error.value == CalcErrorCode.CALC_ERROR_DIVISION_BY_ZERO
        assert result == 0.0


# 平方根函数测试 ---------------------------------------------------
class TestSqrtFunction:   
    def test_sqrt_basic_cases(self, lib):
        """测试平方根正常情况"""
        test_cases = [
            (4.0, 2.0),      # √4 = 2
            (9.0, 3.0),      # √9 = 3  
            (16.0, 4.0),     # √16 = 4
            (0.0, 0.0),      # √0 = 0
            (1.0, 1.0),      # √1 = 1
            (2.0, 1.414213), # √2 ≈ 1.414213
        ]
        
        for input_val, expected in test_cases:
            error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
            result = lib.sqrt_calc(input_val, ctypes.byref(error))
            
            print(f"√{input_val} = {result}, 期望: {expected}, 错误码: {error.value}")
            assert error.value == CalcErrorCode.CALC_SUCCESS
            assert abs(result - expected) < 0.0001

    @pytest.mark.parametrize("input_val,expected,precision", [
        (4.0, 2.0, 0.0001),        # √4 = 2 (精确值)
        (9.0, 3.0, 0.0001),        # √9 = 3 (精确值)
        (0.0, 0.0, 0.0001),        # √0 = 0 (边界值)
        (2.0, 1.41421356, 0.000001), # √2 (测试牛顿迭代法精度)
    ])
    def test_sqrt_precision_cases(self, lib, input_val, expected, precision):
        """参数化测试平方根精度"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.sqrt_calc(input_val, ctypes.byref(error))
        
        print(f"√{input_val} = {result}, 期望: {expected}, 精度: {precision}")
        assert error.value == CalcErrorCode.CALC_SUCCESS
        assert abs(result - expected) < precision

    @pytest.mark.parametrize("input_val,expected_error", [
        (-1.0, CalcErrorCode.CALC_ERROR_NEGATIVE_SQRT),  # 负数平方根
        (-4.0, CalcErrorCode.CALC_ERROR_NEGATIVE_SQRT),  # 其他负数
    ])
    def test_sqrt_error_cases(self, lib, input_val, expected_error):
        """参数化测试平方根错误情况"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.sqrt_calc(input_val, ctypes.byref(error))
        
        print(f"√{input_val} = {result}, 错误码: {error.value}")
        assert error.value == expected_error
        assert result == 0.0  # 错误时返回安全值


    def test_sqrt_special_values(self, lib):
        """测试平方根特殊值（不适合参数化的复杂情况）"""
        import math
        
        # 测试NaN
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.sqrt_calc(math.nan, ctypes.byref(error))
        print(f"√NaN = {result}, 错误码: {error.value}")
        assert error.value == CalcErrorCode.CALC_ERROR_INVALID_INPUT
        
        # 测试无穷大
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.sqrt_calc(math.inf, ctypes.byref(error))
        print(f"√inf = {result}, 错误码: {error.value}")
        assert error.value == CalcErrorCode.CALC_ERROR_INVALID_INPUT


# 幂函数测试 ---------------------------------------------------
class TestPowerFunction:   
    @pytest.mark.parametrize("base,exp,expected,description", [
        (2.0, 3.0, 8.0, "2^3=8"),                    # 整数幂
        (5.0, 2.0, 25.0, "5^2=25"),                  # 平方
        (10.0, 0.0, 1.0, "任何数的0次方=1"),         # 零次方
        (1.0, 100.0, 1.0, "1的任何次方=1"),          # 1的幂
        (0.0, 5.0, 0.0, "0的正数次方=0"),            # 0的幂
        (4.0, 0.5, 2.0, "4^0.5=2"),                  # 平方根
        (8.0, 1.0/3.0, 2.0, "8^(1/3)=2"),            # 立方根
        (-2.0, 3.0, -8.0, "(-2)^3=-8"),              # 负底数奇次幂
        (27.0, 1.0/3.0, 3.0, "27^(1/3)=3"),          # 分数幂
    ])
    def test_power_success_cases(self, lib, base, exp, expected, description):
        """参数化测试幂函数成功情况"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.power(base, exp, ctypes.byref(error))
        
        print(f"{description}: {base}^{exp} = {result}")
        assert error.value == CalcErrorCode.CALC_SUCCESS
        assert abs(result - expected) < 0.0001

    @pytest.mark.parametrize("base,exp,expected_error,description", [
        (0.0, -2.0, CalcErrorCode.CALC_ERROR_INVALID_POWER, "0的负数次方"),
        (0.0, -1.0, CalcErrorCode.CALC_ERROR_INVALID_POWER, "0的-1次方"),
    ])
    def test_power_error_cases(self, lib, base, exp, expected_error, description):
        """参数化测试幂函数错误情况"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.power(base, exp, ctypes.byref(error))
        
        print(f"{description}: {base}^{exp} = {result}, 错误码: {error.value}")
        assert error.value == expected_error
        assert result == 0.0  # 错误时返回安全值

    def test_power_special_values(self, lib):
        """测试幂函数特殊值（不适合参数化的复杂情况）"""
        import math
        
        # 测试NaN和无穷大
        special_cases = [
            (math.nan, 2.0, "NaN^2"),
            (2.0, math.nan, "2^NaN"), 
            (math.inf, 2.0, "inf^2"),
            (2.0, math.inf, "2^inf"),
            (-math.inf, 2.0, "-inf^2"),
        ]
        
        for base, exp, description in special_cases:
            error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
            result = lib.power(base, exp, ctypes.byref(error))
            
            print(f"{description}: 错误码: {error.value}")
            assert error.value == CalcErrorCode.CALC_ERROR_INVALID_INPUT


class TestTrigFunction:
    # 三角函数基础功能测试 ---------------------------------------------------
    @pytest.mark.parametrize("input_val,angle_mode,func,expected,precision", [
        # 正弦函数测试
        (30.0, "degrees", "sin", 0.5, 0.0001),      # sin(30°) = 0.5
        (0.523599, "radians", "sin", 0.5, 0.0001),  # sin(π/6) = 0.5
        (90.0, "degrees", "sin", 1.0, 0.0001),      # sin(90°) = 1.0
        
        # 余弦函数测试  
        (60.0, "degrees", "cos", 0.5, 0.0001),      # cos(60°) = 0.5
        (0.0, "degrees", "cos", 1.0, 0.0001),       # cos(0°) = 1.0
        
        # 反正弦函数测试
        (0.5, "degrees", "asin", 30.0, 0.1),        # asin(0.5) = 30°
        (0.5, "radians", "asin", 0.523599, 0.001),  # asin(0.5) = π/6
        (0.0, "degrees", "asin", 0.0, 0.1),         # asin(0) = 0°
    ])
    def test_trig_basic_functions(self, lib, input_val, angle_mode, func, expected, precision):
        """参数化测试三角函数基本功能"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        
        result = lib.trig_calc(input_val, angle_mode.encode(), func.encode(), ctypes.byref(error))
        
        print(f"{func}({input_val} {angle_mode}) = {result}, 期望: {expected}, 错误码: {error.value}")
        assert error.value == CalcErrorCode.CALC_SUCCESS
        assert abs(result - expected) < precision


    # 三角函数错误处理测试 ---------------------------------------------------
    @pytest.mark.parametrize("input_val,angle_mode,func,expected_error", [
        # 无效输入测试
        (2.0, "degrees", "asin", CalcErrorCode.CALC_ERROR_INVALID_INPUT),    # asin(2.0) 超出范围
        (-2.0, "degrees", "asin", CalcErrorCode.CALC_ERROR_INVALID_INPUT),   # asin(-2.0) 超出范围
        
        # 无效角度模式测试
        (30.0, "invalid", "sin", CalcErrorCode.CALC_ERROR_INVALID_TRIG),     # 无效角度模式
        (30.0, "degree", "sin", CalcErrorCode.CALC_ERROR_INVALID_TRIG),      # 错误的角度模式拼写
        
        # 无效函数名测试
        (30.0, "degrees", "invalid", CalcErrorCode.CALC_ERROR_INVALID_TRIG), # 无效函数名
        (30.0, "degrees", "sine", CalcErrorCode.CALC_ERROR_INVALID_TRIG),    # 错误的函数名拼写
    ])
    def test_trig_error_cases(self, lib, input_val, angle_mode, func, expected_error):
        """参数化测试三角函数错误情况"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        
        result = lib.trig_calc(input_val, angle_mode.encode(), func.encode(), ctypes.byref(error))
        
        print(f"错误测试: {func}({input_val} {angle_mode}) - 结果: {result}, 错误码: {error.value}")
        assert error.value == expected_error



class TestAllLibraries:
    """真正的跨编译器兼容性测试"""
    def test_cross_compiler_consistency(self):  # 不依赖fixture的测试方法：需要self（pytest要求
        """验证所有编译器结果一致"""
        all_results = {}
        for lib_file in library_files:
            lib = ctypes.CDLL(os.path.join(get_lib_dir(), lib_file))
            setup_library_functions(lib)
            
            error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
            all_results[lib_file] = {
                'add': lib.add(100, 50),
                'divide': lib.divide(10, 3, ctypes.byref(error)),
                'sin_30': lib.trig_calc(30.0, b"degrees", b"sin", ctypes.byref(error)),
                'sqrt_4': lib.sqrt_calc(4.0, ctypes.byref(error)),      # 新增
                'power_2_3': lib.power(2.0, 3.0, ctypes.byref(error)),  # 新增
            }
        
        # 比较时也检查这两个函数
        first_lib = list(all_results.keys())[0]
        first_results = all_results[first_lib]
        
        for lib_name, results in all_results.items():
            assert results['add'] == first_results['add'], f"{lib_name} 加法结果不一致"
            assert abs(results['divide'] - first_results['divide']) < 0.0001, f"{lib_name} 除法结果不一致"
            assert abs(results['sin_30'] - first_results['sin_30']) < 0.0001, f"{lib_name} 正弦结果不一致"
            assert abs(results['sqrt_4'] - first_results['sqrt_4']) < 0.0001, f"{lib_name} 平方根结果不一致"  # 新增
            assert abs(results['power_2_3'] - first_results['power_2_3']) < 0.0001, f"{lib_name} 幂运算结果不一致"  # 新增


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

    