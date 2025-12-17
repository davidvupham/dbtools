# Modules and Packages

## Modules

A **module** is simply a Python file (`.py`).

```python
# my_module.py
def greet():
    print("Hello")
```

Importing:

```python
import my_module
my_module.greet()

from my_module import greet
greet()
```

## Packages

A **package** is a directory of modules containing a special `__init__.py` file.

```
my_package/
    __init__.py
    module1.py
    module2.py
```

### The `__init__.py` file

This file is executed when the package is imported. It's often used to export key functions.

```python
# __init__.py
from .module1 import func1
from .module2 import func2

__all__ = ['func1', 'func2']
```

## Best Practices

1. **Absolute Imports**: `from my_package.core import utils`
2. **Avoid `import *`**: It pollutes the namespace.
3. **Circular Imports**: Avoid modules importing each other.
