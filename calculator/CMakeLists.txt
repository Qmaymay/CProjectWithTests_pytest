cmake_minimum_required(VERSION 3.10)
project(Calculator LANGUAGES C)

# 在 CMakeLists.txt 中添加以下内容来处理编码问题

# ==================== 字符编码设置 ====================
if(MSVC)
    # 对于 MSVC，只使用 /utf-8 选项（它包含了 source-charset 和 execution-charset）
    add_compile_options("$<$<C_COMPILER_ID:MSVC>:/utf-8>")

    # 禁用特定警告
    add_compile_options("$<$<C_COMPILER_ID:MSVC>:/wd4828>")  # 字符编码警告
else()
    # 对于 GCC/Clang/MinGW
    add_compile_options(-finput-charset=UTF-8)
    add_compile_options(-fexec-charset=UTF-8)
    add_compile_options(-fwide-exec-charset=UTF-8)
endif()


# ==================== 输出目录设置 ====================
set(BUILD_BASE_DIR ${CMAKE_BINARY_DIR})

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${BUILD_BASE_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${BUILD_BASE_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})



# ==================== 编译器设置 ====================
if(MSVC)
    add_compile_options(/utf-8)
    set(COMPILER_TYPE "msvc")
elseif(MINGW)
    set(COMPILER_TYPE "mingw")
elseif(CMAKE_COMPILER_IS_GNUCC)
    set(COMPILER_TYPE "gcc")
elseif(CMAKE_C_COMPILER_ID MATCHES "Clang")
    set(COMPILER_TYPE "clang")
else()
    set(COMPILER_TYPE "unknown")
endif()

message(STATUS "Detected compiler: ${COMPILER_TYPE}")

if(NOT MSVC)
    add_compile_options(-finput-charset=UTF-8)
    add_definitions(-D_UNICODE -DUNICODE)
endif()

# ==================== CI 环境检测 ====================
if(DEFINED ENV{GITHUB_ACTIONS})
    message(STATUS "Running in GitHub Actions environment")
    set(IS_CI TRUE)
else()
    message(STATUS "Running in local development environment")
    set(IS_CI FALSE)
endif()

# ==================== 构建类型设置 ====================
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif()

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    if(MSVC)
        add_compile_options(/Zi /Od)
    else()
        add_compile_options(-g -O0)
    endif()
    message(STATUS "Debug mode enabled")
else()
    if(MSVC)
        add_compile_options(/O2)
    else()
        add_compile_options(-O2)
    endif()
    message(STATUS "Release mode: ${CMAKE_BUILD_TYPE}")
endif()

# ==================== 源文件设置 ====================
set(CALC_SOURCES
        calculator.c
        error_handling.c
        main.c
)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# ==================== 创建共享库 ====================
add_library(calc SHARED ${CALC_SOURCES})

# ==================== 平台和编译器特定命名设置 ====================
if(WIN32)
    if(MSVC)
        # MSVC: calculator_msvc.dll
        set_target_properties(calc PROPERTIES
                OUTPUT_NAME "calculator_msvc"
                PREFIX ""
                SUFFIX ".dll"
        )
        set(LIBRARY_TYPE "msvc")
    elseif(MINGW)
        # MinGW: calculator_mingw.dll
        set_target_properties(calc PROPERTIES
                OUTPUT_NAME "calculator_mingw"
                PREFIX ""
                SUFFIX ".dll"
        )
        set(LIBRARY_TYPE "mingw")
    else()
        # 其他Windows编译器
        set_target_properties(calc PROPERTIES
                OUTPUT_NAME "calculator_win"
                PREFIX ""
                SUFFIX ".dll"
        )
        set(LIBRARY_TYPE "win")
    endif()
    target_compile_definitions(calc PRIVATE CALC_EXPORTS)
else()
    # Linux: libcalc_linux.so
    set_target_properties(calc PROPERTIES
            OUTPUT_NAME "calc_linux"
            PREFIX "lib"
            SUFFIX ".so"
    )
    set(LIBRARY_TYPE "linux")
