# <img src="https://raw.githubusercontent.com/nateshirley/codespeak-assets/main/speaker.png" style="zoom:17%;" /> Codespeak

Write python in natural language. Maintain complete interop with your existing stack and preserve real-time, deterministic execution.

## Installation

`pip install codespeak` or `poetry add codespeak`

See [getting started](#getting-started) for API key config.

## Usage

Declare a function with the `@codespeak` decorator and describe its goal with a docstring. Then, call the function:

```python
from codespeak import codespeak

@codespeak
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

@codespeak
def orders_for_user_since_date(session: Session, user: User, since_date: datetime) -> List[Order]:
  """return all of the orders for the user placed after the given date"""
```

When compared to the first example, this function requires more advanced logic, but its type hints contain much richer information about the data that the function will operate on.

To generate code for the above function, Codespeak will navigate through the function's types and use them to understand how to accomplish its goal. Here, the types should contain plenty of information to implement the function.

If using this function, simply declare it as shown above, and then call it.

### Maintain real-time, deterministic execution

The first time a Codespeak function is executed, the appropriate implementation is generated. From then on, the function is executed deterministically and in real-time.

Here's fizzbuzz in Codespeak:

```python
@codespeak
def fizzbuzz(limit: int) -> None:
  """
  Iterate from 1 to the limit.
  If the number is divisible by 3, print "Fizz".
  If the number is divisible by 5, print "Buzz".
  If the number is divisible by both 3 and 5, print "FizzBuzz".
  Otherwise, print the number.
  """
```

The first time fizzbuzz() is called, Codespeak will generate its implementation and execute it. When the function is called anytime thereafter, the current version is compared with the previous using a checksum.

When changes are detected, new code is generated and executed. Otherwise, the previous implementation is executed in real-time.

In production environments, Codespeak assumes all functions are unchanged and executes them with near-zero overhead—on an M2 Mac, you would need to call a Codespeak function about 13 million times to generate 1 second of latency.

To configure production settings, use an environment variable `ENVIRONMENT=PROD` or call `codespeak.set_environment("prod")`

### Use tests to guarantee execution properties

Alongside type hints, tests allow Codespeak to guarantee specific properties in your functions.

When writing code for a function with tests, Codespeak will rewrite and execute its code until the tests pass.

To attach a test to a function, simply assign it with the function's built-in "assign_pytest_function" method:

```python
@codespeak
def add_two(x: int, y: int) -> int:
  """add two numbers together"""

def test_add_two():
  assert add_two(1, 3) == 4

add_two.assign_pytest_function(test_add_two)

```

Currently, Codespeak receives tests exclusively in the form of pytest functions.

### Access and manipulate generated logic in your file system

When Codespeak implements your functions, they're written to the file system in a `codespeak_inferred/` directory under the same hiearchy as they are defined.

Each function is implemented in its own file, named after the function. To view or edit logic for a function, simply visit the file at [function_name].

## Why would I use this?

#### The right syntax is whatever makes sense to you.

Stop crawling your memory for syntax and data structures. Whatever makes sense to you, just works, so you can stay focused on your program's goals.

#### Choose the best-fit abstraction for your work.

Maintain the flexibility to delegate as much—or as little—programming as you'd like to an LLM, and adjust your choice on a case-by-case basis. Let a model control an entire endpoint, or a single SQL query.

#### Always know what you wrote and what you didn't.

Stop digging through blocks of code that Copilot wrote last month and sending them to ChatGPT. Let your code clarify your responsibilities.

#### Modify AI-generated code with simple comment revisions.

With Codespeak, everything that's required to generate new code for your existing programs is declared in your codebase. This means your codegen can be immediately re-produced or updated on any machine, simply by adjusting your code comments.

#### Accomplish more with your programs in fewer declared-lines.

Compress your exposure to program logic. Fewer lines means fewer files and fewer functions to manage, so you can stop wasting your time re-organzing and re-naming. Stay focused on your program's goals.

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
