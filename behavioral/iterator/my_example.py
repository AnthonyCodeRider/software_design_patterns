from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any, Protocol


class Rule(Protocol):
    def apply(self, data: Any) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...


class RuleIterator(Iterator[Rule]):
    def __next__(self) -> Rule: ...


class SimpleRuleIterator(RuleIterator):
    def __init__(self, rules: RuleGroup):
        self._rules = rules._rules
        self._index = 0

    def __next__(self) -> Rule:
        if self._index < len(self._rules):
            rule = self._rules[self._index]
            self._index += 1
            return rule
        else:
            raise StopIteration


class NestedRuleIterator(RuleIterator):
    def __init__(self, rule_group: RuleGroup):
        self._rule_group = rule_group
        self._index = 0
        self._current_iterator: RuleIterator | None = None

    def __next__(self) -> Rule:
        while True:
            if self._current_iterator is None:
                if self._index < len(self._rule_group._rules):
                    current_rule = self._rule_group._rules[self._index]
                    self._index += 1
                    if isinstance(current_rule, RuleGroup):
                        self._current_iterator = current_rule.get_nested_iterator()
                    else:
                        return current_rule
                else:
                    raise StopIteration
            else:
                try:
                    return next(self._current_iterator)
                except StopIteration:
                    self._current_iterator = None


class RuleGroup(Iterable):
    def __init__(self):
        self._rules: list[Rule] = []

    def add_rule(self, rule: Rule) -> None:
        self._rules.append(rule)

    def apply(self, data: Any) -> bool:
        for rule in self._rules:
            if not rule.apply(data):
                return False
        return True

    def __iter__(self) -> RuleIterator:
        return SimpleRuleIterator(self)

    def get_nested_iterator(self) -> RuleIterator:
        return NestedRuleIterator(self)

    def __str__(self) -> str:
        return f"RuleGroup({self._rules})"

    def __repr__(self) -> str:
        return self.__str__()


class RuleA1:
    def apply(self, data: Any) -> bool:
        print("Applying RuleA1 to data...")
        return True

    def __str__(self) -> str:
        return "RuleA1"

    def __repr__(self) -> str:
        return self.__str__()


class RuleA2:
    def apply(self, data: Any) -> bool:
        print("Applying RuleA2 to data...")
        return True

    def __str__(self) -> str:
        return "RuleA2"

    def __repr__(self) -> str:
        return self.__str__()


class RuleK1:
    def apply(self, data: Any) -> bool:
        print("Applying RuleK1 to data...")
        return True

    def __str__(self) -> str:
        return "RuleK1"

    def __repr__(self) -> str:
        return self.__str__()


class RuleK2:
    def apply(self, data: Any) -> bool:
        print("Applying RuleK2 to data...")
        return True

    def __str__(self) -> str:
        return "RuleK2"

    def __repr__(self) -> str:
        return self.__str__()


if __name__ == "__main__":
    airflow_rules = RuleGroup()
    airflow_rules.add_rule(RuleA1())
    airflow_rules.add_rule(RuleA2())

    kafka_rules = RuleGroup()
    kafka_rules.add_rule(RuleK1())
    kafka_rules.add_rule(RuleK2())

    rules = RuleGroup()
    rules.add_rule(airflow_rules)
    rules.add_rule(kafka_rules)

    print("Iterating over rules (simple iterator):")
    for rule in rules:
        print(rule)
        rule.apply(None)

    print("Iterating over rules (nested iterator):")
    nested_iterator = rules.get_nested_iterator()
    for rule in nested_iterator:
        print(rule)
        rule.apply(None)
