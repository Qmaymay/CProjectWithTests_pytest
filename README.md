# Calculator Project

## 🏗️ 本项目架构图

### 核心文件关系
```
📦 Calculator Project
├── 🔧 构建系统
│   ├── CMakeLists.txt (主配置)
│   ├── build.bat (Windows构建)
│   └── simple_test.py (Python构建)
│
├── 💻 C核心库
│   ├── calculator.h (主接口)
│   ├── calculator.c (实现)
│   ├── error_handling.c (错误处理)
│   └── main.c (演示程序)
│
├── 🧪 测试系统
│   ├── test_runner.py (测试入口)
│   ├── test_interfaces.py (功能测试)
│   ├── security_tests.py (安全测试)
│   └── performance_tests.py (性能测试)
│
├── 🔄 CI/CD
│   └── .github/workflows/ci.yml (自动化流水线)
│
└── ⚙️ 开发配置
    └── .vscode/ (IDE设置)
```

### 本地构建流程
```
1. build.bat 
   ↓
2. CMake 编译 C 代码
   ↓  
3. 生成 calculator_*.dll
   ↓
4. lib_loader.py 自动检测
   ↓
5. python 运行所有测试（可用pytest测试各.py测试文件）
```

### 版本管理
```
Git Commit → pre-commit钩子 → auto_test_version.py → 更新版本号
```

## 🚀 快速开始

```bash
# 本地构建并测试可执行文件
.\build.bat

# 本地构建并测试所有套件（功能，性能，安全测试，可执行文件测试）
cd calculator_tests .\quick_test.bat
cd calculator_tests python build_and_test.py

# 只本地测试所有套件
cd calculator_tests python test_runner.py

```
## 📊 测试状态
86个测试通过 ✅ | 2个测试失败 ❌


# 已知问题：
1，边界值处理：极大值三角函数输入返回 CALC_ERROR_INVALID_INPUT (-5) 而非成功 (0)
2，安全过滤：恶意输入（如空字节注入）未被正确识别，返回成功而非 CALC_ERROR_INVALID_TRIG (-4)

# 对使用者的影响：
✅ 核心功能正常：基本运算、错误处理、性能测试全部通过
⚠️ 边界情况需注意：极端输入和恶意输入的处理需要改进
🔧 不影响主要使用：问题出现在边界和安全场景，日常使用无影响


## 📊 技术栈

- **语言**: C (C17标准) + Python
- **构建**: CMake + MSVC/GCC/MinGW  
- **测试**: pytest + ctypes
- **CI/CD**: GitHub Actions
- **版本控制**: Git + 自动化版本管理

---

💡 **项目亮点**: 跨平台兼容、全面测试覆盖、自动化流水线、智能版本管理