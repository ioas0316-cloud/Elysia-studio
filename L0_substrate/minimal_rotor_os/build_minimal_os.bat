@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
if errorlevel 1 (
  echo [ERROR] MSVC 2022 BuildTools vcvars64.bat failed
  exit /b 1
)
cl /nologo /O2 /EHsc /std:c++17 /W3 "%~dp0elysia_minimal_os.cpp" /Fe:"%~dp0elysia_minimal_os.exe" /Fo:"%~dp0elysia_minimal_os.obj"
if errorlevel 1 exit /b 1
echo [OK] Built %~dp0elysia_minimal_os.exe
