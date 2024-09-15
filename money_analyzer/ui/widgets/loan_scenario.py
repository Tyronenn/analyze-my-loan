from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt
from ...controllers.loan_controller import LoanController

class LoanScenario(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = LoanController()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.loan_amount_container, self.loan_amount_slider, _ = self.create_slider_with_input(1000, 1000000, 250000, "Loan Amount ($):", name="loan_amount_slider")
        self.down_payment_container, self.down_payment_slider, _ = self.create_slider_with_input(0, 500000, 50000, "Down Payment ($):", name="down_payment_slider")
        self.interest_rate_container, self.interest_rate_slider, _ = self.create_slider_with_input(5, 150, 50, "Interest Rate (%):", scale_factor=10, name="interest_rate_slider")
        self.loan_term_container, self.loan_term_slider, _ = self.create_slider_with_input(1, 30, 30, "Loan Term (Years):", name="loan_term_slider")
        self.extra_payment_container, self.extra_payment_slider, _ = self.create_slider_with_input(0, 10000, 0, "Extra Monthly Payment ($):", name="extra_payment_slider")

        layout.addWidget(self.loan_amount_container)
        layout.addWidget(self.down_payment_container)
        layout.addWidget(self.interest_rate_container)
        layout.addWidget(self.loan_term_container)
        layout.addWidget(self.extra_payment_container)

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

    def update_loan(self):
        loan_amount = self.loan_amount_slider.value()
        down_payment = self.down_payment_slider.value()
        interest_rate = self.interest_rate_slider.value() / 10
        loan_term = self.loan_term_slider.value()
        extra_payment = self.extra_payment_slider.value()

        self.controller.create_loan(loan_amount, interest_rate, loan_term, down_payment, extra_payment)

    def get_amortization_data(self):
        return self.controller.get_amortization_data()

    def get_loan_summary(self):
        return self.controller.get_loan_summary()