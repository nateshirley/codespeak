# <img src="https://raw.githubusercontent.com/nateshirley/codespeak-assets/main/speaker.png" style="zoom:17%;" /> Codespeak

Codespeak is a python framework for writing *Inferred Functions*—functions that implement their own logic. 

## Installation

`pip install codespeak` or `poetry add codespeak`

See [getting started](#getting-started) for API key config.

## Usage

Declare a function with Codespeak's `@infer` decorator and describe its goal with a docstring. Then, call the function:

```python
from codespeak import infer

@infer
def add_two(x: int, y: int) -> int:
  """add two numbers together"""
  
 
result = add_two(1, 3) 
print(result) # output: 4  
```

Inferred functions understand your program's goals and generate logic to accomplish them. When inferred functions are called, their generated logic is executed.

### Use type hints to write reliable, highly-capable functions

Type hints are one important way that data structures can be made available to inferred functions. Let's look at another example.

```python
from sqlalchemy.orm.session import Session
from datetime import datetime
from my_models import User, Order
from typing import List

@infer
def orders_for_user_since_date(session: Session, user: User, since_date: datetime) -> List[Order]:
  """return all of the orders for the user placed after the given date"""
```

Relative to the types in the first example, this function's types contain much more complex data structures. These data structures give Codespeak the information it needs to make a more advanced inference for the function.

To use this function, simply declare it as shown above, then call it.

### Add resources to your functions with Frames

Every inferred function has a Frame. Frames hold resources used to make inferences.

The types in a function's declaration are always bundled to its Frame. For the `orders_for_user_since_date` function shown above, Session, User, datetime, List, and Order would be automatically added to the function's frame at import time.

In many cases, function declarations on their own provide enough information for Codespeak to make performant inferences.

However, sometimes you'll need to programmatically add resources to a function's frame. Let's look at a simple example where you might want to modify a function in a way that requires explicitly adding resources to its frame. 

```python
from codespeak import infer

class Order(Base):
  ...

class User(Base):
    ...
    latest_order_id = Column(Integer)
  
# performs as-is
@infer
def get_latest_order_for_user(session: Session, user: User) -> Order:
  """Find the latest order for the user and return it"""

# needs more resources
@infer
def get_latest_order_total_for_user(session: Session, user: User) -> int:
  """Find the latest order for the user and return the total price paid"""
```

In the first function, our inference will perform as intended. Codespeak will use the `latest_order_id` variable on User and the Order class in the function's return type to understand the Orders table and locate the appropriate order.

In the second function, the function's frame doesn't have access to the Order class, so the inference engine won't understand how to find the appropriate order. To fix this, the Order class needs to be explicitly added to the Function's frame.

```python
from codespeak import infer, Frame
...

@infer
def get_latest_order_total_for_user(session: Session, user: User) -> int:
  """Find the latest order for the user and return the total price paid"""
  frame = Frame.this()
  frame.add_type(Order)
```

`Frame.this()` can be used to get a function's frame from inside its body. Here, we get the frame and add the Order class. Now, our inference will work as intended.

### Use tests to guarantee execution properties on your functions

Alongside types, tests help Codespeak make more advanced inferences.

When making an inference for a function with tests, Codespeak will execute the function's tests and use the results to make new inferences until the tests pass.

As with types, tests are attached to an inferred function via the function's Frame.

```python
def test_add_two():
  assert add_two(1, 3) == 4
 
@infer
def add_two(x: int, y: int) -> int:
  """add two numbers together"""
  frame = Frame.this()
  frame.add_test_function(test_add_two)
```

Currently, Frames receive and execute tests in the form of pytest functions.

### Share resources across functions with module-level Frames

The types included in a Frame act as an inventory of resources for the function to use when writing its logic, they're not an instruction set. This means it's perfectly fine for a function to have types in its frame that aren't relevant to its logic—Codespeak will simply ignore them.

In some cases, one may choose to build a single set of resources and share it across several functions, letting Codespeak choose when to use them. For these cases, Codespeak offers module-level Frames.

```python
from codespeak import infer, Frame
from models.order import Order

# get the module's frame
module_frame = Frame.for_module(__name__)

# add types to it
module_frame.add_type(Order)
```

A module's frame is a parent of the Frames for each function in the module. Any resources added to a module's frame are availble to every function in the module.

### Easily check and edit inferences in your filesystem

Function inferences are written to the project's filesystem in a `codespeak_inferences/` directory, following the same hiearchy as the files in which they're defined.

Each function inference is written to its own file, named after the function. To view or edit an inference for a function, simply visit its file at [function_name].py.

### Maintain real-time, deterministic execution

The first time an inferred function is called, Codespeak makes an inference for it. From then on, Codespeak makes new inferences for your functions whenever their declarations or their resources change.

Otherwise, the function's previously generated inference is loaded and executed in real-time.

In production environments, Codespeak assumes all functions are unchanged and executes them with near-zero overhead—on an M2 Macbook Air, you would need to call a Codespeak function about 13 million times to generate 1 second of execution latency.

To configure production settings, use an environment variable `ENVIRONMENT=PROD` or call `codespeak.set_environment("prod")`

## Why would I use this?

#### The right syntax is whatever makes sense to you.

Stop crawling your memory for syntax and data structures. Whatever makes sense to you, just works, so you can stay focused on your program's goals.

#### Choose the best-fit abstraction for your work.

Maintain the flexibility to delegate away as much—or as little—logic as you'd like, and adjust your choice on a case-by-case basis. Let an inferred function control an entire endpoint, or just a single SQL query.

#### Always know what you wrote and what you didn't.

Stop digging through blocks of code that Copilot wrote last month and sending them to ChatGPT. Let your code clarify your responsibilities.

#### Modify AI-generated code with simple function revisions.

With Codespeak, everything that's required to generate new code for your existing functions is declared in your codebase. This means your codegen can be immediately modified on any machine, simply by adjusting your inferred functions.

#### Accomplish more with your programs in fewer declared-lines.

Compress your exposure to program logic. Fewer lines means fewer files and fewer functions to manage, so you can stop wasting time organzing and logic-tracing. Stay focused on your program's goals.

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

## Coming soon

1. Use functions as resources
2. Use modules as resources
3. Use modules as tests
