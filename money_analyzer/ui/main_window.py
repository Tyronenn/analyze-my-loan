from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QDockWidget, QInputDialog, QListWidget, QPushButton, QVBoxLayout, QWidget, QCheckBox, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag
from .widgets.loan_widget import LoanWidget
from .widgets.graph_widget import GraphWidget
from ..controllers.graph_manager import GraphManager  # Add this import

class DraggableLabel(QLabel):
    def __init__(self, text, main_window, parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)
        self.main_window = main_window

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = self.main_window.create_mime_data(self.text())
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.CopyAction)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Money Analyzer")
        self.setGeometry(100, 100, 1200, 800)

        self.graph_manager = GraphManager(self)
        self.checkboxes = {}
        self.current_graph = None
        self.setup_menu_bar()
        self.setup_dock_widgets()
        self.setup_graph_controls()

    def create_mime_data(self, text):
        mime_data = QMimeData()
        if self.current_graph:
            mime_data.setText(f"{self.current_graph.windowTitle()}:{text}")
        else:
            mime_data.setText(text)
        return mime_data

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
        self.loan_widget.loan_updated.connect(self.update_checkboxes)
        self.loan_widget.loan_added.connect(self.update_checkboxes)
        self.loan_widget.loan_removed.connect(self.update_checkboxes)
        self.loan_widget.loan_renamed.connect(self.update_checkboxes)

    def update_checkboxes(self):
        # Update checkboxes based on current loan scenarios
        current_scenarios = set(scenario.name for scenario in self.loan_widget.loan_scenarios)
        
        # Remove checkboxes for scenarios that no longer exist
        for name in list(self.checkboxes.keys()):
            if name not in current_scenarios:
                del self.checkboxes[name]
        
        # Add new checkboxes for new scenarios
        for scenario in self.loan_widget.loan_scenarios:
            if scenario.name not in self.checkboxes:
                self.checkboxes[scenario.name] = True  # Default to checked

        self.update_loan_selection_layout()
        self.update_all_graphs()

    def update_loan_selection_layout(self):
        # Clear previous loan selection widgets
        for i in reversed(range(self.loan_selection_layout.count())): 
            self.loan_selection_layout.itemAt(i).widget().setParent(None)

        # Add current checkboxes and draggable labels to the layout
        for scenario in self.loan_widget.loan_scenarios:
            scenario_widget = QWidget()
            scenario_layout = QVBoxLayout(scenario_widget)

            checkbox = QCheckBox(scenario.name)
            checkbox.setChecked(self.checkboxes.get(scenario.name, True))  # Use stored state or default to True
            checkbox.stateChanged.connect(lambda state, s=scenario.name: self.checkbox_state_changed(s, state))
            scenario_layout.addWidget(checkbox)

            for param in ['Principal Balance', 'Monthly Payment', 'Cumulative Interest', 'Interest Rate']:
                label = DraggableLabel(f"{scenario.name} - {param}", self)
                scenario_layout.addWidget(label)

            self.loan_selection_layout.addWidget(scenario_widget)

    def checkbox_state_changed(self, scenario_name, state):
        self.checkboxes[scenario_name] = state == Qt.CheckState.Checked
        self.update_all_graphs()

    def update_current_graph(self):
        if self.current_graph:
            self.update_graph(self.current_graph)

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
            self.current_graph = next((graph for graph in self.graph_manager.graphs if graph.windowTitle() == selected_graph_title), None)
            if self.current_graph:
                self.show_loan_selection(self.current_graph)

    def show_loan_selection(self, graph):
        self.update_loan_selection_layout()
        self.update_graph(graph)

    def update_graph(self, graph):
        if graph:  # Add this check
            selected_scenarios = [scenario for scenario in self.loan_widget.loan_scenarios 
                                  if self.checkboxes.get(scenario.name, True)]  # Default to True if not found
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
                self.update_graph(graph)

    def show_loan_analyzer(self):
        self.loan_dock.show()
        self.loan_dock.raise_()