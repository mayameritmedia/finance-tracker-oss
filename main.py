
from datetime import datetime
from decimal import Decimal, InvalidOperation

from database import (
    delete_transaction,
    get_budgets,
    get_monthly_transactions,
    get_transactions,
    initialize_budgets,
    initialize_database,
    save_budget,
    save_transaction,
    update_transaction,
)

CATEGORIES = [
    "Housing",
    "Groceries",
    "Transportation",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Savings",
    "Other"
]


def money(cents):
    sign = "-" if cents < 0 else ""
    value = abs(cents)
    return f"{sign}${value // 100:,}.{value % 100:02d}"


def choose_category(kind):
    if kind == "income":
        return "Income"

    print("\nSelect a category:")

    for number, category in enumerate(CATEGORIES, 1):
        print(f"{number}. {category}")

    choice = input("Category number: ").strip()

    if choice.isdigit():
        index = int(choice) - 1

        if 0 <= index < len(CATEGORIES):
            return CATEGORIES[index]

    return "Other"


def add_transaction(kind):
    description = input("Description: ").strip()

    if not description:
        print("Description cannot be empty.")
        return

    try:
        amount = Decimal(input("Amount ($): "))

        if not amount.is_finite() or amount <= 0:
            print("Amount must be positive.")
            return

        cents = amount * 100

        if cents != cents.to_integral_value():
            print("Maximum 2 decimal places allowed.")
            return

        amount_cents = int(cents)

    except InvalidOperation:
        print("Invalid amount.")
        return

    category = choose_category(kind)

    save_transaction(
        kind,
        description,
        amount_cents,
        category
    )

    print("Transaction saved successfully!")


def view_balance():
    transactions = get_transactions()

    income = sum(
        row[3]
        for row in transactions
        if row[1] == "income"
    )

    expenses = sum(
        row[3]
        for row in transactions
        if row[1] == "expense"
    )

    print("\n===== ACCOUNT SUMMARY =====")
    print(f"Total Income:   {money(income)}")
    print(f"Total Expenses: {money(expenses)}")
    print(f"Balance:        {money(income - expenses)}")


def view_history():
    transactions = get_transactions()

    if not transactions:
        print("\nNo transactions found.")
        return

    print("\n===== TRANSACTION HISTORY =====")

    for row in transactions:
        transaction_id, kind, description, cents, category, date = row

        print(
            f"#{transaction_id} | {date[:10]} | "
            f"{kind.title()} | {category} | "
            f"{description} | {money(cents)}"
        )


