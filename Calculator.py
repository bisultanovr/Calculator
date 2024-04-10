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

        # Ввод операнда. Перед вводом очередного операнда (True) выполняем clear_entry
        self.enter_state = True
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
        # Ввод operand
        if self.expression_evaluated:
            self.clear_all()
        self.expression_evaluated = False

        if self.enter_state:
            self.EnterReg.clear()
            self.result = 0
        self.enter_state = False

        if self.int_part:
            self.result = self.result * 10 + int(num)
        else:
            self.fractional_part += 1
            self.result = self.result + num / 10 ** self.fractional_part
            self.result = int(self.result * 10 ** self.fractional_part) / 10 ** self.fractional_part

        current_text = self.EnterReg.text()
        new_text = current_text + str(num)
        self.EnterReg.setText(new_text)

    def on_btn_clicked_backspace(self):
        erasable_char = None

        if not self.enter_state:        # Если пытаемся стереть уже полученный результат, то clear_all
            if not self.int_part:       # Стираем из дробной части
                erasable_char = self.result * 10 ** self.fractional_part % 10
                self.result = self.result - erasable_char / 10 ** self.fractional_part

                self.fractional_part -= 1
                if self.fractional_part == 0:
                    self.int_part = True
                    self.result = int(self.result)

                # Если дробная часть нулевая, она отбрасывается
                self.discard_zero_fractional_part()

                self.EnterReg.setText(str(self.result))
            else:                       # Стираем из целой части
                erasable_char = self.result % 10
                self.result = (self.result - erasable_char) // 10
                self.EnterReg.setText(str(self.result))

                if self.result == 0:
                    self.clear_entry()
        else:
            self.clear_all()

    def on_btn_clicked_operation(self, operator):
        self.operator = operator

        self.enter_state = True
        self.expression_evaluated = False

        # Следующее вводимое число будет целым
        self.int_part = True
        self.fractional_part = 1

        # Если дробная часть нулевая, она отбрасывается
        self.discard_zero_fractional_part()

        self.operand1 = self.result
        # Выполняем операцию, если введён второй операнд
        if not self.enter_state:
            if operator is self.add_char:
                self.result = self.operand1 + self.operand2
            elif operator is self.sub_char:
                self.result = self.operand1 - self.operand2
            elif operator is self.multiply_char:
                self.result = self.operand1 * self.operand2
            elif operator is self.divide_char:
                self.result = self.operand1 / self.operand2

        # Если дробная часть нулевая, она отбрасывается
        self.discard_zero_fractional_part()

        self.operand2 = 0

        self.MemoryReg.setText(f"{self.operand1} {self.operator}")
        self.EnterReg.setText(str(self.result))

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
            self.operator = None
        else:
            self.MemoryReg.setText(f"{self.operand1} = ")
            self.EnterReg.setText(str(self.result))

        self.operand1 = self.result
        self.operand2 = 0

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

            if self.input_operand:
                self.expression[0] += '.'
            else:
                self.expression[2] += '.'

    def on_btn_clicked_switch_sign(self):
        self.result = -self.result
        self.EnterReg.setText(str(self.result))

    def clear_entry(self):
        self.enter_state = True
        self.int_part = True
        self.EnterReg.setText("0")
        self.operand2 = 0
        self.result = 0

    def clear_all(self):
        self.enter_state = True
        self.int_part = True
        self.EnterReg.setText("0")
        self.MemoryReg.clear()
        self.operand1 = 0
        self.operand2 = 0
        self.result = 0

    def discard_zero_fractional_part(self):
        if self.result - int(self.result) == 0:
            self.result = int(self.result)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Calculator()
    window.show()

    sys.exit(app.exec_())