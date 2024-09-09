from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QSlider, QLabel, QWidget, QTableWidget, QTableWidgetItem, QLineEdit, QHBoxLayout, QCheckBox, QDockWidget, QDialog, QComboBox, QPushButton, QListWidget)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QPalette, QColor, QIcon, QDrag
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

class DraggableWidget(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)
        self.title_label = QLabel(title)
        self.layout.addWidget(self.title_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.title_label.text())
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        pos = event.position()
        dropped_widget = event.source()
        if dropped_widget != self:
            self.layout.addWidget(dropped_widget)
            event.acceptProposedAction()

class Graph(DraggableWidget):
    def __init__(self, title="Graph", parent=None):
        super().__init__(title, parent)
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)
        self.parameters = []

    def dropEvent(self, event):
        super().dropEvent(event)
        parameter = event.mimeData().text()
        if parameter not in self.parameters:
            self.parameters.append(parameter)
            self.update_graph()

    def update_graph(self):
        self.ax.clear()
        # Here you would get the actual data for the parameters
        # For now, we'll just plot some dummy data
        for param in self.parameters:
            self.ax.plot(range(10), np.random.rand(10), label=param)
        self.ax.legend()
        self.canvas.draw()

class MoneyAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Money Analyzer")
        self.setWindowIcon(QIcon(r"C:\Users\Snail\Python\analyze-my-loan\money-analysis.png"))

        # Create central widget and layout
        self.central_widget = QWidget()
        self.central_layout = QHBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Create left panel for controls
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.central_layout.addWidget(self.left_panel)

        # Create right panel for graphs and other widgets
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.central_layout.addWidget(self.right_panel)

        # Add graph button
        self.add_graph_button = QPushButton("Add Graph")
        self.add_graph_button.clicked.connect(self.add_graph)
        self.left_layout.addWidget(self.add_graph_button)

        # Create draggable parameters
        self.create_draggable_parameters()

        # Create sliders and inputs
        self.create_sliders_and_inputs()

        # Amortization Table
        self.amortization_table = QTableWidget()
        self.amortization_widget = DraggableWidget("Amortization Table")
        self.amortization_widget.layout.addWidget(self.amortization_table)
        self.right_layout.addWidget(self.amortization_widget)

        # Connect the header click signal to the new method
        self.amortization_table.horizontalHeader().sectionClicked.connect(self.show_attribute_editor)

        # Initial update
        self.update_data()

    def create_draggable_parameters(self):
        parameters = ["Loan Amount", "Down Payment", "Interest Rate", "Loan Term", "Extra Payment"]
        for param in parameters:
            label = DraggableWidget(param)
            self.left_layout.addWidget(label)

    def create_sliders_and_inputs(self):
        # Create sliders and inputs similar to before, but wrap them in DraggableWidget
        loan_amount_widget = DraggableWidget("Loan Amount")
        self.loan_amount_slider, self.loan_amount_input, container = self.create_slider_with_input(1000, 1000000, 250000, "Loan Amount ($):")
        loan_amount_widget.layout.addWidget(container)
        self.right_layout.addWidget(loan_amount_widget)

        # Do the same for other sliders and inputs
        down_payment_widget = DraggableWidget("Down Payment")
        self.down_payment_slider, self.down_payment_input, container = self.create_slider_with_input(0, 500000, 50000, "Down Payment ($):")
        down_payment_widget.layout.addWidget(container)
        self.right_layout.addWidget(down_payment_widget)

        interest_rate_widget = DraggableWidget("Interest Rate")
        self.interest_rate_slider, self.interest_rate_input, container = self.create_slider_with_input(5, 150, 50, "Interest Rate (%):", scale_factor=10)
        interest_rate_widget.layout.addWidget(container)
        self.right_layout.addWidget(interest_rate_widget)

        loan_term_widget = DraggableWidget("Loan Term")
        self.loan_term_slider, self.loan_term_input, container = self.create_slider_with_input(1, 30, 30, "Loan Term (Years):")
        loan_term_widget.layout.addWidget(container)
        self.right_layout.addWidget(loan_term_widget)

        extra_payment_widget = DraggableWidget("Extra Payment")
        self.extra_payment_slider, self.extra_payment_input, container = self.create_slider_with_input(0, 10000, 0, "Extra Monthly Payment ($):")
        extra_payment_widget.layout.addWidget(container)
        self.right_layout.addWidget(extra_payment_widget)

    def create_slider_with_input(self, min_value, max_value, default_value, label, scale_factor=1):
        """Create a slider with an input field beside it, in a horizontal layout."""
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(default_value)

        input_field = QLineEdit()
        input_field.setText(str(default_value / scale_factor))
        input_field.setFixedWidth(80)  # Make the input field a reasonable size

        layout.addWidget(slider)
        layout.addWidget(input_field)

        container = QWidget()
        container.setLayout(layout)
        return slider, input_field, container

    def update_slider_from_input(self, slider, value, scale_factor=1):
        """Update slider value based on input field value."""
        try:
            slider.setValue(int(float(value) * scale_factor))
        except ValueError:
            pass  # Ignore invalid input

    def add_graph(self):
        graph = Graph()
        self.right_layout.addWidget(graph)

    def update_data(self):
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

        # Update all Graph widgets
        for i in range(self.right_layout.count()):
            widget = self.right_layout.itemAt(i).widget()
            if isinstance(widget, Graph):
                widget.update_graph()

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