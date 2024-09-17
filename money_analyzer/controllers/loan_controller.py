from ..models.loan import Loan
import numpy as np

class LoanController:
    def __init__(self):
        self.loan = None

    def create_loan(self, loan_amount, interest_rate, loan_term, down_payment, extra_payment):
        self.loan = Loan(loan_amount, interest_rate, loan_term, down_payment, extra_payment)

    def get_loan_summary(self):
        if not self.loan:
            raise ValueError("Loan has not been created yet.")

        loan_details = self.loan.calculate_loan_details()
        total_interest = sum(loan_details['interest_payments'])
        total_payments = sum(loan_details['principal_payments']) + total_interest

        return {
            'loan_amount': self.loan.principal - self.loan.down_payment,
            'monthly_payment': self.loan.monthly_payment,
            'total_interest': total_interest,
            'total_payments': total_payments,
            'loan_term': len(loan_details['months']) / 12
        }

    def get_amortization_data(self):
        if not self.loan:
            return None

        return self.loan.calculate_loan_details()
