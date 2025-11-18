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


# 多库测试固件
@pytest.fixture(params=library_files if library_files else [])
def lib(request):
    """为每个库提供实例"""
    lib_file = request.param
    lib_path = os.path.join(get_lib_dir(), lib_file)
    
    # 加载动态库 使用CDLL（根据你的C库编译设置）—— 把C库变成Python对象
    lib = ctypes.CDLL(lib_path)

    # 配置接口——告诉Python如何与C函数交互
    setup_library_functions(lib)
    return lib


def test_add(lib):
    """测试加法"""
    result = lib.add(10, 5)
    assert result == 15


def test_subtract(lib):
    """测试减法"""
    result = lib.subtract(10, 5)
    assert result == 5


def test_multiply(lib):
    """测试乘法"""
    result = lib.multiply(10, 5)
    assert result == 50


def test_divide(lib):
    """测试除法"""
    error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
    result = lib.divide(10, 5, ctypes.byref(error))

    print(f"除法结果: {result}, 错误码: {error.value}")

    # 检查操作是否成功
    if error.value != CalcErrorCode.CALC_SUCCESS:
        pytest.fail(f"除法失败，错误码: {error.value}")
    
    # 根据你的C函数签名，应该返回double 2.0
    assert abs(result - 2.0) < 0.0001


def test_divide_error(lib):
    """测试除法错误处理"""
    error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
    result = lib.divide(10, 0, ctypes.byref(error))

    print(f"除零错误测试 - 结果: {result}, 错误码: {error.value}")
    assert error.value == CalcErrorCode.CALC_ERROR_DIVISION_BY_ZERO


def test_square(lib):
    """测试平方"""
    result = lib.square(5)
    assert result == 25


def test_cube(lib):
    """测试立方"""
    result = lib.cube(3)
    assert result == 27


def test_sqrt(lib):
    """测试平方根"""
    error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
    result = lib.sqrt_calc(9.0, ctypes.byref(error))

    print(f"平方根结果: {result}, 错误码: {error.value}")

    # 检查操作是否成功
    if error.value != CalcErrorCode.CALC_SUCCESS:
        pytest.fail(f"平方根失败，错误码: {error.value}")
    
    assert abs(result - 3.0) < 0.0001


def test_sqrt_error(lib):
    """测试平方根错误处理"""
    error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
    result = lib.sqrt_calc(-1.0, ctypes.byref(error))

    print(f"负数平方根测试 - 结果: {result}, 错误码: {error.value}")
    assert error.value == CalcErrorCode.CALC_ERROR_NEGATIVE_SQRT


def test_prototype_caching_issue(lib):
    """测试函数原型是否会被缓存或重置"""
    print("\n🔍 测试函数原型缓存问题:")
    
    # 记录初始的函数原型设置
    initial_divide_restype = lib.divide.restype
    initial_divide_argtypes = lib.divide.argtypes
    print(f"初始设置 - divide.restype: {initial_divide_restype}")
    print(f"初始设置 - divide.argtypes: {initial_divide_argtypes}")
    
    # 故意修改函数原型
    lib.divide.restype = ctypes.c_int  # 改为错误的类型
    lib.divide.argtypes = [ctypes.c_int, ctypes.c_int]  # 改为错误的参数
    
    print(f"修改后 - divide.restype: {lib.divide.restype}")
    print(f"修改后 - divide.argtypes: {lib.divide.argtypes}")
    
    # 测试使用错误原型调用函数
    try:
        # 这会失败，因为参数数量不对
        result = lib.divide(10, 5)
        print(f"错误原型调用结果: {result}")
    except Exception as e:
        print(f"错误原型调用失败: {e}")
    
    # 重新设置正确的函数原型
    setup_library_functions(lib)
    
    print(f"重新设置后 - divide.restype: {lib.divide.restype}")
    print(f"重新设置后 - divide.argtypes: {lib.divide.argtypes}")
    
    # 测试使用正确原型调用函数
    error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
    result = lib.divide(10, 5, ctypes.byref(error))
    print(f"正确原型调用结果: {result}, 错误码: {error.value}")
    
    # 验证结果是否正确
    assert abs(result - 2.0) < 0.0001
    assert error.value == CalcErrorCode.CALC_SUCCESS

    # 全局变量来跟踪状态
test_call_count = 0

def test_prototype_persistence_1(lib):
    """测试1：验证函数原型在测试间的持久性"""
    global test_call_count
    test_call_count += 1
    
    print(f"\n📝 测试 {test_call_count}:")
    print(f"divide.restype: {lib.divide.restype}")
    
    # 如果是第一次调用，记录初始状态
    if test_call_count == 1:
        # 故意修改原型
        lib.divide.restype = ctypes.c_int
        print("✅ 故意修改了 divide.restype")
    
    # 测试函数调用
    error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
    result = lib.divide(10, 5, ctypes.byref(error))
    print(f"结果: {result}, 类型: {type(result)}")

def test_prototype_persistence_2(lib):
    """测试2：验证修改是否影响其他测试"""
    global test_call_count
    test_call_count += 1
    
    print(f"\n📝 测试 {test_call_count}:")
    print(f"divide.restype: {lib.divide.restype}")
    
    # 测试函数调用
    error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
    result = lib.divide(10, 5, ctypes.byref(error))
    print(f"结果: {result}, 类型: {type(result)}")
    
    # 这个应该正常工作，因为fixture会重新创建lib实例
    assert abs(result - 2.0) < 0.0001

class TestAllLibraries:
    """测试所有库的兼容性"""

    def test_basic_operations(self, lib):
        """测试每个库的基本操作"""
        
        assert lib.add(10, 5) == 15
        assert lib.subtract(10, 5) == 5
        assert lib.multiply(10, 5) == 50
        
        # 测试除法
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        result = lib.divide(10, 5, ctypes.byref(error))
        assert abs(result - 2.0) < 0.0001
        assert error.value == CalcErrorCode.CALC_SUCCESS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

    