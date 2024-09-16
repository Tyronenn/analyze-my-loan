from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QDockWidget, QInputDialog, QListWidget, QPushButton, QVBoxLayout, QWidget, QCheckBox
from PyQt6.QtCore import Qt
from .widgets.loan_widget import LoanWidget
from .widgets.graph_widget import GraphWidget
from ..controllers.graph_manager import GraphManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Money Analyzer")
        self.setGeometry(100, 100, 1200, 800)

        self.graph_manager = GraphManager(self)
        self.setup_menu_bar()
        self.setup_dock_widgets()
        self.setup_graph_controls()

    def setup_menu_bar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)
        file_menu.addAction("Exit", self.close)

        tools_menu = QMenu("Tools", self)
        menu_bar.addMenu(tools_menu)
        tools_menu.addAction("Loan Analyzer", self.show_loan_analyzer)
        tools_menu.addAction("New Graph", self.create_new_graph)
        tools_menu.addAction("Show Graph Controls", self.toggle_graph_controls)

    def setup_dock_widgets(self):
        self.loan_widget = LoanWidget()
        self.loan_dock = QDockWidget("Loan Analyzer", self)
        self.loan_dock.setWidget(self.loan_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.loan_dock)

        # Connect signals from LoanWidget to update graphs
        self.loan_widget.loan_updated.connect(self.update_all_graphs)
        self.loan_widget.loan_added.connect(self.update_all_graphs)
        self.loan_widget.loan_removed.connect(self.update_all_graphs)
        self.loan_widget.loan_renamed.connect(self.update_all_graphs)

    def setup_graph_controls(self):
        self.graph_controls = QWidget()
        layout = QVBoxLayout(self.graph_controls)

        self.graph_list = QListWidget()
        self.graph_list.itemSelectionChanged.connect(self.update_selected_graph)
        layout.addWidget(self.graph_list)

        delete_graph_button = QPushButton("Delete Graph")
        delete_graph_button.clicked.connect(self.delete_selected_graph)
        layout.addWidget(delete_graph_button)

        self.loan_selection_widget = QWidget()
        self.loan_selection_layout = QVBoxLayout(self.loan_selection_widget)
        layout.addWidget(self.loan_selection_widget)

        self.graph_controls_dock = QDockWidget("Graph Controls", self)
        self.graph_controls_dock.setWidget(self.graph_controls)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.graph_controls_dock)
        self.graph_controls_dock.hide()  # Initially hide the graph controls

    def toggle_graph_controls(self):
        if self.graph_controls_dock.isVisible():
            self.graph_controls_dock.hide()
        else:
            self.graph_controls_dock.show()

    def create_new_graph(self):
        title, ok = QInputDialog.getText(self, "New Graph", "Enter graph title:")
        if ok and title:
            graph = self.graph_manager.create_graph(title)
            self.graph_list.addItem(title)
            graph.visibilityChanged.connect(self.update_graph_list)
            self.update_all_graphs()

    def update_graph_list(self):
        self.graph_list.clear()
        for graph in self.graph_manager.graphs:
            if not graph.isHidden():
                self.graph_list.addItem(graph.windowTitle())

    def update_selected_graph(self):
        selected_items = self.graph_list.selectedItems()
        if selected_items:
            selected_graph_title = selected_items[0].text()
            selected_graph = next((graph for graph in self.graph_manager.graphs if graph.windowTitle() == selected_graph_title), None)
            if selected_graph:
                self.show_loan_selection(selected_graph)

    def show_loan_selection(self, graph):
        # Clear previous loan selection widgets
        for i in reversed(range(self.loan_selection_layout.count())): 
            self.loan_selection_layout.itemAt(i).widget().setParent(None)

        self.checkboxes = []
        for scenario in self.loan_widget.loan_scenarios:
            checkbox = QCheckBox(scenario.name)
            checkbox.setChecked(True)  # Default to checked
            checkbox.stateChanged.connect(lambda: self.update_graph(graph))
            self.checkboxes.append(checkbox)
            self.loan_selection_layout.addWidget(checkbox)

        self.update_graph(graph)

    def update_graph(self, graph):
        selected_scenarios = [scenario for scenario, checkbox in zip(self.loan_widget.loan_scenarios, self.checkboxes) if checkbox.isChecked()]
        graph.update_graph(selected_scenarios)

    def delete_selected_graph(self):
        selected_items = self.graph_list.selectedItems()
        if selected_items:
            selected_graph_title = selected_items[0].text()
            self.graph_manager.remove_graph(selected_graph_title)
            self.update_graph_list()

    def update_all_graphs(self):
        for graph in self.graph_manager.graphs:
            if not graph.isHidden():
                selected_scenarios = [scenario for scenario, checkbox in zip(self.loan_widget.loan_scenarios, self.checkboxes) if checkbox.isChecked()]
                graph.update_graph(selected_scenarios)

    def show_loan_analyzer(self):
        self.loan_dock.show()
        self.loan_dock.raise_()