endif()

message(STATUS "Library type: ${LIBRARY_TYPE}")

# ==================== 数学库链接 ====================
find_library(MATH_LIB m)
if(MATH_LIB)
    target_link_libraries(calc PRIVATE ${MATH_LIB})
    message(STATUS "Math library found: ${MATH_LIB}")
else()
    message(STATUS "Math library not found, continuing without it")
endif()

# ==================== 可执行文件创建 ====================
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/main.c")
    add_executable(calculator_app main.c)
    target_link_libraries(calculator_app calc)

    # 根据编译器和平台设置可执行文件命名
    if(MSVC)
        # MSVC: calculator_app_msvc.exe
        set_target_properties(calculator_app PROPERTIES
                OUTPUT_NAME "calculator_app_msvc"
                SUFFIX ".exe"
        )
    elseif(MINGW)
        # MinGW: calculator_app_mingw.exe
        set_target_properties(calculator_app PROPERTIES
                OUTPUT_NAME "calculator_app_mingw"
                SUFFIX ".exe"
        )
    else()
        # Linux: calculator_app_linux
        set_target_properties(calculator_app PROPERTIES
                OUTPUT_NAME "calculator_app_linux"
        )
    endif()

    # Windows DLL 复制
    if(WIN32)
        add_custom_command(TARGET calculator_app POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy
                "$<TARGET_FILE:calc>"
                "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/$<TARGET_FILE_NAME:calc>"
                COMMENT "Copying DLL to executable directory"
        )
    endif()
endif()

# ==================== 验证目标 ====================
add_custom_target(validate_all
        COMMAND ${CMAKE_COMMAND} -E echo "Build successful!"
        COMMAND ${CMAKE_COMMAND} -E echo "=== 生成的库文件 ==="
        COMMAND ${CMAKE_COMMAND} -E echo "动态库: $<TARGET_FILE:calc>"
        COMMAND ${CMAKE_COMMAND} -E echo "=== 生成的可执行文件 ==="
        COMMAND ${CMAKE_COMMAND} -E echo "可执行文件: $<TARGET_FILE:calculator_app>"
        COMMENT "Validating build results"
        DEPENDS calc calculator_app
)

add_dependencies(validate_all calc)
if(TARGET calculator_app)
    add_dependencies(validate_all calculator_app)
endif()

# ==================== 清理目标 ====================
add_custom_target(clean_all
        COMMAND ${CMAKE_COMMAND} -E echo "Cleaning generated files..."
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}
        COMMENT "Cleaning all generated files in build directory"
)

# ==================== 安装规则 ====================
install(TARGETS calc
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION lib
)

if(TARGET calculator_app)
    install(TARGETS calculator_app
            RUNTIME DESTINATION bin
    )
endif()

# ==================== 配置完成信息 ====================
message(STATUS "")
message(STATUS "====== Calculator Configuration Complete ======")
message(STATUS "Project Name: ${PROJECT_NAME}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Compiler: ${COMPILER_TYPE}")
message(STATUS "Library Type: ${LIBRARY_TYPE}")
message(STATUS "Library Output: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
message(STATUS "Runtime Output: ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
message(STATUS "Available Targets:")
message(STATUS "   - calc (shared library: $<TARGET_FILE_NAME:calc>)")
if(TARGET calculator_app)
    message(STATUS "   - calculator_app (executable: $<TARGET_FILE_NAME:calculator_app>)")
endif()
message(STATUS "   - validate_all (verify build)")
message(STATUS "   - clean_all (clean build artifacts)")
message(STATUS "")
message(STATUS "Expected Output Files:")
message(STATUS "   Shared Library: $<TARGET_FILE:calc>")
if(TARGET calculator_app)
    message(STATUS "   Executable: $<TARGET_FILE:calculator_app>")
endif()
message(STATUS "======================================")