//
// Created by Admin on 2025/11/7.
//
/*
 * calculator_app 运行说明
 * CLion 有两种运行模式：
 * - CMake 模式：通过 CMakeLists.txt，正确链接所有依赖
 * - 单文件模式：快速测试单个文件，但无法处理复杂依赖
 * 与测试python代码共享动态库时，main.c 下点绿色三角只会编译main.c
 */

#include <stdio.h>
#include "calculator.h"  // 只需要包含这个，会自动包含 error_handling.h

// 测试基本运算
void test_basic_operations(void) {
    printf("=== 基本运算测试 ===\n");

    // 不需要错误检查的简单运算
    printf("5 + 3 = %d\n", add(5, 3));
    printf("10 - 4 = %d\n", subtract(10, 4));

    // 需要错误检查的运算
    CalcErrorCode error;

    // 正常除法
    double result = divide(10, 2, &error);
    if (error == CALC_SUCCESS) {
        printf("10 / 2 = %.2f\n", result);
    } else {
        printf("除法错误: %s\n", get_last_error());
    }

    // 除零错误
    result = divide(10, 0, &error);
    if (error != CALC_SUCCESS) {
        printf("检测到除零错误: %s (错误码: %d)\n",
               get_last_error(), error);
        printf("错误描述: %s\n", error_code_to_string(error));
    }
}

// 测试高级运算
void test_advanced_operations(void) {
    printf("\n=== 高级运算测试 ===\n");

    CalcErrorCode error;

    // 平方根测试
    double sqrt_result = sqrt_calc(25.0, &error);
    if (error == CALC_SUCCESS) {
        printf("√25 = %.2f\n", sqrt_result);
    }

    // 负数平方根测试
    sqrt_result = sqrt_calc(-4.0, &error);
    if (error != CALC_SUCCESS) {
        printf("平方根错误: %s\n", error_code_to_string(error));
    }
}

// 幂运算测试
void test_power_function(void) {
    printf("\n=== 幂运算测试 ===\n");

    CalcErrorCode error;

    // 测试1: 正常情况
    double power_result = power(2.0, 3.0, &error);
    if (error == CALC_SUCCESS) {
        printf("2^3 = %.2f\n", power_result);
    } else {
        printf("计算失败: %s\n", get_last_error());
    }

    // 测试2: 0的负数次方（应该报错）
    power_result = power(0.0, -2.0, &error);
    if (error != CALC_SUCCESS) {
        printf("检测到错误: %s (错误码: %d)\n",
               get_last_error(), error);
        printf("错误描述: %s\n", error_code_to_string(error));
    }

    // 测试3: 负数底数的小数次方（应该报错）
    power_result = power(-4.0, 0.5, &error);
    if (error != CALC_SUCCESS) {
        printf("检测到错误: %s\n", error_code_to_string(error));
    }

    // 测试4: 无效输入检测
    double zero = 0.0;
    double result = divide(10.0, 0.0, &error);
    if (error != CALC_SUCCESS) {
        printf("无效输入检测: %s\n", get_last_error());
    }
}

// 测试三角函数
void test_trig_functions(void) {
    printf("\n=== 三角函数测试 ===\n");

    CalcErrorCode error;

    // 正常三角函数计算
    double sin_result = trig_calc(30.0, "degrees", "sin", &error);
    if (error == CALC_SUCCESS) {
        printf("sin(30°) = %.2f\n", sin_result);
    }

    // 无效角度模式测试
    double invalid_result = trig_calc(30.0, "invalid_mode", "sin", &error);
    if (error != CALC_SUCCESS) {
        printf("三角函数错误: %s\n", get_last_error());
    }

    // 无效函数名测试
    invalid_result = trig_calc(30.0, "degrees", "invalid_func", &error);
    if (error != CALC_SUCCESS) {
        printf("函数名错误: %s\n", error_code_to_string(error));
    }
}

// 直接使用验证函数
void test_validation_functions(void) {
    printf("\n=== 输入验证测试 ===\n");

    // 直接使用验证函数（不需要通过计算器）
    printf("验证数字 3.14: %s\n", is_valid_number(3.14) ? "有效" : "无效");

    // 测试无效输入
    double zero = 0.0;
    double invalid_num = zero / zero;  // 运行时计算，编译时不会检测
    printf("验证 NaN 数字: %s\n", is_valid_number(invalid_num) ? "有效" : "无效");
}

int main(void) {
    printf("计算器测试程序\n");
    test_basic_operations();
    test_advanced_operations();
    test_power_function();
    test_trig_functions();
    test_validation_functions();

    printf("\n所有测试完成！\n");
    return 0;
}