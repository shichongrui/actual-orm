from typing import Generic, TypeVar, Dict, Optional

Val = TypeVar('Val')

class DotDict(Generic[Val]):
    _data: Dict[str, Val]
    def __init__(self, **kwargs: Val):
        # Initialize the dictionary with keyword arguments
        self.__dict__["_data"] = kwargs

    def __getitem__(self, key: str) -> Val:
        # Access items like a dictionary
        if key not in self._data:
            raise KeyError(f"Key '{key}' not found in DotDict.")
        return self._data[key]

    def __setitem__(self, key: str, value: Val) -> None:
        # Set items like a dictionary
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        # Delete items like a dictionary
        if key not in self._data:
            raise KeyError(f"Key '{key}' not found in DotDict.")
        del self._data[key]

    def __getattr__(self, key: str) -> Val:
        # Access attributes like dot notation
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key: str, value: Val) -> None:
        # Set attributes like dot notation
        if key == "_data":  # Avoid overriding internal data
            super().__setattr__(key, value)
        else:
            self._data[key] = value

    def __delattr__(self, key: str) -> None:
        # Delete attributes like dot notation
        if key in self._data:
            del self._data[key]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __repr__(self) -> str:
        return f"DotDict({self._data!r})"

    def __str__(self) -> str:
        return str(self._data)

    def get(self, key: str, default: Optional[Val] = None) -> Optional[Val]:
        # Provide a dictionary-like 'get' method
        return self._data.get(key, default)

    def keys(self):
        # Return dictionary keys
        return self._data.keys()

    def values(self):
        # Return dictionary values
        return self._data.values()

    def items(self):
        # Return dictionary items
        return self._data.items()
