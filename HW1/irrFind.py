import sys
import numpy as np
from scipy.optimize import fsolve

TXT_PATH = "/Users/ss580/Desktop/python/fintech/Homework 1 Computing IRR copy.txt"

# 1.read the file and get cashflow, cashflow period, compound period
cashflow = []
cashflow_period = []
period = []
equatio_left = 0
for line in sys.stdin:
    strip_line_initial = line.strip()
    strip_line = strip_line_initial.split(" ")
    cashflow.append(strip_line[0:-2])
    cashflow_period.append(float(strip_line[-2]))
    period.append(float(strip_line[-2]) / float(strip_line[-1]))

def irr_find(r, cash_flow, period):
    equation_left = cash_flow[0]
    for t, c in enumerate(cash_flow[1:]):
        equation_left += c / (1 + r / period) ** ((t + 1) * period)
    return equation_left


# 2.build the function which can calculate IRR
for cash_flow_str, p1, p2 in zip(cashflow, period, cashflow_period):
    cash_flow_float = [float(i) for i in cash_flow_str]
    initial_guess = 0
    solution = fsolve(irr_find, initial_guess, args=(cash_flow_float, p1))
    for i in solution:
        if 10 > i * 100 > -10:
            answer = i * 12 / p2
            print(f"{answer * 100:.4f}")
        else:
            print("No valid IRR found.")
