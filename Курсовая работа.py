import sys
import os
import platform
import subprocess
import socket
import time
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
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
        test_hosts = ['8.8.8.8', '1.1.1.1', 'ya.ru']
        for host in test_hosts:
            try:
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                command = ['ping', param, '1', host]
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
                if result.returncode == 0:
                    self.results['internet'] = True
                    return True, f"✓ Соединение с Интернетом установлено (через {host})"
            except Exception:
                continue
        self.results['internet'] = False
        return False, "✗ Соединение с Интернетом отсутствует"

    def check_antivirus_installed(self):
        antivirus_paths = {
            'Windows Defender': 'C:\\Program Files\\Windows Defender\\MsMpEng.exe',
            'Kaspersky': 'C:\\Program Files (x86)\\Kaspersky Lab',
            'Dr.Web': 'C:\\Program Files\\DrWeb',
            'ESET NOD32': 'C:\\Program Files\\ESET',
            'Avast': 'C:\\Program Files\\Avast Software'
        }
        found_antivirus = []
        if platform.system().lower() == 'windows':
            for av_name, av_path in antivirus_paths.items():
                if os.path.exists(av_path):
                    found_antivirus.append(av_name)
        if found_antivirus:
            self.results['antivirus_installed'] = found_antivirus
            return True, f"✓ Обнаружено: {', '.join(found_antivirus)}"
        else:
            self.results['antivirus_installed'] = []
            return False, "✗ Антивирусное ПО не обнаружено"

    def check_firewall_installed(self):
        found_firewall = []
        if platform.system().lower() == 'windows':
            try:
                result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], capture_output=True, text=True)
                if 'ON' in result.stdout.upper() or 'ВКЛ' in result.stdout.upper():
                    found_firewall.append('Windows Firewall')
            except Exception:
                pass
            firewall_paths = {
                'Kaspersky Internet Security': 'C:\\Program Files (x86)\\Kaspersky Lab',
                'Comodo Firewall': 'C:\\Program Files\\COMODO'
            }
            for fw_name, fw_path in firewall_paths.items():
                if os.path.exists(fw_path):
                    found_firewall.append(fw_name)
        if found_firewall:
            self.results['firewall_installed'] = found_firewall
            return True, f"✓ Обнаружено: {', '.join(found_firewall)}"
        else:
            self.results['firewall_installed'] = []
            return False, "✗ МЭ не обнаружен"

    def check_antivirus_working(self):
        eicar_string = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        test_file = "eicar_test.txt"
        try:
            with open(test_file, 'w') as f:
                f.write(eicar_string)
            time.sleep(2)
            if os.path.exists(test_file):
                os.remove(test_file)
                self.results['antivirus_working'] = False
                return False, "✗ Антивирус не среагировал на тестовый файл EICAR"
            else:
                self.results['antivirus_working'] = True
                return True, "✓ Тестовый файл EICAR заблокирован или удален, антивирус работает корректно"
        except Exception:
            self.results['antivirus_working'] = True
            return True, "✓ Антивирус заблокировал создание файла: защита работает"

    def check_firewall_working(self):
        test_ports = [135, 139, 445, 1433, 3389]
        blocked_ports = []
        for port in test_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                if result != 0:
                    blocked_ports.append(port)
            except Exception:
                blocked_ports.append(port)
        if len(blocked_ports) >= 3:
            self.results['firewall_working'] = True
            return True, f"✓ Заблокировано портов: {len(blocked_ports)}/{len(test_ports)} - МЭ работает корректно"
        else:
            self.results['firewall_working'] = False
            return False, f"✗ Заблокировано портов: {len(blocked_ports)}/{len(test_ports)} - МЭ работает некорректно/отключен"

    def get_summary(self):
        summary = "РЕЗУЛЬТАТЫ ПРОВЕРКИ СИСТЕМЫ БЕЗОПАСНОСТИ\n"
        summary += "━" * 50 + "\n\n"
        summary += f"1. Интернет: {'✓ Доступно' if self.results['internet'] else '✗ Отсутствует'}\n\n"
        avs = self.results['antivirus_installed']
        summary += f"2. Антивирус: {('✓ ' + ', '.join(avs)) if avs else '✗ Не обнаружено'}\n\n"
        fws = self.results['firewall_installed']
        summary += f"3. Межсетевой экран: {('✓ ' + ', '.join(fws)) if fws else '✗ Не обнаружен'}\n\n"
        av_work = self.results['antivirus_working']
        fw_work = self.results['firewall_working']
        summary += f"4. Работоспособность антивируса: {'✓' if av_work else '✗' if av_work is not None else '?'}\n\n"
        summary += f"5. Работоспособность МЭ: {'✓' if fw_work else '✗' if fw_work is not None else '?'}\n"
        return summary

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.checker = SecurityChecker()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Курсовая работа Елина ВВ')
        self.setGeometry(100, 100, 800, 700)
        
        # Цвета
        self.color_dark_gray = '#2C3E50'
        self.color_light_gray = '#ECF0F1'
        self.color_mint = '#1ABC9C'
        self.color_light_mint = '#16A085'
        self.color_white = '#FFFFFF'
        self.color_text = '#2C3E50'
        
        # Главный layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Верхний баннер
        banner = QWidget()
        banner.setStyleSheet(f"background-color: {self.color_mint};")
        banner_layout = QVBoxLayout()
        banner_layout.setContentsMargins(20, 25, 20, 25)
        
        title = QLabel('Проверка безопасности ПК')
        title_font = QFont('Arial', 24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {self.color_white};")
        banner_layout.addWidget(title)
        
        subtitle = QLabel('Комплексное тестирование систем защиты')
        subtitle_font = QFont('Arial', 11)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet(f"color: {self.color_white}; opacity: 0.9;")
        banner_layout.addWidget(subtitle)
        
        banner.setLayout(banner_layout)
        main_layout.addWidget(banner)
        
        # Центральная область
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {self.color_light_gray};")
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(30, 30, 30, 30)
        central_layout.setSpacing(15)
        
        # Сетка кнопок
        buttons_layout = QtWidgets.QGridLayout()
        buttons_layout.setSpacing(15)
        
        buttons_info = [
            ('Интернет', self.check_internet, 0, 0),
            ('Антивирус', self.check_av, 0, 1),
            ('Межсетевой экран', self.check_fw, 1, 0),
            ('Работа АВ', self.check_av_work, 1, 1),
            ('Работа МЭ', self.check_fw_work, 2, 0),
        ]
        
        for text, func, row, col in buttons_info:
            btn = QPushButton(text)
            btn_font = QFont('Arial', 10)
            btn.setFont(btn_font)
            btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(func)
            btn.setMinimumHeight(80)
            self.style_button(btn, is_primary=False)
            buttons_layout.addWidget(btn, row, col)
        
        # Полная проверка (во весь ряд)
        btn_full = QPushButton('⚡ ПОЛНАЯ ПРОВЕРКА')
        btn_full_font = QFont('Arial', 11)
        btn_full_font.setBold(True)
        btn_full.setFont(btn_full_font)
        btn_full.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_full.clicked.connect(self.full_check)
        btn_full.setMinimumHeight(60)
        self.style_button(btn_full, is_primary=True)
        buttons_layout.addWidget(btn_full, 2, 1)
        
        central_layout.addLayout(buttons_layout)
        central_layout.addStretch()
        
        # Результаты
        results_label = QLabel('Результаты последней проверки:')
        results_label_font = QFont('Arial', 12)
        results_label_font.setBold(True)
        results_label.setFont(results_label_font)
        results_label.setStyleSheet(f"color: {self.color_text};")
        central_layout.addWidget(results_label)
        
        self.results_display = QLabel('Выполните проверку для получения результатов')
        self.results_display.setFont(QFont('Courier', 10))
        self.results_display.setStyleSheet(f"background-color: {self.color_white}; color: {self.color_text}; padding: 15px; border-radius: 5px; border: 1px solid #BDC3C7;")
        self.results_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.results_display.setWordWrap(True)
        self.results_display.setMinimumHeight(150)
        central_layout.addWidget(self.results_display)
        
        # Кнопка показать результаты
        btn_summary = QPushButton('Показать полные результаты')
        btn_summary_font = QFont('Arial', 10)
        btn_summary.setFont(btn_summary_font)
        btn_summary.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_summary.clicked.connect(self.show_summary)
        btn_summary.setMinimumHeight(45)
        self.style_button(btn_summary, is_primary=False)
        central_layout.addWidget(btn_summary)
        
        central_widget.setLayout(central_layout)
        main_layout.addWidget(central_widget, 1)
        
        # Нижний подвал
        footer = QWidget()
        footer.setStyleSheet(f"background-color: {self.color_dark_gray};")
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(20, 15, 20, 15)
        
        footer_text = QLabel('Курсовая работа • Методы и средства защиты информации в компьютерных сетях • Елина ВВ • БСТ2204')
        footer_text_font = QFont('Arial', 9)
        footer_text.setFont(footer_text_font)
        footer_text.setStyleSheet(f"color: {self.color_light_gray};")
        footer_layout.addWidget(footer_text)
        footer_layout.addStretch()
        
        footer.setLayout(footer_layout)
        main_layout.addWidget(footer)
        
        self.setLayout(main_layout)

    def style_button(self, button, is_primary=False):
        if is_primary:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.color_mint};
                    color: {self.color_white};
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    font-weight: bold;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {self.color_light_mint};
                }}
                QPushButton:pressed {{
                    background-color: #0E8B6F;
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.color_white};
                    color: {self.color_text};
                    border: 2px solid {self.color_mint};
                    border-radius: 8px;
                    padding: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.color_light_mint};
                    color: {self.color_white};
                    border: 2px solid {self.color_light_mint};
                }}
                QPushButton:pressed {{
                    background-color: #0E8B6F;
                    color: {self.color_white};
                }}
            """)

    def show_result(self, title, message, is_success=True):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg_font = QFont('Arial', 10)
        msg.setFont(msg_font)
        
        if is_success:
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.color_white};
                }}
                QMessageBox QLabel {{
                    color: {self.color_text};
                }}
                QPushButton {{
                    background-color: {self.color_mint};
                    color: {self.color_white};
                    border: none;
                    border-radius: 5px;
                    padding: 5px 20px;
                    min-width: 60px;
                }}
                QPushButton:hover {{
                    background-color: {self.color_light_mint};
                }}
            """)
        else:
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {self.color_white};
                }}
                QMessageBox QLabel {{
                    color: #E74C3C;
                }}
                QPushButton {{
                    background-color: #E74C3C;
                    color: {self.color_white};
                    border: none;
                    border-radius: 5px;
                    padding: 5px 20px;
                    min-width: 60px;
                }}
                QPushButton:hover {{
                    background-color: #C0392B;
                }}
            """)
        
        msg.exec_()

    def update_results_display(self, message):
        self.results_display.setText(message)

    def check_internet(self):
        ok, msg = self.checker.check_internet_connection()
        self.show_result('Проверка Интернета', msg, ok)
        self.update_results_display(msg)

    def check_av(self):
        ok, msg = self.checker.check_antivirus_installed()
        self.show_result('Проверка антивируса', msg, ok)
        self.update_results_display(msg)

    def check_fw(self):
        ok, msg = self.checker.check_firewall_installed()
        self.show_result('Проверка межсетевого экрана', msg, ok)
        self.update_results_display(msg)

    def check_av_work(self):
        ok, msg = self.checker.check_antivirus_working()
        self.show_result('Проверка работоспособности антивируса', msg, ok)
        self.update_results_display(msg)

    def check_fw_work(self):
        ok, msg = self.checker.check_firewall_working()
        self.show_result('Проверка работоспособности МЭ', msg, ok)
        self.update_results_display(msg)

    def full_check(self):
        self.checker.check_internet_connection()
        self.checker.check_antivirus_installed()
        self.checker.check_firewall_installed()
        self.checker.check_antivirus_working()
        self.checker.check_firewall_working()
        summary = self.checker.get_summary()
        self.update_results_display(summary)
        self.show_result('Полная проверка', 'Комплексная проверка завершена!\n\nСм. результаты ниже.', True)

    def show_summary(self):
        summary = self.checker.get_summary()
        msg = QMessageBox(self)
        msg.setWindowTitle('Полные результаты проверки')
        msg.setText(summary)
        msg_font = QFont('Courier', 10)
        msg.setFont(msg_font)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {self.color_white};
            }}
            QMessageBox QLabel {{
                color: {self.color_text};
            }}
            QPushButton {{
                background-color: {self.color_mint};
                color: {self.color_white};
                border: none;
                border-radius: 5px;
                padding: 5px 20px;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: {self.color_light_mint};
            }}
        """)
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
