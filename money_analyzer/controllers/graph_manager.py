from ..ui.widgets.graph_widget import GraphWidget
from PyQt6.QtCore import Qt

class GraphManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.graphs = []

    def create_graph(self, title="Financial Graph"):
        graph = GraphWidget(parent=self.main_window, title=title)
        self.graphs.append(graph)
        self.main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, graph)
        return graph

    def remove_graph(self, title):
        graph = next((graph for graph in self.graphs if graph.windowTitle() == title), None)
        if graph:
            self.graphs.remove(graph)
            self.main_window.removeDockWidget(graph)
            graph.deleteLater()

    def update_all_graphs(self, data_sources):
        for graph in self.graphs:
            if not graph.isHidden():
                graph.update_graph(data_sources)