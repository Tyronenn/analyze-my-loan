from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QSlider, QLabel, QWidget, QTableWidget, QTableWidgetItem, QLineEdit, QHBoxLayout, QCheckBox, QDockWidget, QDialog, QComboBox, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QIcon
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
class MoneyAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Money Analyzer")

        # Set the window icon
        self.setWindowIcon(QIcon(r"C:\Users\Snail\Python\analyze-my-loan\money-analysis.png"))

        # Create Graph widget
        self.graph_widget = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_widget)

        # Create Amortization widget
        self.amortization_widget = QWidget()
        self.amortization_layout = QVBoxLayout(self.amortization_widget)

        # Create dock widgets
        self.graph_dock = QDockWidget("Loan Analyzer", self)
        self.graph_dock.setWidget(self.graph_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.graph_dock)

        self.amortization_dock = QDockWidget("Amortization Table", self)
        self.amortization_dock.setWidget(self.amortization_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.amortization_dock)

        # Allow nested docks
        self.setDockNestingEnabled(True)

        # Apply custom styles to make boundaries more visible
        self.apply_custom_styles()

        # Instead, set the central widget to None
        self.setCentralWidget(None)

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
        self.graph_layout.addWidget(self.horizontal_grid_checkbox)
        self.graph_layout.addWidget(self.vertical_grid_checkbox)

        # Summary Label
        self.summary_label = QLabel("")
        self.graph_layout.addWidget(self.summary_label)

        # Matplotlib Figure and Canvas
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        self.graph_layout.addWidget(self.canvas)

        # Amortization Table
        self.amortization_table = QTableWidget()
        self.amortization_layout.addWidget(self.amortization_table)

        # Connect the header click signal to the new method
        self.amortization_table.horizontalHeader().sectionClicked.connect(self.show_attribute_editor)

        # Initial graph and summary update
        self.update_graph_and_summary()

    def create_slider_with_input(self, min_value, max_value, default_value, label, scale_factor=1):
        """Create a slider with an input field beside it, in a horizontal layout."""
        layout = QHBoxLayout()
        self.graph_layout.addWidget(QLabel(label))
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(default_value)

        input_field = QLineEdit()
        input_field.setText(str(default_value / scale_factor))
        input_field.setFixedWidth(80)  # Make the input field a reasonable size

        layout.addWidget(slider)
        layout.addWidget(input_field)
        self.graph_layout.addLayout(layout)

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

        # Store the data types for each column
        self.column_data_types = {
            0: int,  # Month
            1: float,  # Monthly Payment
            2: float,  # Principal
            3: float,  # Interest
        }

    def show_attribute_editor(self, column):
        header_item = self.amortization_table.horizontalHeaderItem(column)
        if header_item:
            attribute_name = header_item.text()
            current_data_type = self.column_data_types[column].__name__
            editor = AttributeEditor(attribute_name, current_data_type, self)
            if editor.exec() == QDialog.DialogCode.Accepted:
                new_data_type = editor.get_selected_data_type()
                self.update_column_data_type(column, new_data_type)

    def update_column_data_type(self, column, new_data_type):
        type_conversion = {
            'int': int,
            'float': float,
            'str': str,
            'hex': hex,
            'bin': bin
        }
        
        self.column_data_types[column] = type_conversion[new_data_type]
        
        # Update the column with the new data type
        for row in range(self.amortization_table.rowCount()):
            item = self.amortization_table.item(row, column)
            if item:
                value = item.text()
                try:
                    if new_data_type == 'hex':
                        new_value = hex(int(float(value)))
                    elif new_data_type == 'bin':
                        new_value = bin(int(float(value)))
                    else:
                        new_value = type_conversion[new_data_type](float(value))
                    self.amortization_table.setItem(row, column, QTableWidgetItem(str(new_value)))
                except ValueError:
                    pass  # If conversion fails, leave the cell as is

    def apply_custom_styles(self):
        # Set a stylesheet for QDockWidget
        dock_style = """
        QDockWidget {
            border: 1px solid #999999;
        }
        QDockWidget::title {
            background: #cccccc;
            padding-left: 5px;
        }
        """
        self.setStyleSheet(dock_style)

class AttributeEditor(QDialog):
    def __init__(self, attribute_name, current_data_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit {attribute_name}")
        self.setModal(True)

        layout = QVBoxLayout()

        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(['int', 'float', 'str', 'hex', 'bin'])
        self.data_type_combo.setCurrentText(current_data_type)

        layout.addWidget(QLabel(f"Attribute: {attribute_name}"))
        layout.addWidget(QLabel(f"Current Data Type: {current_data_type}"))
        layout.addWidget(QLabel("Select new data type:"))
        layout.addWidget(self.data_type_combo)

        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def get_selected_data_type(self):
        return self.data_type_combo.currentText()

# Main function to run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set the application name
    app.setApplicationName("Money Analyzer")
    
    # Optionally, set the organization name (useful for settings)
    app.setOrganizationName("Money Analyzer")
    
    window = MoneyAnalyzer()
    window.show()
    sys.exit(app.exec())