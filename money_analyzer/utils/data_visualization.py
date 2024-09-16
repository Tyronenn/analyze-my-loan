import matplotlib.pyplot as plt
import mplcursors
import numpy as np

def create_interactive_line_graph(x_data, y_data, title="Line Graph", x_label="X-axis", y_label="Y-axis"):
    fig, ax = plt.subplots()
    ax.plot(x_data, y_data, label='Data Line')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend()

    # Add interactivity
    cursor = mplcursors.cursor(ax, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(f'X: {sel.target[0]:.2f}\nY: {sel.target[1]:.2f}'))

    plt.show()

def create_interactive_pie_chart(labels, sizes, title="Pie Chart"):
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.set_title(title)

    # Add interactivity
    cursor = mplcursors.cursor(wedges, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(f'{labels[sel.index]}: {sizes[sel.index]:.2f}%'))

    plt.show()

# Example usage
if __name__ == "__main__":
    # Line graph example
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    create_interactive_line_graph(x, y, title="Sine Wave", x_label="Time", y_label="Amplitude")

    # Pie chart example
    labels = ['A', 'B', 'C', 'D']
    sizes = [15, 30, 45, 10]
    create_interactive_pie_chart(labels, sizes, title="Sample Pie Chart")
