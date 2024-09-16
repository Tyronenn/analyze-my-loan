from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDockWidget
from PyQt6.QtCore import Qt, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.text import Text

class GraphWidget(QDockWidget):
    visibilityChanged = pyqtSignal(bool)

    def __init__(self, parent=None, title="Financial Graph"):
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
        self.fig, self.ax = plt.subplots(figsize=(8, 6))  # Increased figure size
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.hover_text = self.ax.text(0.5, 1.05, '', transform=self.ax.transAxes, ha='center')
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def update_graph(self, data_sources):
        self.ax.clear()
        max_x = 0
        max_y = 0
        
        for source in data_sources:
            data = source.get_data()
            x = data.get('x', range(len(data['y'])))
            y = data['y']
            self.ax.plot(x, y, label=source.get_name())
            
            max_x = max(max_x, max(x))
            max_y = max(max_y, max(y))
        
        self.ax.set_title(data_sources[0].get_title() if data_sources else "Financial Data")
        self.ax.set_xlabel(data_sources[0].get_x_label() if data_sources else "X-axis")
        self.ax.set_ylabel(data_sources[0].get_y_label() if data_sources else "Y-axis")
        
        # Set appropriate axis limits
        self.ax.set_xlim(0, max_x * 1.05)  # Add 5% padding
        self.ax.set_ylim(0, max_y * 1.05)  # Add 5% padding
        
        handles, labels = self.ax.get_legend_handles_labels()
        if labels:
            self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

        # Always show grid lines
        self.ax.grid(True)

        # Adjust the layout
        self.fig.subplots_adjust(bottom=0.2, top=0.9, left=0.1, right=0.9)
        self.canvas.draw()

    def on_hover(self, event):
        if event.inaxes == self.ax and self.ax.lines:
            try:
                month = int(event.xdata)
                if 0 <= month < len(self.ax.lines[0].get_xdata()):
                    principal = self.ax.lines[0].get_ydata()[month]
                    interest = self.ax.lines[1].get_ydata()[month]
                    hover_text = f"Month: {month}, Principal: ${principal:,.2f}, Interest: ${interest:,.2f}"
                    self.hover_text.set_text(hover_text)
                    self.canvas.draw_idle()
                else:
                    self.hover_text.set_text('')
            except (ValueError, IndexError):
                self.hover_text.set_text('')
        else:
            self.hover_text.set_text('')

    def closeEvent(self, event):
        self.visibilityChanged.emit(False)
        super().closeEvent(event)

    def showEvent(self, event):
        self.visibilityChanged.emit(True)
        super().showEvent(event)