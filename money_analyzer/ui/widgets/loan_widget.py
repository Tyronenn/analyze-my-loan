from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel, QLineEdit, QHBoxLayout, QCheckBox, QPushButton, QFileDialog, QMessageBox, QTabWidget, QInputDialog, QMenu, QTabBar, QToolButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import csv
from ...controllers.loan_controller import LoanController
from functools import partial
from .loan_scenario import LoanScenario

class CustomTabBar(QTabBar):
    def __init__(self, parent=None, loan_widget=None):
        super().__init__(parent)
        self.loan_widget = loan_widget
        self.setTabsClosable(False)  # Disable built-in close buttons

    def tabInserted(self, index):
        if index != self.count() - 1:  # Ensure the "+" tab does not get a close button
            self.add_close_button(index)

    def add_close_button(self, index):
        close_button = QToolButton(self)
        close_button.setText('x')  # Set the text to 'x'
        close_button.setFixedSize(16, 16)  # Set a fixed size for the button
        close_button.setStyleSheet("""
            QToolButton {
                border: none;
                border-radius: 8px;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
                qproperty-iconSize: 12px;
                text-align: center;
            }
            QToolButton:hover {
                background-color: lightgray;
            }
        """)  # Set the styles for normal and hover states
        close_button.clicked.connect(partial(self.loan_widget.remove_tab, index))
        self.setTabButton(index, QTabBar.ButtonPosition.RightSide, close_button)

class LoanWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.loan_scenarios = []
        self.setup_ui()
        self.add_loan_scenario()
        self.add_plus_tab()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.init_tab_widget()
        self.init_checkboxes()
        self.init_export_button()
        self.init_summary_label()
        self.init_matplotlib_canvas()

    def init_tab_widget(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(CustomTabBar(self.tab_widget, self))
        self.tab_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.tab_widget.tabBarDoubleClicked.connect(self.rename_tab)
        self.layout.addWidget(self.tab_widget)

    def init_checkboxes(self):
        self.horizontal_grid_checkbox = QCheckBox("Show Horizontal Grid Lines")
        self.vertical_grid_checkbox = QCheckBox("Show Vertical Grid Lines")
        self.layout.addWidget(self.horizontal_grid_checkbox)
        self.layout.addWidget(self.vertical_grid_checkbox)

    def init_export_button(self):
        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        self.layout.addWidget(self.export_button)

    def init_summary_label(self):
        self.summary_label = QLabel("")
        self.layout.addWidget(self.summary_label)

    def init_matplotlib_canvas(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def add_loan_scenario(self):
        scenario = LoanScenario()
        self.loan_scenarios.append(scenario)
        self.tab_widget.insertTab(self.tab_widget.count() - 1, scenario, f"Loan {len(self.loan_scenarios)}")
        scenario.loan_amount_slider.valueChanged.connect(self.update_loan)
        scenario.down_payment_slider.valueChanged.connect(self.update_loan)
        scenario.interest_rate_slider.valueChanged.connect(self.update_loan)
        scenario.loan_term_slider.valueChanged.connect(self.update_loan)
        scenario.extra_payment_slider.valueChanged.connect(self.update_loan)
        self.update_loan()

    def add_plus_tab(self):
        plus_tab = QWidget()
        self.tab_widget.addTab(plus_tab, "+")
        self.tab_widget.tabBarClicked.connect(self.handle_tab_click)

    def handle_tab_click(self, index):
        if index == self.tab_widget.count() - 1:  # If the "+" tab is clicked
            self.add_loan_scenario()
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 2)  # Switch to the new tab

    def remove_tab(self, index):
        if index != self.tab_widget.count() - 1:  # Ensure the "+" tab is not removed
            self.tab_widget.removeTab(index)
            if index < len(self.loan_scenarios):
                self.loan_scenarios.pop(index)
            self.update_loan()

    def rename_tab(self, index):
        if index != self.tab_widget.count() - 1:  # Ensure the "+" tab is not renamed
            new_name, ok = QInputDialog.getText(self, "Rename Tab", "Enter new name:")
            if ok and new_name:
                self.tab_widget.setTabText(index, new_name)

    def show_context_menu(self, position: QPoint):
        context_menu = QMenu(self)
        rename_action = context_menu.addAction("Rename Tab")
        remove_action = context_menu.addAction("Remove Tab")
        action = context_menu.exec(self.tab_widget.mapToGlobal(position))
        current_index = self.tab_widget.tabBar().tabAt(position)

        if action == rename_action:
            self.rename_tab(current_index)
        elif action == remove_action:
            self.remove_tab(current_index)

    def update_loan(self):
        for scenario in self.loan_scenarios:
            scenario.update_loan()
        self.update_summary()
        self.update_graph()

    def update_summary(self):
        summaries = [scenario.get_loan_summary() for scenario in self.loan_scenarios]
        summary_texts = [
            f"Loan {i+1}:\n"
            f"Loan Amount: ${summary['loan_amount']:,.2f}\n"
            f"APR: {scenario.controller.loan.interest_rate:.2f}%\n"
            f"Monthly Payment: ${summary['monthly_payment']:,.2f}\n"
            f"Loan Term (years): {summary['loan_term']:.1f}\n"
            f"Total Interest Paid: ${summary['total_interest']:,.2f}\n"
            for i, (scenario, summary) in enumerate(zip(self.loan_scenarios, summaries))
        ]
        self.summary_label.setText("\n\n".join(summary_texts))

    def update_graph(self):
        self.ax.clear()
        for i, scenario in enumerate(self.loan_scenarios):
            amortization_data = scenario.get_amortization_data()
            self.ax.plot(amortization_data['months'], amortization_data['principal_payments'], label=f"Principal Paid (Loan {i+1})")
            self.ax.plot(amortization_data['months'], amortization_data['interest_payments'], label=f"Interest Paid (Loan {i+1})")
        
        self.ax.set_title("Loan Repayment Breakdown")
        self.ax.set_xlabel("Month")
        self.ax.set_ylabel("Amount Paid")
        
        # Check if there are any labels before calling legend
        handles, labels = self.ax.get_legend_handles_labels()
        if labels:
            self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

        self.ax.grid(
            self.horizontal_grid_checkbox.isChecked(),
            axis='y',
        )
        self.ax.grid(
            self.vertical_grid_checkbox.isChecked(),
            axis='x',
        )

        # Use subplots_adjust instead of tight_layout
        self.fig.subplots_adjust(bottom=0.2, top=0.8)
        self.canvas.draw()

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            amortization_data = self.loan_scenarios[0].get_amortization_data()
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Month", "Monthly Payment", "Principal", "Interest"])
                for month, principal, interest in zip(amortization_data['months'], amortization_data['principal_payments'], amortization_data['interest_payments']):
                    writer.writerow([month, principal + interest, principal, interest])

    def on_hover(self, event):
        if event.inaxes == self.ax:
            # Display information based on hover location
            month = int(event.xdata)
            if 0 <= month < len(self.loan_scenarios[0].get_amortization_data()['months']):
                principal = self.loan_scenarios[0].get_amortization_data()['principal_payments'][month]
                interest = self.loan_scenarios[0].get_amortization_data()['interest_payments'][month]
                self.ax.set_title(f"Month: {month}, Principal: ${principal:,.2f}, Interest: ${interest:,.2f}")
                self.canvas.draw()