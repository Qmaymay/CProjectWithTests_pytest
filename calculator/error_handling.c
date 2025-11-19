//
// Created by Admin on 2025/11/2.
//

#include "error_handling.h"
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <math.h>

static char last_error[256] = {0};

// ================== 错误处理部分 ==================
CALC_API void set_error(const char* format, ...) {
    va_list args;
    va_start(args, format);
    vsnprintf(last_error, sizeof(last_error), format, args);
    va_end(args);
}

CALC_API const char* get_last_error(void) {
    return last_error;
}

CALC_API void clear_error(void) {
    last_error[0] = '\0';
}

CALC_API const char* error_code_to_string(CalcErrorCode code) {
    switch (code) {
        case CALC_SUCCESS: return "Success";
        case CALC_ERROR_DIVISION_BY_ZERO: return "Division by zero";
        case CALC_ERROR_NEGATIVE_SQRT: return "Square root of negative number";
        case CALC_ERROR_INVALID_POWER: return "Invalid power operation";
        case CALC_ERROR_INVALID_TRIG: return "Invalid trigonometric operation";
        case CALC_ERROR_INVALID_INPUT: return "Invalid input";
        case CALC_ERROR_TANGENT_UNDEFINED: return "Tangent undefined for this angle";
        default: return "Unknown error";
    }
}

/// ================== 输入验证部分 ==================
CALC_API bool is_valid_number(double x) {
    return !isnan(x) && !isinf(x);
}

