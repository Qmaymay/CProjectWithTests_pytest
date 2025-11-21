//
// Created by Admin on 2025/11/7.
//

#include <stdio.h>
#include "calculator.h"  // 只需要包含这个，会自动包含 error_handling.h

// 测试基本运算
void test_basic_operations(void) {
    printf("=== 基本运算测试 ===\n");

    // 不需要错误检查的简单运算
    printf("5 + 3 = %d\n", add(5, 3));
    printf("10 - 4 = %d\n", subtract(10, 4));

    // 需要错误检查的运算, 采用随机值为初始值，这样函数不正确工作时error打印出来就是随机值
    CalcErrorCode error;  // 不初始化，保持随机值

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


int main(void) {
    printf("计算器测试程序\n");
    test_basic_operations();
    test_advanced_operations();
    test_power_function();
    test_trig_functions();

    printf("\n所有测试完成！\n");
    return 0;
}