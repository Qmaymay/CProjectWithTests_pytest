@echo off
echo Starting quick test...
echo.

echo 1. Building C library...
cd ..
call build.bat

echo.
echo 2. Running Python tests...

:: 确保切换到正确的测试目录
cd /d "%~dp0"
echo 当前目录: %CD%

:: 检查main.py是否存在
if exist main.py (
    echo 找到main.py，开始运行Python测试...
    python main.py
) else (
    echo 错误: 找不到main.py
    echo 当前目录文件列表:
    dir
    pause
    exit /b 1
)

if %errorlevel% equ 0 (
    echo.
    echo ✅ All tests passed! Ready to push to GitHub.
) else (
    echo.
    echo ❌ Tests failed, please check issues.
)

pause
