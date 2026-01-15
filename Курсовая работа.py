import sys
import os
import platform
import subprocess
import socket
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QGridLayout, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class SecurityChecker:
    def __init__(self):
        self.results = {
            'internet': None,
            'antivirus_installed': None,
            'firewall_installed': None,
            'antivirus_working': None,
            'firewall_working': None
        }

    def check_internet_connection(self):
        """Проверяем интернет через пинг нескольких хостов"""
        test_hosts = ['8.8.8.8', '1.1.1.1', 'ya.ru']
        
        for host in test_hosts:
            try:
                if platform.system().lower() == 'windows':
                    param = '-n'
                else:
                    param = '-c'
                    
                cmd = ['ping', param, '1', host]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, timeout=5)
                
                if result.returncode == 0:
                    self.results['internet'] = True
                    return True, f"Соединение есть (пинг {host} прошел)"
                    
            except:
                continue
        
        self.results['internet'] = False
        return False, "Интернет недоступен"

    def check_antivirus_installed(self):
        """Ищем популярные антивирусы по путям"""
        paths = {
            'Windows Defender': r'C:\Program Files\Windows Defender\MsMpEng.exe',
            'Kaspersky': r'C:\Program Files (x86)\Kaspersky Lab',
            'Dr.Web': r'C:\Program Files\DrWeb',
            'ESET NOD32': r'C:\Program Files\ESET',
            'Avast': r'C:\Program Files\Avast Software'
        }
        
        found = []
        if platform.system().lower() == 'windows':
            for name, path in paths.items():
                if os.path.exists(path):
                    found.append(name)
        
        if found:
            self.results['antivirus_installed'] = found
            return True, f"Найдено: {', '.join(found)}"
        else:
            self.results['antivirus_installed'] = []
            return False, "Антивирус не найден"

    def check_firewall_installed(self):
        """Проверяем наличие файрвола"""
        found = []
        
        if platform.system().lower() == 'windows':
            # Проверяем встроенный файрвол
            try:
                result = subprocess.run(['netsh', 'advfirewall', 'show', 
                                       'allprofiles', 'state'], 
                                      capture_output=True, text=True)
                if 'ON' in result.stdout.upper() or 'ВКЛ' in result.stdout.upper():
                    found.append('Windows Firewall')
            except:
                pass
            
            # Проверяем сторонние
            fw_paths = {
                'Kaspersky IS': r'C:\Program Files (x86)\Kaspersky Lab',
                'Comodo': r'C:\Program Files\COMODO'
            }
            
            for name, path in fw_paths.items():
                if os.path.exists(path):
                    found.append(name)
        
        if found:
            self.results['firewall_installed'] = found
            return True, f"Файрволы: {', '.join(found)}"
        else:
            self.results['firewall_installed'] = []
            return False, "Файрвол не обнаружен"

    def check_antivirus_working(self):
        """Тестируем антивирус EICAR файлом"""
        eicar = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        test_file = "eicar_test.txt"
        
        try:
            with open(test_file, 'w') as f:
                f.write(eicar)
            time.sleep(2)
            
            if os.path.exists(test_file):
                os.remove(test_file)
                self.results['antivirus_working'] = False
                return False, "Антивирус пропустил EICAR тест"
            else:
                self.results['antivirus_working'] = True
                return True, "EICAR заблокирован - антивирус работает"
                
        except Exception:
            self.results['antivirus_working'] = True
            return True, "Антивирус сработал при записи файла"

    def check_firewall_working(self):
        """Проверяем блокировку портов локально"""
        ports = [135, 139, 445, 1433, 3389]
        blocked = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                res = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                
                if res != 0:  # порт закрыт/заблокирован
                    blocked.append(port)
            except:
                blocked.append(port)
        
        total = len(ports)
        blocked_count = len(blocked)
        
        if blocked_count >= 3:
            self.results['firewall_working'] = True
            return True, f"Заблокировано {blocked_count}/{total} портов - файрвол ок"
        else:
            self.results['firewall_working'] = False
            return False, f"Заблокировано только {blocked_count}/{total} - проблема с файрволом"

    def get_summary(self):
        """Формируем текстовый отчет"""
        report = "Результаты проверки безопасности\n"
        report += "=" * 40 + "\n\n"
        
        report += f"Интернет: {'OK' if self.results['internet'] else 'НЕТ'}\n\n"
        
        avs = self.results['antivirus_installed']
        report += f"Антивирус: {', '.join(avs) if avs else 'НЕ НАЙДЕН'}\n\n"
        
        fws = self.results['firewall_installed']
        report += f"Файрвол: {', '.join(fws) if fws else 'НЕ НАЙДЕН'}\n\n"
        
        av_work = self.results['antivirus_working']
        fw_work = self.results['firewall_working']
        
        report += f"Тест АВ: {'OK' if av_work else 'ПЛОХО' if av_work is not None else '?'}\n\n"
        report += f"Тест файрвола: {'OK' if fw_work else 'ПЛОХО' if fw_work is not None else '?'}\n"
        
        return report

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.checker = SecurityChecker()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Проверка безопасности ПК')
        self.setGeometry(100, 100, 800, 700)
        
        # Цвета (простые)
        self.bg_color = '#f5f5f5'
        self.btn_color = '#27ae60'
        self.text_color = '#2c3e50'
        self.white = '#ffffff'
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel('Проверка безопасности компьютера')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Кнопки в сетке
        grid = QGridLayout()
        grid.setSpacing(15)
        
        buttons = [
            ('Интернет', self.check_internet),
            ('Антивирус', self.check_av),
            ('Файрвол', self.check_fw),
            ('Тест АВ', self.check_av_work),
            ('Тест файрвола', self.check_fw_work)
        ]
        
        for i, (text, func) in enumerate(buttons):
            btn = QPushButton(text)
            btn.clicked.connect(func)
            btn.setFont(QFont('Arial', 11, QFont.Bold))
            btn.setMinimumHeight(60)
            self.style_btn(btn)
            grid.addWidget(btn, i // 2, i % 2)
        
        # Полная проверка
        full_btn = QPushButton('Полная проверка')
        full_btn.clicked.connect(self.full_check)
        full_btn.setFont(QFont('Arial', 12, QFont.Bold))
        full_btn.setMinimumHeight(60)
        full_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.btn_color};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                padding: 15px;
            }}
            QPushButton:hover {{
                background-color: #219a52;
            }}
        """)
        grid.addWidget(full_btn, 3, 0, 1, 2)
        
        layout.addLayout(grid)
        
        # Область результатов
        self.results_label = QLabel('Нажмите кнопку для проверки')
        self.results_label.setFont(QFont('Courier', 11))
        self.results_label.setStyleSheet(f"""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            min-height: 120px;
        """)
        self.results_label.setWordWrap(True)
        self.results_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.results_label)
        
        # Кнопка детального отчета
        summary_btn = QPushButton('Подробный отчет')
        summary_btn.clicked.connect(self.show_summary)
        summary_btn.setMinimumHeight(50)
        self.style_btn(summary_btn)
        layout.addWidget(summary_btn)
        
        self.setLayout(layout)

    def style_btn(self, btn):
        """Стиль для обычных кнопок"""
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: {self.text_color};
                border: 2px solid {self.btn_color};
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.btn_color};
                color: white;
            }}
        """)

    def show_result(self, title, message, success=True):
        """Показываем popup с результатом"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        
        color = '#27ae60' if success else '#e74c3c'
        msg.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {color};
            }}
            QLabel {{
                color: {self.text_color};
            }}
        """)
        msg.exec_()

    def update_results(self, msg):
        self.results_label.setText(msg)

    def check_internet(self):
        ok, msg = self.checker.check_internet_connection()
        self.show_result('Интернет', msg, ok)
        self.update_results(msg)

    def check_av(self):
        ok, msg = self.checker.check_antivirus_installed()
        self.show_result('Антивирус', msg, ok)
        self.update_results(msg)

    def check_fw(self):
        ok, msg = self.checker.check_firewall_installed()
        self.show_result('Файрвол', msg, ok)
        self.update_results(msg)

    def check_av_work(self):
        ok, msg = self.checker.check_antivirus_working()
        self.show_result('Тест антивируса', msg, ok)
        self.update_results(msg)

    def check_fw_work(self):
        ok, msg = self.checker.check_firewall_working()
        self.show_result('Тест файрвола', msg, ok)
        self.update_results(msg)

    def full_check(self):
        """Запускаем все тесты"""
        self.checker.check_internet_connection()
        self.checker.check_antivirus_installed()
        self.checker.check_firewall_installed()
        self.checker.check_antivirus_working()
        self.checker.check_firewall_working()
        
        summary = self.checker.get_summary()
        self.update_results(summary)
        self.show_result('Готово', 'Все проверки завершены', True)

    def show_summary(self):
        summary = self.checker.get_summary()
        msg = QMessageBox(self)
        msg.setWindowTitle('Отчет')
        msg.setText(summary)
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