def monthly_summary():
    month = input("Enter month (YYYY-MM): ").strip()

    try:
        datetime.strptime(month, "%Y-%m")

        if len(month) != 7:
            raise ValueError

    except ValueError:
        print("Invalid month. Example: 2026-11")
        return

    transactions = get_monthly_transactions(month)

    income = sum(
        amount
        for kind, category, amount in transactions
        if kind == "income"
    )

    expenses = sum(
        amount
        for kind, category, amount in transactions
        if kind == "expense"
    )

    print(f"\n===== MONTHLY SUMMARY: {month} =====")
    print(f"Income:   {money(income)}")
    print(f"Expenses: {money(expenses)}")
    print(f"Balance:  {money(income - expenses)}")

    totals = {}

    for kind, category, amount in transactions:
        if kind == "expense":
            totals[category] = (
                totals.get(category, 0) + amount
            )

    print("\nExpenses by category:")

    if not totals:
        print("No expenses recorded.")

    for category, amount in sorted(
        totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(f"{category}: {money(amount)}")


def read_month():
    month = input("Enter month (YYYY-MM): ").strip()

    try:
        datetime.strptime(month, "%Y-%m")

        if len(month) != 7:
            raise ValueError

    except ValueError:
        print("Invalid month. Example: 2026-11")
        return None

    return month


def set_monthly_budget():
    month = read_month()

    if month is None:
        return

    print("\nSelect budget category:")

    for number, category in enumerate(CATEGORIES, 1):
        print(f"{number}. {category}")

    choice = input("Category number: ").strip()

    if not choice.isdigit():
        print("Invalid category.")
        return

    index = int(choice) - 1

    if not 0 <= index < len(CATEGORIES):
        print("Invalid category.")
        return

    category = CATEGORIES[index]

    try:
        amount = Decimal(input("Monthly budget ($): "))

        if not amount.is_finite() or amount < 0:
            print("Budget cannot be negative.")
            return

        cents = amount * 100

        if cents != cents.to_integral_value():
            print("Maximum 2 decimal places allowed.")
            return

    except InvalidOperation:
        print("Invalid amount.")
        return

    save_budget(month, category, int(cents))

    print(f"Budget saved: {category} = {money(int(cents))}")


def view_budget_report():
    month = read_month()

    if month is None:
        return

    transactions = get_monthly_transactions(month)
    budgets = get_budgets(month)

    income = sum(
        amount for kind, category, amount in transactions
        if kind == "income"
    )

    expenses = {}

    for kind, category, amount in transactions:
        if kind == "expense":
            expenses[category] = (
                expenses.get(category, 0) + amount
            )

    total_budget = sum(amount for category, amount in budgets)

    print(f"\n===== BUDGET REPORT: {month} =====")
    print(f"Monthly Income:  {money(income)}")
    print(f"Assigned Budget: {money(total_budget)}")
    print(f"Left to Assign:  {money(income - total_budget)}")

    print("\nCategory              Budget        Spent       Left")
    print("-" * 62)

    for category, budget in budgets:
        spent = expenses.get(category, 0)
        remaining = budget - spent

        print(
            f"{category:<20}"
            f"{money(budget):>12}"
            f"{money(spent):>12}"
            f"{money(remaining):>12}"
        )

    unbudgeted = [
        (category, spent)
        for category, spent in expenses.items()
        if category not in dict(budgets)
    ]

    if unbudgeted:
        print("\nExpenses without a budget:")

        for category, spent in unbudgeted:
            print(f"{category}: {money(spent)}")


def find_transaction():
    view_history()

    try:
        transaction_id = int(
            input("\nEnter transaction ID: ").strip()
        )
    except ValueError:
        print("Invalid transaction ID.")
        return None

    transactions = get_transactions()

    for transaction in transactions:
        if transaction[0] == transaction_id:
            return transaction

    print("Transaction not found.")
    return None


def edit_transaction():
    transaction = find_transaction()

    if transaction is None:
        return

    transaction_id, kind, old_description, old_cents, old_category, _date = transaction

    print(f"\nEditing transaction #{transaction_id}")
    print("Press Enter to keep the current value.")

    description = input(
        f"Description [{old_description}]: "
    ).strip() or old_description

    amount_text = input(
        f"Amount [{money(old_cents)}]: "
    ).strip()

    amount_cents = old_cents

    if amount_text:
        try:
            amount = Decimal(amount_text)

            if not amount.is_finite() or amount <= 0:
                print("Amount must be positive.")
                return

            cents = amount * 100

            if cents != cents.to_integral_value():
                print("Maximum 2 decimal places allowed.")
                return

            amount_cents = int(cents)

        except InvalidOperation:
            print("Invalid amount.")
            return

    if kind == "income":
        category = "Income"
    else:
        print(f"\nCurrent category: {old_category}")
        print("Press Enter to keep the current category.")

        for number, name in enumerate(CATEGORIES, 1):
            print(f"{number}. {name}")

        choice = input("New category number: ").strip()

        category = old_category

        if choice:
            if not choice.isdigit():
                print("Invalid category.")
                return

            index = int(choice) - 1

            if not 0 <= index < len(CATEGORIES):
                print("Invalid category.")
                return

            category = CATEGORIES[index]

    print("\nUpdated values:")
    print(f"Description: {description}")
    print(f"Amount: {money(amount_cents)}")
    print(f"Category: {category}")

    confirm = input("Save changes? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Changes cancelled.")
        return

    updated = update_transaction(
        transaction_id,
        description,
        amount_cents,
        category
    )

    if updated:
        print("Transaction updated successfully!")
    else:
        print("Transaction could not be updated.")


def remove_transaction():
    transaction = find_transaction()

    if transaction is None:
        return

    transaction_id, _kind, description, cents, category, _date = transaction

    print("\nTransaction to delete:")
    print(f"ID: #{transaction_id}")
    print(f"Description: {description}")
    print(f"Amount: {money(cents)}")
    print(f"Category: {category}")

    confirm = input(
        "Type DELETE to permanently remove this transaction: "
    ).strip()

    if confirm != "DELETE":
        print("Deletion cancelled.")
        return

    deleted = delete_transaction(transaction_id)

    if deleted:
        print("Transaction deleted successfully!")
    else:
        print("Transaction could not be deleted.")




def main():
    initialize_database()
    initialize_budgets()

    while True:
        print("\n===== PERSONAL FINANCE TRACKER =====")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Balance")
        print("4. Transaction History")
        print("5. Monthly Summary")
        print("6. Set Monthly Budget")
        print("7. View Budget Report")
        print("8. Edit Transaction")
        print("9. Delete Transaction")
        print("10. Exit")

        choice = input("\nChoose an option (1-10): ").strip()

        if choice == "1":
            add_transaction("income")
        elif choice == "2":
            add_transaction("expense")
        elif choice == "3":
            view_balance()
        elif choice == "4":
            view_history()
        elif choice == "5":
            monthly_summary()
        elif choice == "6":
            set_monthly_budget()
        elif choice == "7":
            view_budget_report()
        elif choice == "8":
            edit_transaction()
        elif choice == "9":
            remove_transaction()
        elif choice == "10":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()


