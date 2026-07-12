from abc import ABC, abstractmethod


class Rule(ABC):
    @abstractmethod
    def validate(self, data: dict) -> bool:
        """Validates the given data against the rule."""
        pass


class Rules(Rule):
    """Composite class that contains a group of rules."""

    def __init__(self):
        self.rules: list[Rule] = []

    def validate(self, data: dict) -> bool:
        """Validates the given data against all the rules in the group."""
        for rule in self.rules:
            if not rule.validate(data):
                return False
        return True

    def add(self, rule: Rule) -> None:
        """Adds a new rule to the group."""
        self.rules.append(rule)

    def remove(self, rule: Rule) -> None:
        """Removes a rule from the group."""
        self.rules.remove(rule)


class AirflowDAGIdRule(Rule):
    """Concrete rule that checks if the DAG ID is valid."""

    def validate(self, data: dict) -> bool:
        """Validates the given data against the DAG ID rule."""
        dag_id = data.get("dag_id", "")
        return isinstance(dag_id, str) and len(dag_id) > 0


class AirflowTaskIdRule(Rule):
    """Concrete rule that checks if the Task ID is valid."""

    def validate(self, data: dict) -> bool:
        """Validates the given data against the Task ID rule."""
        task_id = data.get("task_id", "")
        return isinstance(task_id, str) and len(task_id) > 0


class KafkaTopicRule(Rule):
    """Concrete rule that checks if the Kafka topic is valid."""

    def validate(self, data: dict) -> bool:
        """Validates the given data against the Kafka topic rule."""
        topic = data.get("topic", "")
        return isinstance(topic, str) and len(topic) > 0


class KafkaPartitionRule(Rule):
    """Concrete rule that checks if the Kafka partition is valid."""

    def validate(self, data: dict) -> bool:
        """Validates the given data against the Kafka partition rule."""
        partition = data.get("partition", None)
        return isinstance(partition, int) and partition >= 0


def client_code(rule: Rule, data: dict) -> None:
    """Client code that uses the rule to validate the given data."""
    if rule.validate(data):
        print("Data is valid.")
    else:
        print("Data is invalid.")


if __name__ == "__main__":
    airflow_data = {"dag_id": "example_dag", "task_id": "example_task"}
    kafka_data = {"topic": "example_topic", "partition": 0}
    data = airflow_data | kafka_data

    airflow_rules = Rules()
    airflow_rules.add(AirflowDAGIdRule())
    airflow_rules.add(AirflowTaskIdRule())

    kafka_rules = Rules()
    kafka_rules.add(KafkaTopicRule())
    kafka_rules.add(KafkaPartitionRule())

    rules = Rules()
    rules.add(airflow_rules)
    rules.add(kafka_rules)

    client_code(rules, data)
    client_code(rules, {})
