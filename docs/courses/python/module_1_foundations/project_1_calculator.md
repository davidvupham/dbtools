# Project 1: CLI Financial Calculator

**Goal**: Build a command-line tool to calculate compound interest, tax, and investment returns.

## Learning Objectives

* Control Flow (`if`, `match`, `while`)
* Error Handling (`try`, `except`)
* User Input (`input()`)
* String Formatting

## Requirements

1. **Menu System**
    * Display options: "Compound Interest", "Income Tax", "Investment Return", "Exit".
    * Loop until user chooses exit.

2. **Compound Interest Calculator**
    * Input: Principal, Rate, Time.
    * Formula: $A = P(1 + \frac{r}{n})^{nt}$
    * Output: Final Amount.

3. **Income Tax**
    * Input: Annual Income.
    * Logic: Progressive tax brackets (e.g., 0-10k: 0%, 10-50k: 10%, 50k+: 20%).

4. **Robustness**
    * Handle invalid inputs (e.g., "abc" for rate) gracefully.
    * Don't crash.

## Challenge

Save the history of calculations to a list and print it on exit.
