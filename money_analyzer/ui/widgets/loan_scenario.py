from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from ...controllers.loan_controller import LoanController
from ...config import *  # Import all constants from config.py
from ...utils.data_visualization import DataSource

class LoanScenario(DataSource, QWidget):
    loan_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.name = f"Loan {id(self)}"  # Unique name for each scenario
        self.controller = LoanController()
        self.setup_ui()
        self.connect_signals()
        self._updating = False

    def setup_ui(self):
        self.layout = QVBoxLayout(self)  # Change this line
        self.loan_amount_container, self.loan_amount_slider, _ = self.create_slider_with_input(
            LOAN_AMOUNT_MIN, LOAN_AMOUNT_MAX, LOAN_AMOUNT_DEFAULT, "Loan Amount ($):", name="loan_amount_slider"
        )
        self.down_payment_container, self.down_payment_slider, _ = self.create_slider_with_input(
            DOWN_PAYMENT_MIN, DOWN_PAYMENT_MAX, DOWN_PAYMENT_DEFAULT, "Down Payment ($):", name="down_payment_slider"
        )
        self.interest_rate_container, self.interest_rate_slider, _ = self.create_slider_with_input(
            INTEREST_RATE_MIN, INTEREST_RATE_MAX, INTEREST_RATE_DEFAULT, "Interest Rate (%):", 
            scale_factor=INTEREST_RATE_SCALE_FACTOR, name="interest_rate_slider"
        )
        self.loan_term_container, self.loan_term_slider, _ = self.create_slider_with_input(
            LOAN_TERM_MIN, LOAN_TERM_MAX, LOAN_TERM_DEFAULT, "Loan Term (Years):", name="loan_term_slider"
        )
        self.extra_payment_container, self.extra_payment_slider, _ = self.create_slider_with_input(
            EXTRA_PAYMENT_MIN, EXTRA_PAYMENT_MAX, EXTRA_PAYMENT_DEFAULT, "Extra Monthly Payment ($):", name="extra_payment_slider"
        )

        self.layout.addWidget(self.loan_amount_container)
        self.layout.addWidget(self.down_payment_container)
        self.layout.addWidget(self.interest_rate_container)
        self.layout.addWidget(self.loan_term_container)
        self.layout.addWidget(self.extra_payment_container)

    def create_slider_with_input(self, min_value, max_value, default_value, label, scale_factor=1, name=None):
        container = QWidget()
        layout = QHBoxLayout(container)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(default_value)
        if name:
            slider.setObjectName(name)

        input_field = QLineEdit()
        input_field.setText(str(default_value / scale_factor))
        input_field.setFixedWidth(80)

        layout.addWidget(QLabel(label))
        layout.addWidget(slider)
        layout.addWidget(input_field)
        
        return container, slider, input_field

    def connect_signals(self):
        self.loan_amount_slider.valueChanged.connect(lambda: self.update_loan(True))
        self.down_payment_slider.valueChanged.connect(lambda: self.update_loan(True))
        self.interest_rate_slider.valueChanged.connect(lambda: self.update_loan(True))
        self.loan_term_slider.valueChanged.connect(lambda: self.update_loan(True))
        self.extra_payment_slider.valueChanged.connect(lambda: self.update_loan(True))

    def update_loan(self, emit_signal=True):
        if self._updating:
            return
        self._updating = True

        loan_amount = self.loan_amount_slider.value()
        down_payment = self.down_payment_slider.value()
        interest_rate = self.interest_rate_slider.value() / 10
        loan_term = self.loan_term_slider.value()
        extra_payment = self.extra_payment_slider.value()

        self.controller.create_loan(loan_amount, interest_rate, loan_term, down_payment, extra_payment)
        
        self._updating = False
        if emit_signal:
            self.loan_updated.emit()

    def get_amortization_data(self):
        return self.controller.get_amortization_data()

    def get_loan_summary(self):
        return self.controller.get_loan_summary()

    def get_data(self):
        amortization_data = self.get_amortization_data()
        return {
            'x': amortization_data['months'],
            'y': amortization_data['principal_payments']
        }

    def get_name(self):
        return f"{self.name} - Principal"

    def get_title(self):
        return "Loan Amortization"

    def get_x_label(self):
        return "Months"

    def get_y_label(self):
        return "Amount ($)"

    def get_data_for_param(self, param_name):
        amortization_data = self.get_amortization_data()
        months = amortization_data['months']
        
        if param_name == 'Principal Balance':
            return months, amortization_data['remaining_balance']
        elif param_name == 'Monthly Payment':
            return months, [self.controller.loan.monthly_payment] * len(months)
        elif param_name == 'Cumulative Interest':
            return months, amortization_data['cumulative_interest']
        elif param_name == 'Interest Rate':
            return months, [self.controller.loan.interest_rate] * len(months)
        else:
            raise ValueError(f"Unknown parameter: {param_name}")