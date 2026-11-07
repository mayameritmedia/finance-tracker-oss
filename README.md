
# Personal Finance Tracker

A Python-based personal finance and budgeting application using SQLite.

## Features

- Add income and expense transactions
- Categorize expenses
- View account balance
- Review transaction history
- Generate monthly financial summaries
- Set monthly budgets
- Compare spending against budgets
- Edit and delete transactions

## Technologies

- Python 3
- SQLite
- Git and GitHub

## Getting Started

1. Clone the repository.
2. Make sure Python 3 is installed.
3. Open a terminal in the project directory.
4. Run:

   python main.py

## Current Version

v0.6 — Command-line application.

## Planned Improvements

- Automated tests
- CI/CD using GitHub Actions
- Visual financial dashboard
- Mobile application

## Privacy

Financial records are stored locally in a SQLite database.
The database file is excluded from version control.


## Running Automated Tests

Run the automated tests locally:

```bash
python -m unittest discover -v
```

## Continuous Integration

This project uses GitHub Actions to automatically
run Python database tests on every push and
pull request targeting the main branch.

Workflow file: `.github/workflows/python-ci.yml`
