from ..models.loan import Loan
import numpy as np

class LoanController:
    def __init__(self):
        self.loan = None

    def create_loan(self, principal, interest_rate, term, down_payment=0, extra_payment=0):
        self.loan = Loan(principal, interest_rate, term, down_payment, extra_payment)

    def get_loan_summary(self):
        if not self.loan:
            raise ValueError("Loan has not been created yet.")

        monthly_payment, principal_payments, interest_payments = self.loan.calculate_loan_details()
        total_interest = np.sum(interest_payments)
        total_payments = np.sum(principal_payments) + total_interest

        return {
            'loan_amount': self.loan.principal - self.loan.down_payment,
            'monthly_payment': monthly_payment,
            'total_interest': total_interest,
            'total_payments': total_payments,
            'loan_term': len(principal_payments) / 12
        }

    def get_amortization_data(self):
        if not self.loan:
            raise ValueError("Loan has not been created yet.")

        monthly_payment, principal_payments, interest_payments = self.loan.calculate_loan_details()
        months = np.arange(1, len(principal_payments) + 1)

        return {
            'months': months,
            'principal_payments': np.cumsum(principal_payments),
            'interest_payments': np.cumsum(interest_payments)
        }
