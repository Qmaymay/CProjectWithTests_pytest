//
// Created by Admin on 2025/11/2.
//

#ifndef ERROR_HANDLING_H
#define ERROR_HANDLING_H

#include <stdbool.h>

#ifdef _WIN32
    #define CALC_API __declspec(dllexport)
#else
    #define CALC_API 
#endif


#ifdef __cplusplus
extern "C" {
#endif


// 错误码定义
typedef enum {
    CALC_SUCCESS = 0,
    CALC_ERROR_DIVISION_BY_ZERO = -1,
    CALC_ERROR_NEGATIVE_SQRT = -2,
    CALC_ERROR_INVALID_POWER = -3,
    CALC_ERROR_INVALID_TRIG = -4,
    CALC_ERROR_INVALID_INPUT = -5,
    CALC_ERROR_TANGENT_UNDEFINED = -6
} CalcErrorCode;

// 错误处理函数
CALC_API void set_error(const char* format, ...);
CALC_API const char* get_last_error(void);
CALC_API void clear_error(void);
CALC_API const char* error_code_to_string(CalcErrorCode code);

// 输入验证函数
CALC_API bool is_valid_number(double x);


#ifdef __cplusplus
}
#endif

#endif // ERROR_HANDLING_H
