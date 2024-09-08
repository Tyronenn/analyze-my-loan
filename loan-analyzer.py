from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QSlider, QLabel, QWidget, QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit, QHBoxLayout, QCheckBox)
from PyQt6.QtCore import Qt
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


# Function to calculate loan payment details
def calculate_loan_details(loan_amount, down_payment, annual_rate, years, extra_payment):
    principal = loan_amount - down_payment
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    monthly_payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -num_payments) if monthly_rate != 0 else principal / num_payments

    interest_payment = []
    principal_payment = []
    remaining_balance = principal

    for _ in range(num_payments):
        interest = remaining_balance * monthly_rate
        principal_paid = monthly_payment - interest + extra_payment
        if remaining_balance - principal_paid < 0:  # If the loan is paid off
            principal_paid = remaining_balance
            interest = remaining_balance * monthly_rate
            monthly_payment = principal_paid + interest

        remaining_balance -= principal_paid

        interest_payment.append(interest)
        principal_payment.append(principal_paid)

        if remaining_balance <= 0:  # Break early if the loan is paid off
            break

    return monthly_payment, np.array(principal_payment), np.array(interest_payment)


# The main application window class
class LoanCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loan Calculator with PyQt")

        # Create a tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tabs
        self.main_widget = QWidget()
        self.amortization_widget = QWidget()

        self.tabs.addTab(self.main_widget, "Graph")
        self.tabs.addTab(self.amortization_widget, "Amortization Table")

        # --- Main Widget Setup (Graph Tab) ---
        self.layout = QVBoxLayout(self.main_widget)

        # Loan Amount Slider + Input Field
        self.loan_amount_slider, self.loan_amount_input = self.create_slider_with_input(1000, 1000000, 250000, "Loan Amount ($):")
        self.loan_amount_slider.valueChanged.connect(self.update_graph_and_summary)
        self.loan_amount_input.textChanged.connect(lambda value: self.update_slider_from_input(self.loan_amount_slider, value))

        # Down Payment Slider + Input Field
        self.down_payment_slider, self.down_payment_input = self.create_slider_with_input(0, 500000, 50000, "Down Payment ($):")
        self.down_payment_slider.valueChanged.connect(self.update_graph_and_summary)
        self.down_payment_input.textChanged.connect(lambda value: self.update_slider_from_input(self.down_payment_slider, value))

        # Interest Rate Slider + Input Field
        self.interest_rate_slider, self.interest_rate_input = self.create_slider_with_input(5, 150, 50, "Interest Rate (%):", scale_factor=10)
        self.interest_rate_slider.valueChanged.connect(self.update_graph_and_summary)
        self.interest_rate_input.textChanged.connect(lambda value: self.update_slider_from_input(self.interest_rate_slider, value, scale_factor=10))

        # Loan Term Slider + Input Field
        self.loan_term_slider, self.loan_term_input = self.create_slider_with_input(1, 30, 30, "Loan Term (Years):")
        self.loan_term_slider.valueChanged.connect(self.update_graph_and_summary)
        self.loan_term_input.textChanged.connect(lambda value: self.update_slider_from_input(self.loan_term_slider, value))

        # Extra Payment Slider + Input Field
        self.extra_payment_slider, self.extra_payment_input = self.create_slider_with_input(0, 10000, 0, "Extra Monthly Payment ($):")
        self.extra_payment_slider.valueChanged.connect(self.update_graph_and_summary)
        self.extra_payment_input.textChanged.connect(lambda value: self.update_slider_from_input(self.extra_payment_slider, value))
        
        # Add checkboxes to toggle grid lines
        self.horizontal_grid_checkbox = QCheckBox("Show Horizontal Grid Lines")
        self.horizontal_grid_checkbox.setChecked(True)
        self.horizontal_grid_checkbox.stateChanged.connect(self.update_graph_and_summary)

        self.vertical_grid_checkbox = QCheckBox("Show Vertical Grid Lines")
        self.vertical_grid_checkbox.setChecked(True)
        self.vertical_grid_checkbox.stateChanged.connect(self.update_graph_and_summary)

        # Add the checkboxes to the layout
        self.layout.addWidget(self.horizontal_grid_checkbox)
        self.layout.addWidget(self.vertical_grid_checkbox)

        # Summary Label
        self.summary_label = QLabel("")
        self.layout.addWidget(self.summary_label)

        # Matplotlib Figure and Canvas
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        # --- Amortization Table Setup (Second Tab) ---
        self.amortization_layout = QVBoxLayout(self.amortization_widget)
        self.amortization_table = QTableWidget()
        self.amortization_layout.addWidget(self.amortization_table)

        # Initial graph and summary update
        self.update_graph_and_summary()

    def create_slider_with_input(self, min_value, max_value, default_value, label, scale_factor=1):
        """Create a slider with an input field beside it, in a horizontal layout."""
        layout = QHBoxLayout()
        self.layout.addWidget(QLabel(label))
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(default_value)

        input_field = QLineEdit()
        input_field.setText(str(default_value / scale_factor))
        input_field.setFixedWidth(80)  # Make the input field a reasonable size

        layout.addWidget(slider)
        layout.addWidget(input_field)
        self.layout.addLayout(layout)

        return slider, input_field

    def update_slider_from_input(self, slider, value, scale_factor=1):
        """Update slider value based on input field value."""
        try:
            slider.setValue(int(float(value) * scale_factor))
        except ValueError:
            pass  # Ignore invalid input

    def update_graph_and_summary(self):
        loan_amount = self.loan_amount_slider.value()
        down_payment = self.down_payment_slider.value()
        interest_rate = self.interest_rate_slider.value() / 10  # Convert to decimal interest rate
        loan_term = self.loan_term_slider.value()

        # Update the input fields to match the slider values
        self.loan_amount_input.setText(f"{loan_amount}")
        self.down_payment_input.setText(f"{down_payment}")
        self.interest_rate_input.setText(f"{interest_rate:.1f}")
        self.loan_term_input.setText(f"{loan_term}")

        extra_payment = self.extra_payment_slider.value()
        
        # Update the extra payment input field based on the slider value
        self.extra_payment_input.setText(f"{extra_payment}")

        # Call the loan calculation function
        monthly_payment, principal_payment, interest_payment = calculate_loan_details(
            loan_amount, down_payment, interest_rate, loan_term, extra_payment
        )

        # Update the graph
        self.ax.clear()
        self.ax.plot(np.cumsum(principal_payment), label="Principal Paid")
        self.ax.plot(np.cumsum(interest_payment), label="Interest Paid")
        self.ax.set_title("Loan Repayment Breakdown")
        self.ax.set_xlabel("Month")
        self.ax.set_ylabel("Amount Paid")

        # Move the legend outside the plot, below the graph
        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

        # Add grid lines based on user preferences
        self.ax.grid(
            self.horizontal_grid_checkbox.isChecked(),
            axis='y',  # Horizontal grid lines
        )
        self.ax.grid(
            self.vertical_grid_checkbox.isChecked(),
            axis='x',  # Vertical grid lines
        )

        # Use tight_layout to prevent label cutoff
        self.fig.tight_layout()

        self.canvas.draw()

        # Update the summary text
        total_interest_paid = np.sum(interest_payment)
        apr = interest_rate
        self.summary_label.setText(
            f"Loan Amount: ${loan_amount:,.2f}\n"
            f"APR: {apr:.2f}%\n"
            f"Monthly Payment: ${monthly_payment:,.2f}\n"
            f"Loan Term (years): {loan_term:.1f}\n"
            f"Total Interest Paid: ${total_interest_paid:,.2f}"
        )

        # Update the amortization table
        self.update_amortization_table(monthly_payment, principal_payment, interest_payment)

    def update_amortization_table(self, monthly_payment, principal_payment, interest_payment):
        num_payments = len(principal_payment)
        self.amortization_table.setRowCount(num_payments)
        self.amortization_table.setColumnCount(4)
        self.amortization_table.setHorizontalHeaderLabels(["Month", "Monthly Payment", "Principal", "Interest"])

        for i in range(num_payments):
            self.amortization_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.amortization_table.setItem(i, 1, QTableWidgetItem(f"${monthly_payment:.2f}"))
            self.amortization_table.setItem(i, 2, QTableWidgetItem(f"${principal_payment[i]:.2f}"))
            self.amortization_table.setItem(i, 3, QTableWidgetItem(f"${interest_payment[i]:.2f}"))

        self.amortization_table.resizeColumnsToContents()


# Main function to run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoanCalculator()
    window.show()
    sys.exit(app.exec())