#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания исполняемого файла (.exe)
"""

import subprocess
import sys
import os

def install_pyinstaller():
    """Устанавливает PyInstaller если его нет"""
    try:
        import PyInstaller
        print("✓ PyInstaller уже установлен")
        return True
    except ImportError:
        print("📦 Установка PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✓ PyInstaller успешно установлен")
            return True
        except Exception as e:
            print(f"❌ Ошибка установки PyInstaller: {e}")
            print("\nПопробуйте установить вручную:")
            print("pip install pyinstaller")
            return False

def build_exe():
    """Создает исполняемый файл"""
    print("\n" + "="*60)
    print("🔨 Создание исполняемого файла...")
    print("="*60 + "\n")
    
    # Команда для PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",  # Один файл
        "--console",  # Консольное приложение
        "--name=Проверка_Безопасности_Сайта",  # Имя файла
        "--clean",  # Очистить кэш
        "--noconfirm",  # Не спрашивать подтверждение
        "security_checker.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*60)
        print("✅ ГОТОВО! Исполняемый файл создан!")
        print("="*60)
        print("\n📁 Файл находится в папке: dist/Проверка_Безопасности_Сайта.exe")
        print("\n💡 Вы можете скопировать этот .exe файл на любой компьютер с Windows")
        print("   и запустить его без установки Python или других программ!\n")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при создании файла: {e}")
        print("\nПопробуйте выполнить команду вручную:")
        print("pyinstaller --onefile --console --name=Проверка_Безопасности_Сайта security_checker.py")
        sys.exit(1)

if __name__ == "__main__":
    print("="*60)
    print("🔧 СБОРКА ИСПОЛНЯЕМОГО ФАЙЛА")
    print("="*60)
    print("\nЭтот скрипт создаст один .exe файл, который можно")
    print("запускать на любом Windows компьютере без Python!\n")
    
    if not install_pyinstaller():
        sys.exit(1)
    
    build_exe()
    
    print("\n" + "="*60)
    print("✨ Всё готово! Теперь вы можете распространять")
    print("   файл Проверка_Безопасности_Сайта.exe")
    print("="*60)

