



# <img src="https://raw.githubusercontent.com/nateshirley/codespeak-assets/main/speaker.png" style="zoom:17%;" /> Codespeak

Codespeak lets you write python in natural language while maintaining complete interop with your existing stack and preserving real-time, deterministic execution.



## Installation

`pip install codespeak` or `poetry add codespeak`

See [getting started](#getting-started) for API key config.

## Usage

Declare a function with the `@codespeak()` decorator and describe its goal with a docstring. Then, call the function:

```python
from codespeak import codespeak

@codespeak()
def add_two(x: int, y: int) -> int:
  """add two numbers together"""
  
 
result = add_two(1, 3) 
print(result) # output: 4  
```

Codespeak uses function declarations to understand program intent and write corresponding implementations. When Codespeak functions are called, their generated implementations are executed.

### Use type hints to create reliable, highly-capable functions

Proper type hints allow Codespeak to write more complex code inside your existing projects. Let's look at another example:

```python
from sqlalchemy.orm.session import Session
from datetime import datetime
from my_models import User, Order

@codespeak()
def orders_for_user_since_date(session: Session, user: User, since_date: datetime) -> List[Order]:
  """return all of the orders for the user placed after the given date"""
```

When compared to the first example, this function requires more advanced logic, but its type hints contain much richer information about the data that the function will operate on. 

To generate code for the above function, Codespeak will navigate through the function's types and use them to understand how to accomplish its goal. Here, the types should contain plenty of information to implement the function.

If using this function, simply declare it as shown above, and then call it.

### Maintain real-time, deterministic execution

When Codespeak detects a new and/or different function, it writes new code for it. Otherwise, functions are executed deterministically and in real-time.

Here's fizzbuzz in Codespeak:

```python
@codespeak()
def fizzbuzz(limit: int) -> None:
  """
  Iterate from 1 to the limit.
  If the number is divisible by 3, print "Fizz".
  If the number is divisible by 5, print "Buzz".
  If the number is divisible by both 3 and 5, print "FizzBuzz".
  Otherwise, print the number.
  """
```

The first time fizzbuzz() is called in your project, Codespeak will generate its implementation and execute it. When the function is called anytime thereafter, the current version is compared with the previous using a checksum. 

When changes are detected, new code is generated and executed. Otherwise, the previous implementation is executed in real-time.

In production environments, Codespeak assumes all functions are unchanged and executes them with near-zero overhead.

To configure production settings, use an environment variable `ENVIRONMENT=PROD` or call `codespeak.set_environment("prod")`

### Use tests to guarantee execution properties

Alongside type hints, tests allow Codespeak to guarantee specific properties in your functions.

When writing code for a function with tests, Codespeak will rewrite and execute its code until the tests pass.

To apply a test to a function, simply pass it into the `@codespeak()` decorator as an argument:

```python
def test_add_two():
  assert add_two(1, 3) == 4
 
@codespeak(test_add_two)
def add_two(x: int, y: int) -> int:
  """add two numbers together"""
```

Currently, Codespeak tests are run exclusively as pytest functions.

### Access and manipulate generated logic in your file system

When Codespeak implements your functions, they are written to the file system in a `codespeak_generated/` directory under the same hiearchy as they are defined.

Each function is implemented in its own file, named after the function. To view or edit logic for a function, simply visit the file at [function_name].



## Why would I use this?

- English is easy to write
- Explicitly pairing prompt-context to programming logic ensures that any information used to create a block of code is easily accessible and editable in the future
- Programmers have full control over the quantity of work they are abstracting to a language-model
- Automated file management



## Getting started

Codespeak needs to be configured with an OpenAI API key (access your keys [here](https://platform.openai.com/account/api-keys)). 

The library will automatically use an environment variable `OPENAI_API_KEY` if one exists:

```python
export OPENAI_API_KEY='sk-...'
```

Otherwise, set it explicitly with `codespeak.set_openai_api_key()`:

```python
import codespeak

codespeak.set_openai_api_key("sk-...")
```



