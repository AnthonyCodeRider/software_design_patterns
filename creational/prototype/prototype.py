"""Prototye pattern is available in Python out of the box"""

import copy


class Prototype:
    def __init__(self, value, deep=False):
        self.value = value
        self.deep = deep

    def clone(self):
        if self.deep:
            return copy.deepcopy(self)
        else:
            return copy.copy(self)


if __name__ == "__main__":
    original = Prototype([1, 2, 3], deep=True)
    clone = original.clone()

    print("Original:", original.value)  # Output: Original: [1, 2, 3]
    print("Clone:", clone.value)  # Output: Clone: [1, 2, 3]

    # Modifying the original's value to see if it affects the clone
    original.value.append(4)

    print("Original after modification:", original.value)  # Output: Original after modification: [1, 2, 3, 4]
    print("Clone after original modification:", clone.value)  # Output: Clone after original modification: [1, 2, 3]
