import numpy as np

class Loan:
    def __init__(self, principal, interest_rate, term, down_payment=0, extra_payment=0):
        self.principal = principal
        self.interest_rate = interest_rate
        self.term = term
        self.down_payment = down_payment
        self.extra_payment = extra_payment

    def calculate_monthly_payment(self):
        loan_amount = self.principal - self.down_payment
        monthly_rate = self.interest_rate / 12 / 100
        num_payments = self.term * 12
        if monthly_rate == 0:
            return loan_amount / num_payments
        return (loan_amount * monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)

    def generate_amortization_schedule(self):
        monthly_payment = self.calculate_monthly_payment()
        remaining_balance = self.principal - self.down_payment
        schedule = []

        for month in range(1, self.term * 12 + 1):
            interest_payment = remaining_balance * (self.interest_rate / 12 / 100)
            principal_payment = monthly_payment - interest_payment + self.extra_payment
            
            if remaining_balance - principal_payment < 0:
                principal_payment = remaining_balance
                interest_payment = remaining_balance * (self.interest_rate / 12 / 100)
                monthly_payment = principal_payment + interest_payment

            remaining_balance -= principal_payment

            schedule.append({
                'month': month,
                'payment': monthly_payment + self.extra_payment,
                'principal': principal_payment,
                'interest': interest_payment,
                'balance': max(0, remaining_balance)
            })

            if remaining_balance <= 0:
                break

        return schedule

    def calculate_loan_details(self):
        schedule = self.generate_amortization_schedule()
        monthly_payment = self.calculate_monthly_payment() + self.extra_payment
        principal_payments = [payment['principal'] for payment in schedule]
        interest_payments = [payment['interest'] for payment in schedule]
        
        return monthly_payment, np.array(principal_payments), np.array(interest_payments)