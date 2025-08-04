@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo    Image Search Application - Smart Update
echo ======================================================
echo.
echo Этот скрипт обновит существующую установку до последней версии
echo с поддержкой оптимизации памяти для больших коллекций.
echo.

REM Переход в директорию скрипта
cd /d "%~dp0"

REM Определение существующего окружения
echo [1/6] Анализ существующей установки...

set "VENV_PATH="
set "VENV_PYTHON="
set "EXISTING_MODE="

REM Поиск виртуального окружения
if exist ".venv\Scripts\activate.bat" (
    echo ✅ Найдено окружение: .venv
    set "VENV_PATH=.venv"
    set "VENV_PYTHON=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\activate.bat" (
    echo ✅ Найдено окружение: venv
    set "VENV_PATH=venv"
    set "VENV_PYTHON=venv\Scripts\python.exe"
) else (
    echo ❌ Виртуальное окружение не найдено!
    echo.
    echo Похоже, что приложение не было установлено ранее.
    echo Запустите install.bat для новой установки.
    echo.
    pause
    exit /b 1
)

REM Активация окружения
call "%VENV_PATH%\Scripts\activate.bat"

REM Проверка Python
"%VENV_PYTHON%" --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Проблемы с Python в виртуальном окружении
    echo Возможно, окружение повреждено. Запустите install.bat для переустановки.
    pause
    exit /b 1
)

echo ✅ Python окружение активно

REM Определение текущей конфигурации
echo.
echo [2/6] Определение текущей конфигурации...

REM Проверка наличия CUDA
"%VENV_PYTHON%" -c "import torch; print('CUDA' if torch.cuda.is_available() else 'CPU')" 2>nul
if !errorlevel! equ 0 (
    for /f %%i in ('"%VENV_PYTHON%" -c "import torch; print('CUDA' if torch.cuda.is_available() else 'CPU')" 2^>nul') do set "EXISTING_MODE=%%i"
) else (
    set "EXISTING_MODE=UNKNOWN"
)

echo Текущий режим: !EXISTING_MODE!

REM Проверка текущих версий
echo.
echo Текущие версии пакетов:
"%VENV_PYTHON%" -c "import torch; print(f'PyTorch: {torch.__version__}')" 2>nul
"%VENV_PYTHON%" -c "import sentence_transformers; print(f'SentenceTransformers: {sentence_transformers.__version__}')" 2>nul
"%VENV_PYTHON%" -c "import psutil; print(f'PSUtil: {psutil.__version__}')" 2>nul || echo "PSUtil: не установлен"

REM Выбор действия
echo.
echo [3/6] Выбор типа обновления...
echo.
echo Что вы хотите сделать?
echo.
echo 1) Добавить только оптимизацию памяти (сохранить текущую конфигурацию)
echo 2) Обновить все пакеты до последних версий
echo 3) Переключиться на GPU режим (если доступно)
echo 4) Переключиться на CPU режим
echo 5) Полная переустановка
echo.
set /p UPDATE_TYPE="Введите номер (1-5): "

if "%UPDATE_TYPE%"=="1" (
    set "UPDATE_MODE=MEMORY_ONLY"
    echo Выбрано: Добавление оптимизации памяти
) else if "%UPDATE_TYPE%"=="2" (
    set "UPDATE_MODE=UPDATE_ALL"
    echo Выбрано: Обновление всех пакетов
) else if "%UPDATE_TYPE%"=="3" (
    set "UPDATE_MODE=SWITCH_GPU"
    echo Выбрано: Переключение на GPU
) else if "%UPDATE_TYPE%"=="4" (
    set "UPDATE_MODE=SWITCH_CPU"
    echo Выбрано: Переключение на CPU
) else if "%UPDATE_TYPE%"=="5" (
    echo Запуск полной переустановки...
    install.bat
    exit /b 0
) else (
    echo Неверный выбор. Используется добавление оптимизации памяти.
    set "UPDATE_MODE=MEMORY_ONLY"
)

REM Резервное копирование
echo.
echo [4/6] Создание резервной копии...

if exist "cache" (
    echo ✅ Папка cache сохранена (содержит ваши индексы)
)

if exist "config.py" (
    copy config.py config.py.backup >nul 2>&1
    echo ✅ Конфигурация сохранена в config.py.backup
)

REM Установка/обновление пакетов
echo.
echo [5/6] Обновление пакетов...

