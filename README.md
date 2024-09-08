# money-analyzer

## Overview

This Python-based **Loan Analyzer** provides a graphical user interface (GUI) using **PyQt** to help users calculate their monthly loan payments, total interest paid, and view an amortization schedule. The app also features interactive sliders for adjusting loan parameters, and it dynamically updates the graph and summary information in real-time.

The calculator can handle various types of loans and provides an amortization table that can be exported for external analysis. 

---

## Features

- **Real-time Loan Calculation**: Users can input loan amount, down payment, interest rate, and loan term using either sliders or input fields.
- **Graphical Loan Repayment Breakdown**: The app dynamically updates a graph that shows principal vs. interest payments over time.
- **Amortization Table**: Provides a detailed breakdown of monthly payments, including principal and interest portions.
- **Multiple Loan Scenarios**: Easily compare different loan scenarios.
- **CSV Export** (Planned): The ability to export the amortization schedule to a CSV file.

---

## Technologies Used

- **Python 3.x**
- **PyQt6**: For the graphical user interface (GUI).
- **Matplotlib**: For plotting the loan repayment graph.
- **NumPy**: For performing loan payment calculations.
  
---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Tyronenn/analyze-my-loan.git
cd loan-calculator
```

### 2. Create and Activate a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Required Dependencies

```bash
pip install -r requirements.txt
```

Alternatively, you can manually install the necessary libraries:

```bash
pip install pyqt6 numpy matplotlib
```

---

## Usage

To run the application, simply execute the main script:

```bash
python loan-analyzer.py
```

### User Instructions:

1. **Loan Parameters**: Adjust the loan amount, down payment, interest rate, and loan term using either the sliders or the input fields.
2. **Real-Time Updates**: As you adjust the parameters, the graph and amortization table will update in real-time.
3. **Amortization Table**: Switch to the "Amortization Table" tab to view a detailed breakdown of monthly payments, including principal and interest.
4. **Loan Summary**: The summary box provides the APR, total interest paid, and monthly payment.

---

## Planned Features

- **CSV/Excel Export**: Ability to export the amortization table to a CSV or Excel file.
- **Extra Payments**: Support for additional payments toward the principal to reduce the loan term.
- **Loan Comparison**: Ability to compare multiple loan scenarios side by side.
- **Interactive Graph**: Hover over the graph to view exact monthly payments, interest paid, and remaining balance.
- **Dark Mode**: Add a dark mode option for better accessibility.

---

## Project Structure

```bash
loan-calculator/
│
├── loan_analyzer.py         # Main application script
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! If you'd like to improve the project or add new features, feel free to submit a pull request. Please ensure your changes align with the overall project goals and architecture.

---

## Contact

For questions or feedback, please reach out to **[TBD](mailto:your-email@example.com)** or open an issue on GitHub.
