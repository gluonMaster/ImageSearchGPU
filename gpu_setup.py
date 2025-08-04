"""
Скрипт для проверки и настройки GPU поддержки.
Поможет настроить RTX 2060 для ускорения работы приложения.
"""

import subprocess
import sys

def check_gpu_support():
    """Проверка текущей поддержки GPU."""
    print("=== ПРОВЕРКА GPU ПОДДЕРЖКИ ===")
    
    try:
        import torch
        print(f"✅ PyTorch установлен: {torch.__version__}")
        
        cuda_available = torch.cuda.is_available()
        print(f"CUDA доступна: {'✅ Да' if cuda_available else '❌ Нет'}")
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            print(f"Количество GPU: {device_count}")
            
            for i in range(device_count):
                gpu_name = torch.cuda.get_device_name(i)
                props = torch.cuda.get_device_properties(i)
                memory_gb = props.total_memory / 1024**3
                compute_capability = f"{props.major}.{props.minor}"
                
                print(f"GPU {i}: {gpu_name}")
                print(f"  Память: {memory_gb:.1f} ГБ")
                print(f"  Compute Capability: {compute_capability}")
                
                # Проверка совместимости с RTX 2060
                if "2060" in gpu_name:
                    print(f"  🎯 RTX 2060 обнаружена! Отлично подходит для ускорения.")
                    
            if torch.version.cuda:
                print(f"CUDA версия PyTorch: {torch.version.cuda}")
            else:
                print("❌ PyTorch установлен БЕЗ поддержки CUDA")
                return False
                
        else:
            print("❌ CUDA недоступна")
            return False
            
        return True
        
    except ImportError:
        print("❌ PyTorch не установлен")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        return False

def install_cuda_pytorch():
    """Установка PyTorch с поддержкой CUDA."""
    print("\n=== УСТАНОВКА PYTORCH С CUDA ===")
    
    print("Удаление текущей версии PyTorch...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "-y"])
    
    print("Установка PyTorch с CUDA 11.8 (рекомендуется для RTX 2060)...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "torch", "torchvision", 
        "--index-url", "https://download.pytorch.org/whl/cu118"
    ])
    
    if result.returncode == 0:
        print("✅ PyTorch с CUDA установлен успешно!")
        return True
    else:
        print("❌ Ошибка при установке PyTorch с CUDA")
        return False

def test_gpu_performance():
    """Тест производительности GPU."""
    print("\n=== ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ GPU ===")
    
    try:
        import torch
        import time
        
        if not torch.cuda.is_available():
            print("❌ CUDA недоступна для тестирования")
            return
        
        device = torch.device('cuda')
        print(f"Тестирование на: {torch.cuda.get_device_name(0)}")
        
        # Тест скорости вычислений
        size = 1000
        print(f"Создание матриц {size}x{size}...")
        
        # CPU тест
        start_time = time.time()
        a_cpu = torch.randn(size, size)
        b_cpu = torch.randn(size, size)
        c_cpu = torch.mm(a_cpu, b_cpu)
        cpu_time = time.time() - start_time
        
        # GPU тест
        start_time = time.time()
        a_gpu = torch.randn(size, size, device=device)
        b_gpu = torch.randn(size, size, device=device)
        torch.cuda.synchronize()  # Ждем завершения операций
        
        start_compute = time.time()
        c_gpu = torch.mm(a_gpu, b_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start_compute
        
        print(f"CPU время: {cpu_time:.3f} сек")
        print(f"GPU время: {gpu_time:.3f} сек")
        print(f"Ускорение: {cpu_time/gpu_time:.1f}x")
        
        # Проверка памяти GPU
        memory_allocated = torch.cuda.memory_allocated() / 1024**2
        memory_reserved = torch.cuda.memory_reserved() / 1024**2
        print(f"Используется GPU памяти: {memory_allocated:.1f} МБ")
        print(f"Зарезервировано: {memory_reserved:.1f} МБ")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

def check_nvidia_driver():
    """Проверка драйвера NVIDIA."""
    print("\n=== ПРОВЕРКА ДРАЙВЕРА NVIDIA ===")
    
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Драйвер NVIDIA установлен:")
            print(result.stdout)
        else:
            print("❌ nvidia-smi не найден")
            print("Установите драйвер NVIDIA с официального сайта")
    except FileNotFoundError:
        print("❌ nvidia-smi не найден")
        print("Установите драйвер NVIDIA с официального сайта")

def main():
    """Главная функция скрипта настройки GPU."""
    print("=== НАСТРОЙКА GPU ДЛЯ ПРИЛОЖЕНИЯ ПОИСКА ИЗОБРАЖЕНИЙ ===")
    print("Этот скрипт поможет настроить RTX 2060 для ускорения работы")
    print()
    
    # Проверка драйвера
    check_nvidia_driver()
    
    # Проверка текущего состояния
    gpu_ready = check_gpu_support()
    
    if not gpu_ready:
        print("\n🔧 CUDA поддержка не найдена. Нужна установка PyTorch с CUDA.")
        
        response = input("Установить PyTorch с поддержкой CUDA? (y/n): ").lower()
        if response == 'y':
            success = install_cuda_pytorch()
            if success:
                print("\n🔄 Проверяем установку...")
                gpu_ready = check_gpu_support()
            else:
                print("❌ Установка не удалась")
                return
    
    if gpu_ready:
        print("\n🚀 GPU поддержка готова!")
        test_gpu_performance()
        
        print("\n=== РЕКОМЕНДАЦИИ ===")
        print("✅ Ваша RTX 2060 готова к использованию!")
        print("✅ Приложение автоматически будет использовать GPU")
        print("✅ Ожидаемое ускорение: 3-10x по сравнению с CPU")
        print("✅ Можете увеличить размер батча в config.py для лучшей производительности")
        
    else:
        print("\n❌ GPU поддержка не настроена")
        print("Возможные проблемы:")
        print("1. Не установлен драйвер NVIDIA")
        print("2. Устаревший драйвер")
        print("3. Проблемы с PyTorch")
        print("\nПроверьте драйвер на сайте NVIDIA и повторите настройку")

if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")
