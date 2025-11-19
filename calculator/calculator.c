#include "calculator.h"
#include <stdio.h>
#include <math.h>
#include <string.h>

// 简单的函数不需要错误参数
CALC_API int add(int a, int b) { return a + b; }

CALC_API int subtract(int a, int b) { return a - b; }

CALC_API int multiply(int a, int b) { return a * b; }

CALC_API double divide(int a, int b, CalcErrorCode* error) {
    if (error) *error = CALC_SUCCESS;  // 有点像flag的功能

    if (b == 0) {
        set_error("Division by zero: %d / %d", a, b);
        if (error) *error = CALC_ERROR_DIVISION_BY_ZERO;
        return 0.0;
    } 
    return (double)a / b; 
}

CALC_API int square(int x) { return x * x; }

CALC_API int cube(int x) {
    return x * x * x;
}

// sqrt_calc避免与内置函数sqrt重名
CALC_API double sqrt_calc(double x, CalcErrorCode* error) {
    if (error) *error = CALC_SUCCESS;

    // 使用输入验证函数
    if (!is_valid_number(x)) {
        set_error("Invalid number for sqrt: %f", x);
        if (error) *error = CALC_ERROR_INVALID_INPUT;
        return 0.0;
    }

    if (x < 0) {
        set_error("Square root of negative number: %f", x);
        if (error) *error = CALC_ERROR_NEGATIVE_SQRT;
        return 0.0;
    }

    // 处理x=0的情况
    if (x == 0.0) {
        return 0.0;  // √0 = 0
    }

    // 牛顿迭代法计算平方根
    double result = x;
    for (int i = 0; i < 20; i++) {
        result = 0.5 * (result + x / result);
    }
    return result;
}


#include <math.h>

CALC_API double power(double base, double exponent, CalcErrorCode* error) {
    if (error) *error = CALC_SUCCESS;
    
    if (!is_valid_number(base) || !is_valid_number(exponent)) {
        if (error) *error = CALC_ERROR_INVALID_INPUT;
        return 0.0;
    }

    // 检查负数底数的非整数次方
    if (base < 0.0) {
        // 使用 modf 函数获取小数部分
        double int_part;
        double fractional_part = modf(fabs(exponent), &int_part);
        
        // 如果有小数部分，就是分数指数
        if (fractional_part > 1e-15) {
            set_error("Negative base with fractional exponent: %f ^ %f", base, exponent);
            if (error) *error = CALC_ERROR_INVALID_POWER;
            return 0.0;
        }
    }

    // 0的负数次方检查
    if (base == 0.0 && exponent < 0.0) {
        set_error("Zero to negative power: %f ^ %f", base, exponent);
        if (error) *error = CALC_ERROR_INVALID_POWER;
        return 0.0;
    }
    
    return pow(base, exponent);
}


// 修改 contains_embedded_null 函数
static int contains_embedded_null(const char* str) {
    if (!str) return 0;
    
    // 只检查前几个字符是否有内嵌空字节
    for (int i = 0; i < 10 && str[i] != '\0'; i++) {
        if (str[i] == '\0' && i > 0) {
            return 1; // 中间发现空字节
        }
    }
    return 0;
}


// 三角函数相关函数
CALC_API double trig_calc(double input, const char* angle_mode, const char* func, CalcErrorCode* error) {
    if (error) *error = CALC_SUCCESS;

    // 输入验证
    if (!is_valid_number(input)) {
        set_error("Invalid input number: %f", input);
        if (error) *error = CALC_ERROR_INVALID_INPUT;  // -5
        return 0.0;
    }

    // 添加极大值检查
    if (fabs(input) > 1e100) {
        set_error("Input value too large for trigonometric function: %f", input);
        if (error) *error = CALC_ERROR_INVALID_INPUT;  // -5
        return 0.0;
    }

    // 检查空指针
    if (!angle_mode || !func) {
        set_error("NULL pointer in angle_mode or func");
        if (error) *error = CALC_ERROR_INVALID_TRIG;  // -4
        return 0.0;
    }


    // 现有的角度模式验证
    if (strcmp(angle_mode, "degrees") != 0 && strcmp(angle_mode, "radians") != 0) {
        set_error("Invalid angle mode: %s", angle_mode);
        if (error) *error = CALC_ERROR_INVALID_TRIG;  // -4
        return 0.0;
    }

    // 函数名验证
    if (strcmp(func, "sin") != 0 && 
        strcmp(func, "cos") != 0 && 
        strcmp(func, "tan") != 0 &&
        strcmp(func, "asin") != 0 &&
        strcmp(func, "acos") != 0) {
        set_error("Invalid trig function: %s", func);
        if (error) *error = CALC_ERROR_INVALID_TRIG;  // -4
        return 0.0;
    }

    // 角度转换
    int is_degrees = (strcmp(angle_mode, "degrees") == 0);
    double radians = is_degrees ? (input * 3.141592653589793 / 180.0) : input;

    // 函数分发
    if (strcmp(func, "sin") == 0) return sin(radians);
    if (strcmp(func, "cos") == 0) return cos(radians);
    if (strcmp(func, "tan") == 0) return tan(radians);

    // asin 函数
    if (strcmp(func, "asin") == 0) {
        if (input < -1.0 || input > 1.0) {
            set_error("asin input out of range: %f", input);
            if (error) *error = CALC_ERROR_INVALID_INPUT;  // -5
            return 0.0;
        }
        double result = asin(input);
        return is_degrees ? (result * 180.0 / 3.141592653589793) : result;
    }

    // acos 函数  
    if (strcmp(func, "acos") == 0) {
        if (input < -1.0 || input > 1.0) {
            set_error("acos input out of range: %f", input);
            if (error) *error = CALC_ERROR_INVALID_INPUT;  // -5
            return 0.0;
        }
        double result = acos(input);
        return is_degrees ? (result * 180.0 / 3.141592653589793) : result;
    }

    // 不应该到达这里，因为上面已经检查了所有有效函数
    set_error("Unknown trig function: %s", func);
    if (error) *error = CALC_ERROR_INVALID_TRIG;  // -4
    return 0.0;
}

