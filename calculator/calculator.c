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


// 安全检查函数名，防止内嵌空字节攻击
static int is_safe_function_name(const char* func) {
    if (!func) return 0;
    
    // 检查前几个字符，寻找第一个空字节
    int first_null_pos = -1;
    for (int i = 0; i < 5; i++) {
        if (func[i] == '\0') {
            first_null_pos = i;
            break;
        }
    }
    
    // 如果没有找到空字节，说明字符串太长或不规范
    if (first_null_pos == -1) {
        return 0;
    }
    
    // 关键修改：只在第一个空字节之后立即有非空字节时才认为是攻击
    // 如果第一个空字节之后都是空字节，那是正常的字符串结尾
    int has_embedded_null = 0;
    if (first_null_pos < 9) {  // 确保有后续字符可以检查
        // 检查第一个空字节之后的一个字符
        if (func[first_null_pos + 1] != '\0') {
            // 第一个空字节之后立即有非空字节，说明是内嵌空字节攻击
            has_embedded_null = 1;
        }
    }
    
    if (has_embedded_null) {
        return 0;
    }
    
    // 现在检查函数名是否在允许列表中
    int length = first_null_pos;
    
    if (length == 3) {
        // 检查 "sin", "cos", "tan"
        if (func[0] == 's' && func[1] == 'i' && func[2] == 'n') return 1;
        if (func[0] == 'c' && func[1] == 'o' && func[2] == 's') return 1;
        if (func[0] == 't' && func[1] == 'a' && func[2] == 'n') return 1;
    }
    else if (length == 4) {
        // 检查 "asin", "acos"
        if (func[0] == 'a' && func[1] == 's' && func[2] == 'i' && func[3] == 'n') return 1;
        if (func[0] == 'a' && func[1] == 'c' && func[2] == 'o' && func[3] == 's') return 1;
    }
    
    return 0;
}



// 三角函数相关函数
CALC_API double trig_calc(double input, const char* angle_mode, const char* func, CalcErrorCode* error) {
    if (error) *error = CALC_SUCCESS;

    // 严格的空指针检查 - 必须在任何指针访问之前
    if (angle_mode == NULL) {
        // 在确认指针为NULL时，避免任何函数调用
        if (error) *error = CALC_ERROR_INVALID_TRIG;
        return 0.0; // 在确认指针为NULL时，避免任何函数调用
    }

    if (func == NULL) {
        // 同样，避免函数调用
        set_error("NULL func pointer");
        if (error) *error = CALC_ERROR_INVALID_TRIG;
        return 0.0;
    }

    // 直接使用参数，假设调用者传递了有效指针
    // 调试输出（只在开发时启用）
    #ifdef DEBUG
    printf("DEBUG: Received func: ");
    for (int i = 0; i < 15; i++) {
        if (func[i] == '\0') {
            printf("\\0 ");
        } else if (func[i] >= 32 && func[i] <= 126) {
            printf("%c ", func[i]);
        } else {
            printf("? ");
        }
    }
    printf("\n");
    #endif

    // 只有确认所有指针都有效后，才使用 set_error
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


    // 现有的角度模式验证
    if (strcmp(angle_mode, "degrees") != 0 && strcmp(angle_mode, "radians") != 0) {
        set_error("Invalid angle mode: %s", angle_mode);
        if (error) *error = CALC_ERROR_INVALID_TRIG;  // -4
        return 0.0;
    }

    // 用这个安全方案替换上面的复杂检查
    if (!is_safe_function_name(func)) {
        set_error("Invalid trig function: %s", func);
        if (error) *error = CALC_ERROR_INVALID_TRIG;
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

