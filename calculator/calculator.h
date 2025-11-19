#ifndef CALCULATOR_H
#define CALCULATOR_H

#include "error_handling.h"  // 包含错误处理头文件

// 添加导出宏
#ifdef _WIN32
    #define CALC_API __declspec(dllexport)
#else
    #define CALC_API
#endif

#ifdef __cplusplus
    extern "C" {
#endif

// 版本信息
//const char* get_version(void);
//const char* get_last_error(void);

// 基本运算
CALC_API int add(int a, int b);
CALC_API int subtract(int a, int b);
CALC_API int multiply(int a, int b);
CALC_API double divide(int a, int b, CalcErrorCode* error);

// 高级运算
CALC_API int square(int x);
CALC_API int cube(int x);
CALC_API double sqrt_calc(double x, CalcErrorCode* error);
CALC_API double power(double base, double exponent, CalcErrorCode* error);


// 三角运算
CALC_API double trig_calc(double input, const char* angle_mode, const char* func, CalcErrorCode* error) ;


#ifdef __cplusplus
}
#endif

#endif // CALCULATOR_H

