from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QFileDialog, QMessageBox, QTabWidget, QInputDialog, QMenu, QTabBar, QToolButton, QMainWindow, QListWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon
import csv
import json
from ...controllers.loan_controller import LoanController
from functools import partial
from .loan_scenario import LoanScenario
from .graph_widget import GraphWidget

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

class LoanWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loan_scenarios = []
        self.graphs = []
        self.setup_ui()
        self.add_loan_scenario()
        self.add_plus_tab()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.init_tab_widget()
        self.init_checkboxes()
        self.init_export_button()
        self.init_summary_label()
        self.init_graph_controls()
        self.init_save_load_buttons()

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

    def init_graph_controls(self):
        graph_controls_layout = QHBoxLayout()
        
        self.add_graph_button = QPushButton("Add Graph")
        self.add_graph_button.clicked.connect(self.add_graph)
        graph_controls_layout.addWidget(self.add_graph_button)
        
        self.graph_list = QListWidget()
        self.graph_list.itemSelectionChanged.connect(self.update_selected_graph)
        graph_controls_layout.addWidget(self.graph_list)
        
        self.layout.addLayout(graph_controls_layout)

    def init_save_load_buttons(self):
        save_button = QPushButton("Save Scenarios")
        load_button = QPushButton("Load Scenarios")
        save_button.clicked.connect(self.save_scenarios)
        load_button.clicked.connect(self.load_scenarios)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(load_button)
        self.layout.addLayout(button_layout)

    def add_loan_scenario(self):
        scenario = LoanScenario()
        self.loan_scenarios.append(scenario)
        self.tab_widget.insertTab(self.tab_widget.count() - 1, scenario, f"Loan {len(self.loan_scenarios)}")
        scenario.loan_amount_slider.valueChanged.connect(self.update_loan)
        scenario.down_payment_slider.valueChanged.connect(self.update_loan)
        scenario.interest_rate_slider.valueChanged.connect(self.update_loan)
        scenario.loan_term_slider.valueChanged.connect(self.update_loan)
        scenario.extra_payment_slider.valueChanged.connect(self.update_loan)
        
        # Connect the include_in_graph checkbox
        scenario.include_in_graph.stateChanged.connect(self.update_loan)
        
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
            current_name = self.tab_widget.tabText(index)
            new_name, ok = QInputDialog.getText(self, "Rename Tab", "Enter new name:", text=current_name)
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
        self.update_all_graphs()

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

    def add_graph(self):
        graph_title, ok = QInputDialog.getText(self, "New Graph", "Enter graph title:")
        if ok and graph_title:
            new_graph = GraphWidget(self, graph_title)
            self.graphs.append(new_graph)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, new_graph)
            self.graph_list.addItem(graph_title)

    def update_selected_graph(self):
        selected_items = self.graph_list.selectedItems()
        if selected_items:
            selected_graph = self.graphs[self.graph_list.row(selected_items[0])]
            selected_graph.update_graph(
                [scenario for scenario in self.loan_scenarios if scenario.include_in_graph],
                self.horizontal_grid_checkbox.isChecked(),
                self.vertical_grid_checkbox.isChecked()
            )

    def update_all_graphs(self):
        for graph in self.graphs:
            graph.update_graph(
                [scenario for scenario in self.loan_scenarios if scenario.include_in_graph],
                self.horizontal_grid_checkbox.isChecked(),
                self.vertical_grid_checkbox.isChecked()
            )

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            amortization_data = self.loan_scenarios[0].get_amortization_data()
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Month", "Monthly Payment", "Principal", "Interest"])
                for month, principal, interest in zip(amortization_data['months'], amortization_data['principal_payments'], amortization_data['interest_payments']):
                    writer.writerow([month, principal + interest, principal, interest])

    def save_scenarios(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Loan Scenarios", "", "JSON Files (*.json)")
        if file_path:
            scenarios_data = []
            for scenario in self.loan_scenarios:
                scenario_data = {
                    "loan_amount": scenario.loan_amount_slider.value(),
                    "down_payment": scenario.down_payment_slider.value(),
                    "interest_rate": scenario.interest_rate_slider.value(),
                    "loan_term": scenario.loan_term_slider.value(),
                    "extra_payment": scenario.extra_payment_slider.value(),
                }
                scenarios_data.append(scenario_data)
            
            with open(file_path, 'w') as f:
                json.dump(scenarios_data, f)
            QMessageBox.information(self, "Save Successful", "Loan scenarios saved successfully.")

    def load_scenarios(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Loan Scenarios", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'r') as f:
                scenarios_data = json.load(f)
            
            # Clear existing scenarios
            for i in range(self.tab_widget.count() - 1, 0, -1):  # Leave the '+' tab
                self.remove_tab(i)
            
            # Load saved scenarios
            for scenario_data in scenarios_data:
                self.add_loan_scenario()
                scenario = self.loan_scenarios[-1]
                scenario.loan_amount_slider.setValue(scenario_data["loan_amount"])
                scenario.down_payment_slider.setValue(scenario_data["down_payment"])
                scenario.interest_rate_slider.setValue(scenario_data["interest_rate"])
                scenario.loan_term_slider.setValue(scenario_data["loan_term"])
                scenario.extra_payment_slider.setValue(scenario_data["extra_payment"])
                scenario.update_loan()
            
            self.update_loan()
            QMessageBox.information(self, "Load Successful", "Loan scenarios loaded successfully.")