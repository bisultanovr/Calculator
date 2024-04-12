import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from CalculatorUI import Ui_MainWindow  # Импортируем сгенерированный файл
import math

# Ввести состояния: ввод первого операнда и ввод второго операнда.
# Нажатие кнопки вычисления приводит к сбросу состояний, то есть приходим в начальное состояние 1.
# При нажатии кнопки оператора операнд1 инициализируется введённым значением, операнд2 имеет такое же значение,
# если нет ввода другого значения, в таком случае нажатие кнопки другого оператора приводит к смене оператора
# Если ввод есть, то операнд2 перезаписывается.
# При нажатии кнопки вычисления операнд1 получает значение результата, если нет ввода нового значения операнда1,
# если оно есть, то всё выглядит как с самого начала.
#

# Нужно сделать:
# Разобраться со сложением.
# Переделать MemoryReg.
# Добавить оставшиеся операции.


class Calculator(QMainWindow):
    def __init__(self):
        super(Calculator, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        loadUi("Calculator.ui", self)
        self.setWindowTitle("Calculator")

        self.operator = None        # Какую операцию выполняем (str)

        self.operand1 = 0
        self.operand2 = 0
        self.result = 0

        # Определяет какой операнд сейчас вводится
        # True - operand1
        # False - operand2
        self.input_operand = True

        # Полное выражение, которое будет выводиться в MemoryReg
        # 0 - operand1, 1 - operator, 2 - operand2
        self.expression = ["", "", ""]

        # Выражение, которое будет выводиться в MemoryReg
        # Это будет либо просто число, либо sqr(x), либо √x, либо 1/(x)
        # Для двух операндов
        #self.unary_expression1 = None
        #self.unary_expression2 = None

        self.int_part = True        # Вводится целая часть (True) или дробная (False)
        self.fractional_part = 0    # разрядность дробной части

        # Символы операций
        self.add_char = '+'
        self.sub_char = '-'
        self.multiply_char = '×'
        self.divide_char = '÷'

        # Счётчик введённых цифр
        self.digits_count = 0

        # Размер шрифта регистра ввода по умолчанию
        self.default_entry_font_size = 38

        # Ввод операнда. Перед вводом очередного операнда (True) выполняем clear_entry
        self.enter_state = True
        # Если True, то можем выполнить операцию, иначе - не можем
        self.operand_is_changed = False
        # Выражение вычислено, перед вводом следующего числа выполняется clear_all
        self.expression_evaluated = False

        self.MemoryReg.clear()
        self.clear_entry()

        # Привязки кнопок к функциям
        self.btn_0.clicked.connect(lambda: self.on_btn_clicked_num(0))
        self.btn_1.clicked.connect(lambda: self.on_btn_clicked_num(1))
        self.btn_2.clicked.connect(lambda: self.on_btn_clicked_num(2))
        self.btn_3.clicked.connect(lambda: self.on_btn_clicked_num(3))
        self.btn_4.clicked.connect(lambda: self.on_btn_clicked_num(4))
        self.btn_5.clicked.connect(lambda: self.on_btn_clicked_num(5))
        self.btn_6.clicked.connect(lambda: self.on_btn_clicked_num(6))
        self.btn_7.clicked.connect(lambda: self.on_btn_clicked_num(7))
        self.btn_8.clicked.connect(lambda: self.on_btn_clicked_num(8))
        self.btn_9.clicked.connect(lambda: self.on_btn_clicked_num(9))
        self.btn_backspace.clicked.connect(self.on_btn_clicked_backspace)
        self.btn_point.clicked.connect(self.on_btn_clicked_convertion)
        self.btn_sign.clicked.connect(self.on_btn_clicked_switch_sign)
        self.btn_add.clicked.connect(lambda: self.on_btn_clicked_operation(self.add_char))
        self.btn_sub.clicked.connect(lambda: self.on_btn_clicked_operation(self.sub_char))
        self.btn_multiply.clicked.connect(lambda: self.on_btn_clicked_operation(self.multiply_char))
        self.btn_divide.clicked.connect(lambda: self.on_btn_clicked_operation(self.divide_char))
        self.btn_square.clicked.connect(self.on_btn_clicked_square)
        self.btn_result.clicked.connect(self.calculate_result)
        self.btn_ce.clicked.connect(self.clear_entry)
        self.btn_c.clicked.connect(self.clear_all)

    def on_btn_clicked_num(self, num):
        if self.digits_count > 16:
            return

        self.digits_count += 1

        # Ввод operand
        if self.expression_evaluated:
            self.clear_all()
        self.expression_evaluated = False

        if self.enter_state:
            self.EnterReg.clear()
            self.result = 0
        self.enter_state = False

        self.operand_is_changed = True

        if self.int_part:
            self.result = self.result * 10 + int(num)
        else:
            self.fractional_part += 1
            self.result = self.result + num / 10 ** self.fractional_part
            self.result = int(self.result * 10 ** self.fractional_part) / 10 ** self.fractional_part

        current_text = self.EnterReg.text()
        new_text = current_text + str(num)
        self.EnterReg.setText(new_text)

        # self.result = float(self.EnterReg.text())

        # Регулируем размер регистра вывода
        self.adjust_entry_font_size()

    def on_btn_clicked_backspace(self):
        if not self.enter_state:        # Если пытаемся стереть уже полученный результат, то clear_all
            erased_char = self.EnterReg.text()[-1]
            if erased_char != '.' and int(erased_char) in range(int('0'), int('9') + 1):
                self.digits_count -= 1
            else:
                self.int_part = True

            self.EnterReg.setText(self.EnterReg.text()[:-1])
            if self.EnterReg.text() != "" and self.EnterReg.text() != "-":
                self.result = float(self.EnterReg.text())
            else:
                self.result = 0

            # Если дробная часть нулевая, она отбрасывается
            self.discard_zero_fractional_part()

            if self.result == 0:
                self.clear_entry()

            # Регулируем размер регистра вывода
            self.adjust_entry_font_size()
        else:
            self.clear_all()

    def on_btn_clicked_operation(self, operator):
        self.operator = operator

        self.enter_state = True
        self.expression_evaluated = False

        # вводимое число будет целым
        self.int_part = True
        self.fractional_part = 1

        # Если дробная часть нулевая, она отбрасывается
        self.discard_zero_fractional_part()

        self.operand2 = self.result

        # Выполняем операцию, если введён второй операнд
        if self.operand_is_changed:
            if operator is self.add_char:
                self.result = self.operand1 + self.operand2
            elif operator is self.sub_char:
                self.result = self.operand1 - self.operand2
            elif operator is self.multiply_char:
                self.result = self.operand1 * self.operand2
            elif operator is self.divide_char:
                self.result = self.operand1 / self.operand2

        self.operand1 = self.result

        # Если дробная часть нулевая, она отбрасывается
        self.discard_zero_fractional_part()

        self.operand2 = 0

        self.MemoryReg.setText(f"{self.operand1} {self.operator}")
        self.EnterReg.setText(str(self.result))

        self.operand_is_changed = False

    def calculate_result(self):
        self.enter_state = True

        # Ввод целого числа
        self.int_part = True
        self.fractional_part = 1

        # Если дробная часть нулевая, она отбрасывается
        self.discard_zero_fractional_part()

        self.operand2 = self.result
        # вычисляем выражение
        if self.operator is self.add_char:
            self.result = self.operand1 + self.operand2
        elif self.operator is self.sub_char:
            self.result = self.operand1 - self.operand2
        elif self.operator is self.multiply_char:
            self.result = self.operand1 * self.operand2
        elif self.operator is self.divide_char:
            self.result = self.operand1 / self.operand2
        else:
            self.operator = None

        # Если дробная часть нулевая, она отбрасывается
        self.discard_zero_fractional_part()

        if self.operator is not None:
            self.MemoryReg.setText(f"{self.operand1} {self.operator} {self.operand2} = ")
            self.EnterReg.setText(str(self.result))
            self.expression_evaluated = True
            self.operand_is_changed = True
            self.operator = None
        else:
            self.MemoryReg.setText(f"{self.operand1} = ")
            self.EnterReg.setText(str(self.result))

        self.operand1 = self.result
        self.operand2 = 0

        # Регулируем размер регистра вывода
        self.adjust_entry_font_size()

    def on_btn_clicked_square(self):
        self.result **= 2
        self.EnterReg.setText(str(self.result))

    def on_btn_clicked_convertion(self):
        if self.expression_evaluated:
            self.clear_all()
        self.expression_evaluated = False
        self.enter_state = False

        if self.int_part:
            self.int_part = False
            self.result = float(self.result)
            self.fractional_part = 0
            current_text = self.EnterReg.text()
            self.EnterReg.setText(current_text + '.')

            # Регулируем размер регистра вывода
            self.adjust_entry_font_size()

    def on_btn_clicked_switch_sign(self):
        self.result = -self.result
        self.EnterReg.setText(str(self.result))

        # Регулируем размер регистра вывода
        self.adjust_entry_font_size()

    def clear_entry(self):
        self.enter_state = True
        self.int_part = True
        self.operand_is_changed = False
        self.EnterReg.setText("0")
        self.operand2 = 0
        self.result = 0
        self.digits_count = 0

        # Регулируем размер регистра вывода
        self.adjust_entry_font_size()

    def clear_all(self):
        self.enter_state = True
        self.int_part = True
        self.operand_is_changed = False
        self.EnterReg.setText("0")
        self.MemoryReg.clear()
        self.operand1 = 0
        self.operand2 = 0
        self.result = 0
        self.digits_count = 0

        # Регулируем размер регистра вывода
        self.adjust_entry_font_size()

    def get_entry_text_width(self) -> int:
        return self.EnterReg.fontMetrics().boundingRect(self.EnterReg.text()).width()

    def get_temp_text_width(self) -> int:
        return self.MemoryReg.fontMetrics().boundingRect(
            self.MemoryReg.text()).width()

    def adjust_entry_font_size(self):
        font_size = self.default_entry_font_size

        while self.get_entry_text_width() > self.EnterReg.width() - 15:
            font_size -= 1
            self.EnterReg.setStyleSheet('font-size: ' + str(font_size) + 'pt; border: none;')

        font_size = 1
        while self.get_entry_text_width() < self.EnterReg.width() - 60:
            font_size += 1

            if font_size > self.default_entry_font_size:
                break

            self.EnterReg.setStyleSheet('font-size: ' + str(font_size) + 'pt; border: none;')

    def discard_zero_fractional_part(self):
        if self.result - int(self.result) == 0:
            self.result = int(self.result)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Calculator()
    window.show()

    sys.exit(app.exec_())