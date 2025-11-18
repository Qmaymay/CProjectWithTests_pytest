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
if exist test_runner.py (
    echo 找到maintest_runner.py，开始运行Python测试...
    python test_runner.py
) else (
    echo 错误: 找不到test_runner.py
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
