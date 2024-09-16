from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDockWidget
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class GraphWidget(QDockWidget):
    def __init__(self, parent=None, title="Loan Graph"):
        super().__init__(title, parent)
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                         QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                         QDockWidget.DockWidgetFeature.DockWidgetClosable)
        
        self.content = QWidget()
        self.setWidget(self.content)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self.content)
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def update_graph(self, loan_scenarios, show_horizontal_grid, show_vertical_grid):
        self.ax.clear()
        for scenario in loan_scenarios:
            amortization_data = scenario.get_amortization_data()
            self.ax.plot(amortization_data['months'], amortization_data['principal_payments'], label=f"Principal Paid ({scenario.name})")
            self.ax.plot(amortization_data['months'], amortization_data['interest_payments'], label=f"Interest Paid ({scenario.name})")
        
        self.ax.set_title("Loan Repayment Breakdown")
        self.ax.set_xlabel("Month")
        self.ax.set_ylabel("Amount Paid")
        
        handles, labels = self.ax.get_legend_handles_labels()
        if labels:
            self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

        self.ax.grid(show_horizontal_grid, axis='y')
        self.ax.grid(show_vertical_grid, axis='x')

        self.fig.subplots_adjust(bottom=0.2, top=0.8)
        self.canvas.draw()

    def on_hover(self, event):
        if event.inaxes == self.ax:
            month = int(event.xdata)
            if 0 <= month < len(self.ax.lines[0].get_xdata()):
                principal = self.ax.lines[0].get_ydata()[month]
                interest = self.ax.lines[1].get_ydata()[month]
                self.ax.set_title(f"Month: {month}, Principal: ${principal:,.2f}, Interest: ${interest:,.2f}")
                self.canvas.draw()