from dataclasses import dataclass, field
from typing import Protocol


# Command interface
class Transaction(Protocol):
    def execute(self) -> None: ...

    def undo(self) -> None: ...

    def redo(self) -> None: ...


# Receiver class
class BankAccount:
    def __init__(self, name: str) -> None:
        self.balance = 0
        self.name = name
        self.account_number = id(self)  # Unique account number for demonstration

    def deposit(self, amount: int) -> None:
        self.balance += amount
        print(f"Account {self.name} {self.account_number}: Deposited {amount}, new balance is {self.balance}")

    def withdraw(self, amount: int) -> None:
        if amount > self.balance:
            raise ValueError("Insufficient funds")

        self.balance -= amount
        print(f"Account {self.name} {self.account_number}: Withdrew {amount}, new balance is {self.balance}")


# Invoker class
@dataclass
class TransactionExecutor:
    undo_stack: list[Transaction] = field(default_factory=list)
    redo_stack: list[Transaction] = field(default_factory=list)

    def execute_transaction(self, transaction: Transaction) -> None:
        transaction.execute()
        self.undo_stack.append(transaction)
        self.redo_stack.clear()

    def undo(self) -> None:
        if not self.undo_stack:
            print("No transactions to undo")
            return

        transaction = self.undo_stack.pop()
        transaction.undo()
        self.redo_stack.append(transaction)

    def redo(self) -> None:
        if not self.redo_stack:
            print("No transactions to redo")
            return

        transaction = self.redo_stack.pop()
        transaction.redo()
        self.undo_stack.append(transaction)


# Concrete command classes
class Deposit:
    def __init__(self, account: BankAccount, amount: int) -> None:
        self.account = account
        self.amount = amount

    def execute(self) -> None:
        self.account.deposit(self.amount)

    def undo(self) -> None:
        self.account.withdraw(self.amount)

    def redo(self) -> None:
        self.account.deposit(self.amount)


class Withdraw:
    def __init__(self, account: BankAccount, amount: int) -> None:
        self.account = account
        self.amount = amount

    def execute(self) -> None:
        self.account.withdraw(self.amount)

    def undo(self) -> None:
        self.account.deposit(self.amount)

    def redo(self) -> None:
        self.account.withdraw(self.amount)


class Transfer:
    def __init__(self, from_account: BankAccount, to_account: BankAccount, amount: int) -> None:
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount

    def execute(self) -> None:
        self.from_account.withdraw(self.amount)
        self.to_account.deposit(self.amount)

    def undo(self) -> None:
        self.to_account.withdraw(self.amount)
        self.from_account.deposit(self.amount)

    def redo(self) -> None:
        self.from_account.withdraw(self.amount)
        self.to_account.deposit(self.amount)


if __name__ == "__main__":
    snoopy_account = BankAccount("Snoopy")
    pluto_account = BankAccount("Pluto")
    executor = TransactionExecutor()

    # Execute some transactions
    executor.execute_transaction(Deposit(snoopy_account, 100))
    executor.execute_transaction(Withdraw(snoopy_account, 50))
    executor.execute_transaction(Transfer(snoopy_account, pluto_account, 25))
