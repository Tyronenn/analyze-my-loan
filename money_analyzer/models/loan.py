import numpy as np

class Loan:
    def __init__(self, principal, interest_rate, term, down_payment=0, extra_payment=0):
        self.principal = principal
        self.interest_rate = interest_rate
        self.term = term
        self.down_payment = down_payment
        self.extra_payment = extra_payment
        self.monthly_payment = self.calculate_monthly_payment()

    def calculate_monthly_payment(self):
        loan_amount = self.principal - self.down_payment
        monthly_rate = self.interest_rate / 12 / 100
        num_payments = self.term * 12
        if monthly_rate == 0:
            return loan_amount / num_payments
        return (loan_amount * monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)

    def generate_amortization_schedule(self):
        remaining_balance = self.principal - self.down_payment
        schedule = []
        cumulative_interest = 0

        for month in range(1, self.term * 12 + 1):
            interest_payment = remaining_balance * (self.interest_rate / 12 / 100)
            principal_payment = self.monthly_payment - interest_payment + self.extra_payment
            
            if remaining_balance - principal_payment < 0:
                principal_payment = remaining_balance
                interest_payment = remaining_balance * (self.interest_rate / 12 / 100)

            remaining_balance -= principal_payment
            cumulative_interest += interest_payment

            schedule.append({
                'month': month,
                'payment': self.monthly_payment + self.extra_payment,
                'principal': principal_payment,
                'interest': interest_payment,
                'balance': max(0, remaining_balance),
                'cumulative_interest': cumulative_interest
            })

            if remaining_balance <= 0:
                break

        return schedule

    def calculate_loan_details(self):
        schedule = self.generate_amortization_schedule()
        principal_payments = [payment['principal'] for payment in schedule]
        interest_payments = [payment['interest'] for payment in schedule]
        remaining_balance = [payment['balance'] for payment in schedule]
        cumulative_interest = [payment['cumulative_interest'] for payment in schedule]
        
        return {
            'months': list(range(1, len(schedule) + 1)),
            'principal_payments': principal_payments,
            'interest_payments': interest_payments,
            'remaining_balance': remaining_balance,
            'cumulative_interest': cumulative_interest
        }