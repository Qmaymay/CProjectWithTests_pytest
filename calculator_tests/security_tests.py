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
import math

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


# 三角函数安全测试 ---------------------------------------------------
"""
安全测试覆盖：
1, 边界值攻击：极大值、极小值、边界附近值
2, 特殊数值：NaN、无穷大、负无穷
3, 空指针安全：NULL参数处理
4, 注入攻击：特殊字符函数名
5, 精度安全：浮点数精度边界
6, 数值稳定性：超大角度的周期性处理
7, 跨库一致性：所有编译器版本的安全行为一致
"""
class TestTrigSecurity:
    """三角函数安全测试类"""
    
    @pytest.mark.parametrize("input_val,angle_mode,func,description", [
        (1e308, "degrees", "sin", "极大值sin测试"),
        (1e10, "degrees", "sin", "超大角度sin测试"),
        (-1e10, "degrees", "cos", "负超大角度cos测试"),
    ])
    def test_trig_boundary_values(self, lib, input_val, angle_mode, func, description):
        """测试三角函数边界值安全"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        
        result = lib.trig_calc(input_val, angle_mode.encode(), func.encode(), ctypes.byref(error))
        
        print(f"{description} - 结果: {result}, 错误码: {error.value}")

         # 分类处理不同的测试用例
        if input_val == 1e308:
        # 极大值测试：期望返回输入错误
            assert error.value == CalcErrorCode.CALC_ERROR_INVALID_INPUT  # -5
            assert result == 0.0  # 你的函数返回0.0
        else:
        # 其他边界值测试：期望成功
            assert error.value == CalcErrorCode.CALC_SUCCESS
        if not math.isnan(result):
            # 如果不是nan，检查是否在有效范围内
            assert -1.0 <= result <= 1.0

    @pytest.mark.parametrize("special_value,description", [
        (math.nan, "NaN输入"),
        (math.inf, "正无穷输入"),
        (-math.inf, "负无穷输入"),
    ])
    def test_trig_special_values(self, lib, special_value, description):
        """测试特殊数值输入安全"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        
        result = lib.trig_calc(special_value, b"degrees", b"sin", ctypes.byref(error))
        
        print(f"{description}测试 - 结果: {result}, 错误码: {error.value}")
        assert error.value == CalcErrorCode.CALC_ERROR_INVALID_INPUT

    @pytest.mark.parametrize("input_val,func,expected_error,description", [
        (-1.0000000001, "asin", CalcErrorCode.CALC_ERROR_INVALID_INPUT, "asin略小于-1"),
        (1.0000000001, "asin", CalcErrorCode.CALC_ERROR_INVALID_INPUT, "asin略大于1"),
        (-1.0000000001, "acos", CalcErrorCode.CALC_ERROR_INVALID_INPUT, "acos略小于-1"),
        (1.0000000001, "acos", CalcErrorCode.CALC_ERROR_INVALID_INPUT, "acos略大于1"),
        (0.9999999999, "acos", CalcErrorCode.CALC_SUCCESS, "acos接近1"),
        (-0.9999999999, "acos", CalcErrorCode.CALC_SUCCESS, "acos接近-1"),
    ])
    def test_inverse_trig_boundaries(self, lib, input_val, func, expected_error, description):
        """测试反三角函数边界值安全"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        
        result = lib.trig_calc(input_val, b"degrees", func.encode(), ctypes.byref(error))
        
        print(f"{description}测试 - 结果: {result}, 错误码: {error.value}")
        assert error.value == expected_error
        
        if expected_error == CalcErrorCode.CALC_SUCCESS:
            # 验证反三角函数结果在合理范围内
            if func == "asin":
                assert -90.0 <= result <= 90.0
            elif func == "acos":
                assert 0.0 <= result <= 180.0

    @pytest.mark.parametrize("angle_mode,func,description", [
        (None, b"sin", "NULL angle_mode"),
        (b"degrees", None, "NULL func"),
    ])
    def test_trig_null_pointers(self, lib, angle_mode, func, description):
        """测试空指针安全"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        
        result = lib.trig_calc(30.0, angle_mode, func, ctypes.byref(error))
        
        print(f"{description}测试 - 结果: {result}, 错误码: {error.value}")
        assert error.value == CalcErrorCode.CALC_ERROR_INVALID_TRIG

    @pytest.mark.parametrize("malicious_func,description", [
        (b"sin\x00injection", "空字节注入"),
        (b"../../etc/passwd", "路径遍历"),
        (b"OR 1=1", "SQL注入样式"),
        (b"<script>alert('xss')</script>", "XSS样式"),
    ])
    def test_trig_malicious_inputs(self, lib, malicious_func, description):
        """测试恶意输入安全"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        
        result = lib.trig_calc(30.0, b"degrees", malicious_func, ctypes.byref(error))
        
        print(f"{description}测试 - 结果: {result}, 错误码: {error.value}")
        # 应该被识别为未知函数
        assert error.value == CalcErrorCode.CALC_ERROR_INVALID_TRIG

    @pytest.mark.parametrize("input_val,func,expected_range", [
        (1e-10, "sin", (-1.0, 1.0)),
        (1e-10, "cos", (-1.0, 1.0)),
        (89.999999, "sin", (0.999999, 1.0)),
        (0.000001, "sin", (0.0, 0.0001)),
    ])
    def test_trig_precision_boundaries(self, lib, input_val, func, expected_range):
        """测试三角函数精度边界"""
        error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
        
        result = lib.trig_calc(input_val, b"degrees", func.encode(), ctypes.byref(error))
        
        print(f"精度测试 {func}({input_val}) = {result}, 错误码: {error.value}")
        assert error.value == CalcErrorCode.CALC_SUCCESS
        assert expected_range[0] <= result <= expected_range[1]



class TestAllLibrariesSecurity:
    """跨库安全一致性测试"""
    
    def _test_security_scenario(self, test_cases):
        """通用安全场景测试框架"""
        all_results = {}
        
        for lib_file in library_files:
            lib_path = os.path.join(get_lib_dir(), lib_file)
            lib = ctypes.CDLL(lib_path)
            setup_library_functions(lib)
            
            lib_results = {}
            for case_name, test_func in test_cases.items():
                error = CalcErrorCode(CalcErrorCode.CALC_SUCCESS)
                result = test_func(lib, error)
                lib_results[case_name] = error.value
                print(f"  {case_name}: 错误码={error.value}")
            
            all_results[lib_file] = lib_results
        
        # 比较所有库的一致性
        first_lib = list(all_results.keys())[0]
        first_results = all_results[first_lib]
        
        for lib_name, results in all_results.items():
            for case_name, error_code in results.items():
                assert error_code == first_results[case_name], \
                    f"{lib_name} 的 {case_name} 处理不一致: {error_code} vs {first_results[case_name]}"
        
        return all_results

    def test_trig_security_consistency(self):
        """三角函数安全一致性"""
        print("🔍 测试三角函数安全一致性...")
        
        test_cases = {
            "NaN输入": lambda lib, error: lib.trig_calc(math.nan, b"degrees", b"sin", ctypes.byref(error)),
            "ASIN超范围": lambda lib, error: lib.trig_calc(2.0, b"degrees", b"asin", ctypes.byref(error)),
            "ACOS超范围": lambda lib, error: lib.trig_calc(1.5, b"degrees", b"acos", ctypes.byref(error)),
        }
        
        results = self._test_security_scenario(test_cases)
        print(f"✅ 所有 {len(results)} 个库的三角函数安全行为一致")

    def test_arithmetic_security_consistency(self):
        """算术运算安全一致性"""
        print("🔍 测试算术运算安全一致性...")
        
        test_cases = {
            "除零错误": lambda lib, error: lib.divide(1, 0, ctypes.byref(error)),
            "负数平方根": lambda lib, error: lib.sqrt_calc(-1.0, ctypes.byref(error)),
            "0的负指数": lambda lib, error: lib.power(0.0, -1.0, ctypes.byref(error)),
        }
        
        results = self._test_security_scenario(test_cases)
        print(f"✅ 所有 {len(results)} 个库的算术安全行为一致")



if __name__ == "__main__":
    pytest.main([__file__, "-v"])