from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel, QLineEdit, QHBoxLayout, QCheckBox, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import csv
from ...controllers.loan_controller import LoanController

class LoanWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.loan_controller = LoanController()
        self.setup_ui()

    def setup_ui(self):
        self.loan_amount_slider, self.loan_amount_input = self.create_slider_with_input(1000, 1000000, 250000, "Loan Amount ($):")
        self.down_payment_slider, self.down_payment_input = self.create_slider_with_input(0, 500000, 50000, "Down Payment ($):")
        self.interest_rate_slider, self.interest_rate_input = self.create_slider_with_input(5, 150, 50, "Interest Rate (%):", scale_factor=10)
        self.loan_term_slider, self.loan_term_input = self.create_slider_with_input(1, 30, 30, "Loan Term (Years):")
        self.extra_payment_slider, self.extra_payment_input = self.create_slider_with_input(0, 10000, 0, "Extra Monthly Payment ($):")

        self.horizontal_grid_checkbox = QCheckBox("Show Horizontal Grid Lines")
        self.vertical_grid_checkbox = QCheckBox("Show Vertical Grid Lines")
        self.layout.addWidget(self.horizontal_grid_checkbox)
        self.layout.addWidget(self.vertical_grid_checkbox)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        self.layout.addWidget(self.export_button)

        self.summary_label = QLabel("")
        self.layout.addWidget(self.summary_label)

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        # Connect signals
        self.loan_amount_slider.valueChanged.connect(self.update_loan)
        self.down_payment_slider.valueChanged.connect(self.update_loan)
        self.interest_rate_slider.valueChanged.connect(self.update_loan)
        self.loan_term_slider.valueChanged.connect(self.update_loan)
        self.extra_payment_slider.valueChanged.connect(self.update_loan)
        self.horizontal_grid_checkbox.stateChanged.connect(self.update_graph)
        self.vertical_grid_checkbox.stateChanged.connect(self.update_graph)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

        # Initial update
        self.update_loan()

    def create_slider_with_input(self, min_value, max_value, default_value, label, scale_factor=1):
        container = QWidget()
        layout = QHBoxLayout(container)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(default_value)

        input_field = QLineEdit()
        input_field.setText(str(default_value / scale_factor))
        input_field.setFixedWidth(80)  # Make the input field a reasonable size

        layout.addWidget(QLabel(label))
        layout.addWidget(slider)
        layout.addWidget(input_field)
        
        self.layout.addWidget(container)

        return slider, input_field

    def update_loan(self):
        loan_amount = self.loan_amount_slider.value()
        down_payment = self.down_payment_slider.value()
        interest_rate = self.interest_rate_slider.value() / 10
        loan_term = self.loan_term_slider.value()
        extra_payment = self.extra_payment_slider.value()

        self.loan_controller.create_loan(loan_amount, interest_rate, loan_term, down_payment, extra_payment)
        self.update_summary()
        self.update_graph()

    def update_summary(self):
        summary = self.loan_controller.get_loan_summary()
        self.summary_label.setText(
            f"Loan Amount: ${summary['loan_amount']:,.2f}\n"
            f"APR: {self.loan_controller.loan.interest_rate:.2f}%\n"
            f"Monthly Payment: ${summary['monthly_payment']:,.2f}\n"
            f"Loan Term (years): {summary['loan_term']:.1f}\n"
            f"Total Interest Paid: ${summary['total_interest']:,.2f}"
        )

    def update_graph(self):
        amortization_data = self.loan_controller.get_amortization_data()
        
        self.ax.clear()
        self.ax.plot(amortization_data['months'], amortization_data['principal_payments'], label="Principal Paid")
        self.ax.plot(amortization_data['months'], amortization_data['interest_payments'], label="Interest Paid")
        self.ax.set_title("Loan Repayment Breakdown")
        self.ax.set_xlabel("Month")
        self.ax.set_ylabel("Amount Paid")

        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

        self.ax.grid(
            self.horizontal_grid_checkbox.isChecked(),
            axis='y',
        )
        self.ax.grid(
            self.vertical_grid_checkbox.isChecked(),
            axis='x',
        )

        self.fig.tight_layout()
        self.canvas.draw()

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            amortization_data = self.loan_controller.get_amortization_data()
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Month", "Monthly Payment", "Principal", "Interest"])
                for month, principal, interest in zip(amortization_data['months'], amortization_data['principal_payments'], amortization_data['interest_payments']):
                    writer.writerow([month, principal + interest, principal, interest])

    def on_hover(self, event):
        if event.inaxes == self.ax:
            # Display information based on hover location
            month = int(event.xdata)
            if 0 <= month < len(self.loan_controller.get_amortization_data()['months']):
                principal = self.loan_controller.get_amortization_data()['principal_payments'][month]
                interest = self.loan_controller.get_amortization_data()['interest_payments'][month]
                self.ax.set_title(f"Month: {month}, Principal: ${principal:,.2f}, Interest: ${interest:,.2f}")
                self.canvas.draw()