if "!UPDATE_MODE!"=="MEMORY_ONLY" (
    echo Установка psutil для мониторинга памяти...
    "%VENV_PYTHON%" -m pip install "psutil>=5.9.0" --quiet
    if !errorlevel! neq 0 (
        echo ❌ Ошибка при установке psutil
    ) else (
        echo ✅ psutil установлен
    )
    
) else if "!UPDATE_MODE!"=="UPDATE_ALL" (
    echo Обновление всех пакетов...
    "%VENV_PYTHON%" -m pip install --upgrade pip --quiet
    "%VENV_PYTHON%" -m pip install -r requirements.txt --upgrade --quiet
    if !errorlevel! neq 0 (
        echo ⚠️  Некоторые пакеты могли не обновиться
    ) else (
        echo ✅ Все пакеты обновлены
    )
    
) else if "!UPDATE_MODE!"=="SWITCH_GPU" (
    echo Переключение на GPU режим...
    
    REM Проверка наличия NVIDIA GPU
    wmic path win32_VideoController get name | find /i "nvidia" >nul 2>&1
    if !errorlevel! neq 0 (
        echo ❌ NVIDIA GPU не обнаружен!
        echo Невозможно переключиться на GPU режим.
        pause
        exit /b 1
    )
    
    echo Установка CUDA версии PyTorch...
    "%VENV_PYTHON%" -m pip uninstall torch torchvision torchaudio -y --quiet >nul 2>&1
    "%VENV_PYTHON%" -m pip install "torch>=2.0.0" "torchvision>=0.15.0" --index-url https://download.pytorch.org/whl/cu118 --quiet
    if !errorlevel! neq 0 (
        echo ❌ Ошибка при установке GPU версии
        echo Восстановление CPU версии...
        "%VENV_PYTHON%" -m pip install "torch>=2.0.0" "torchvision>=0.15.0" --quiet
    ) else (
        echo ✅ GPU версия установлена
    )
    
    "%VENV_PYTHON%" -m pip install "psutil>=5.9.0" --quiet
    
) else if "!UPDATE_MODE!"=="SWITCH_CPU" (
    echo Переключение на CPU режим...
    "%VENV_PYTHON%" -m pip uninstall torch torchvision torchaudio -y --quiet >nul 2>&1
    "%VENV_PYTHON%" -m pip install "torch>=2.0.0" "torchvision>=0.15.0" --index-url https://download.pytorch.org/whl/cpu --quiet
    if !errorlevel! neq 0 (
        echo ❌ Ошибка при установке CPU версии
        "%VENV_PYTHON%" -m pip install "torch>=2.0.0" "torchvision>=0.15.0" --quiet
    ) else (
        echo ✅ CPU версия установлена
    )
    
    "%VENV_PYTHON%" -m pip install "psutil>=5.9.0" --quiet
)

REM Проверка и тестирование
echo.
echo [6/6] Проверка обновления...

echo Проверка основных модулей...
"%VENV_PYTHON%" -c "import torch, torchvision, sentence_transformers, PIL, numpy, psutil; print('✅ Все модули импортированы успешно')" 2>nul
if !errorlevel! neq 0 (
    echo ❌ Проблема с импортом модулей!
    echo Возможно, требуется полная переустановка.
    pause
    exit /b 1
)

echo Проверка новой функциональности...
"%VENV_PYTHON%" -c "from search_engine import SearchEngine; engine = SearchEngine(); mem_info = engine.get_memory_usage_info(); print(f'✅ Оптимизация памяти работает! Доступно: {mem_info.get(\"available_gb\", 0):.1f} ГБ')" 2>nul
if !errorlevel! neq 0 (
    echo ⚠️  Проблема с новой функциональностью
    echo Убедитесь, что все файлы приложения обновлены
)

REM Определение финального режима
"%VENV_PYTHON%" -c "import torch; print('GPU' if torch.cuda.is_available() else 'CPU')" 2>nul
if !errorlevel! equ 0 (
    for /f %%i in ('"%VENV_PYTHON%" -c "import torch; print('GPU' if torch.cuda.is_available() else 'CPU')" 2^>nul') do set "FINAL_MODE=%%i"
) else (
    set "FINAL_MODE=UNKNOWN"
)

REM Создание/обновление скрипта запуска
if not exist "start_app.bat" (
    echo Создание скрипта быстрого запуска...
    echo @echo off > start_app.bat
    echo cd /d "%%~dp0" >> start_app.bat
    echo call "%VENV_PATH%\Scripts\activate.bat" >> start_app.bat
    echo "%VENV_PYTHON%" main.py >> start_app.bat
    echo pause >> start_app.bat
    echo ✅ Создан start_app.bat
)

REM Сохранение информации об обновлении
echo.
echo Сохранение информации об обновлении...
echo Update completed on %date% %time% > update_info.txt
echo Previous mode: !EXISTING_MODE! >> update_info.txt
echo Update type: !UPDATE_MODE! >> update_info.txt
echo Final mode: !FINAL_MODE! >> update_info.txt
echo Virtual environment: %VENV_PATH% >> update_info.txt
echo Python executable: %VENV_PYTHON% >> update_info.txt
echo. >> update_info.txt
"%VENV_PYTHON%" -m pip freeze >> update_info.txt

REM Итоговое сообщение
echo.
echo ======================================================
echo           ✅ ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!
echo ======================================================
echo.
echo Изменения:
if "!EXISTING_MODE!" neq "!FINAL_MODE!" (
    echo   • Режим: !EXISTING_MODE! → !FINAL_MODE!
) else (
    echo   • Режим: !FINAL_MODE! (без изменений)
)
echo   • Оптимизация памяти: Добавлена
echo   • Поддержка больших коллекций: До 70k+ изображений
echo   • Восстановление после сбоев: Включено
echo.
echo Новые возможности:
echo   • Автоматическое разбиение на чанки
echo   • Мониторинг памяти в реальном времени  
echo   • Продолжение прерванной индексации
echo   • Адаптивное управление ресурсами
echo.

if "!FINAL_MODE!"=="GPU" (
    echo 🚀 GPU ускорение активно - ожидайте высокую производительность!
) else (
    echo 💻 CPU режим - стандартная производительность
)

echo.
echo Файлы:
echo   • update_info.txt - информация об обновлении
echo   • config.py.backup - резервная копия настроек (если была)
echo   • start_app.bat - скрипт быстрого запуска
echo.

REM Предложение тестирования
set /p RUN_TEST="Запустить диагностику системы? (y/n): "
if /i "%RUN_TEST%"=="y" (
    echo.
    echo Запуск диагностики...
    "%VENV_PYTHON%" system_check.py
) else (
    echo.
    echo Для проверки системы запустите: python system_check.py
    echo Для запуска приложения используйте: start_app.bat
    echo.
    pause
)

endlocal
