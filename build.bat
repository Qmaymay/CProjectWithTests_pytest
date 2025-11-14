@echo off
chcp 65001 >nul

set BUILD_CONFIG=Debug
if "%1"=="release" set BUILD_CONFIG=Release

echo 构建Calculator项目 (%BUILD_CONFIG%模式)...

:: 总是使用build目录
if exist build rmdir /s /q build
mkdir build
cd build

cmake -G "Visual Studio 17 2022" -A x64 ..
cmake --build . --config %BUILD_CONFIG%

echo ✅ %BUILD_CONFIG%构建成功!

:: 测试
cd lib
if exist calculator_app_msvc.exe (
    echo 运行测试...
    calculator_app_msvc.exe
) else (
    echo 错误: 找不到可执行文件
    dir *.exe
)

pause