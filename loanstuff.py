import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

# Function to calculate loan payment details
def calculate_loan_details(loan_amount, down_payment, annual_rate, years):
    principal = loan_amount - down_payment
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -num_payments)
    
    interest_payment = np.zeros(num_payments)
    principal_payment = np.zeros(num_payments)
    remaining_balance = principal

    for i in range(num_payments):
        interest_payment[i] = remaining_balance * monthly_rate
        principal_payment[i] = monthly_payment - interest_payment[i]
        remaining_balance -= principal_payment[i]

    return monthly_payment, principal_payment, interest_payment

# Function to update the graph and summary
def update_graph_and_summary(event=None):
    loan_amount = loan_amount_slider.get()
    interest_rate = interest_rate_slider.get()
    loan_term = loan_term_slider.get()
    down_payment = down_payment_slider.get()

    # Calculate loan details
    monthly_payment, principal_payment, interest_payment = calculate_loan_details(loan_amount, down_payment, interest_rate, loan_term)
    total_payments = len(principal_payment)

    # Update the graph
    ax.clear()
    ax.plot(np.cumsum(principal_payment), label="Principal Paid")
    ax.plot(np.cumsum(interest_payment), label="Interest Paid")
    ax.set_title("Loan Repayment Breakdown")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount Paid")
    ax.legend()
    canvas.draw()

    # Update the summary
    total_interest_paid = np.sum(interest_payment)
    apr = interest_rate  # For simplicity, treating APR as the nominal interest rate
    summary_text.set(f"APR: {apr:.2f}%\n"
                     f"Monthly Payment: ${monthly_payment:.2f}\n"
                     f"Total Interest Paid: ${total_interest_paid:.2f}\n"
                     f"Monthly Principal: ${np.mean(principal_payment):.2f}\n"
                     f"Monthly Interest: ${np.mean(interest_payment):.2f}")

# Initialize the main window
root = tk.Tk()
root.title("Enhanced Loan Calculator")

# Create a figure and axes for the matplotlib plot
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Loan Amount Slider
tk.Label(root, text="Loan Amount ($)").pack()
loan_amount_slider = tk.Scale(root, from_=1000, to=1000000, orient=tk.HORIZONTAL, length=400)
loan_amount_slider.set(250000)  # default value
loan_amount_slider.pack()
loan_amount_slider.bind("<Motion>", update_graph_and_summary)

# Down Payment Slider
tk.Label(root, text="Down Payment ($)").pack()
down_payment_slider = tk.Scale(root, from_=0, to=500000, orient=tk.HORIZONTAL, length=400)
down_payment_slider.set(50000)  # default value
down_payment_slider.pack()
down_payment_slider.bind("<Motion>", update_graph_and_summary)

# Interest Rate Slider
tk.Label(root, text="Interest Rate (%)").pack()
interest_rate_slider = tk.Scale(root, from_=0.5, to=15, resolution=0.1, orient=tk.HORIZONTAL, length=400)
interest_rate_slider.set(5)  # default value
interest_rate_slider.pack()
interest_rate_slider.bind("<Motion>", update_graph_and_summary)

# Loan Term Slider
tk.Label(root, text="Loan Term (Years)").pack()
loan_term_slider = tk.Scale(root, from_=1, to=30, orient=tk.HORIZONTAL, length=400)
loan_term_slider.set(30)  # default value
loan_term_slider.pack()
loan_term_slider.bind("<Motion>", update_graph_and_summary)

# Summary Text Box
summary_text = tk.StringVar()
summary_label = ttk.Label(root, textvariable=summary_text, font=("Arial", 12), justify="left")
summary_label.pack()

# Initial graph and summary
update_graph_and_summary()

# Start the GUI event loop
root.mainloop()