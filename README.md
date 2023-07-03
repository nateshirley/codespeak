# <img src="https://raw.githubusercontent.com/nateshirley/codespeak-assets/main/speaker.png" style="zoom:17%;" /> Codespeak

Codespeak is a python framework for writing *inferred functions*—functions that implement their own logic. 

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

Inferred functions understand your program's goals and write logic to accomplish them. When inferred functions are called, their inferred logic is executed.

### Use type hints to write reliable, highly-capable functions.

Type hints are an important way that inferred functions receive data structures to use when making inferences. Let's look at an example.

```python
from sqlalchemy.orm.session import Session
from datetime import datetime
from my_models import User, Order
from typing import List

@infer
def orders_for_user_since_date(session: Session, user: User, since_date: datetime) -> List[Order]:
  """return all of the orders for the user placed after the given date"""
```

Although this function requires more advanced logic than `add_two`, it also includes much richer types. These types give the function the context it needs to make a more advanced inference.

To use this function, simply declare it as shown above, then call it.

### Frames help functions make performant inferences.

A program's types tell us a lot about its goals and abilities. For this reason, functions rely heavily on types to make performant inferences.

In Codespeak, types are associated with functions via Frames. Every inferred function has a frame, which holds the resources it uses to make inferences.

For the `orders_for_user_since_date` function shown above, Session, User, datetime, List, and Order would be automatically added to the function's frame at import time, since they're used in its declaration.

To access the frame for a function, call `Frame.this()` from inside its body.

```python
from codespeak import infer, Frame

@infer
def fizzbuzz(limit: int) -> None:
  """
  Implement fizzbuzz
  """
  frame = Frame.this()
```

### Use tests to guarantee execution properties on your functions.

Alongside types, tests help functions make more advanced inferences. To use tests, attach them to a function via its Frame.

```python
from codespeak import infer

def test_add_two():
  assert add_two(1, 3) == 4
 
@infer
def add_two(x: int, y: int) -> int:
  """add two numbers together"""
  frame = Frame.this()
  frame.add_test_function(test_add_two)
```

When a function with tests is making a new inference, it will execute its tests and rewrite its implementation until the tests pass.

Currently, Frames receive and execute tests in the form of pytest functions.

### Expand your Frames by programmatically giving them resources

You might also choose to programmatically manipulate frames in order to give a function types that aren't used in its declaration.

Below, you'll see a `get_latest_order_for_user` function that gets the latest order object associated with a `User`. Because the function's declaration includes `Order` and `User`, both types are natively included in its Frame. 

```py
...

class Order(Base):
  ...

class User(Base):
    ...
    latest_order_id = Column(Integer)
  
# performs as-is
@infer
def get_latest_order_for_user(session: Session, user: User) -> Order:
  """Find the latest order for the user and return it"""
```

For the inference above, the function will use the `latest_order_id` variable on `User` to understand the orders table and write logic that locates the appropriate order.

However, sometimes you'll need to add additional resources to a function's frame. Instead of returning the latest `Order`, let's say we want to return only the latest order's total price:

```python
@infer
def get_latest_order_total_price_for_user(session: Session, user: User) -> int:
  """Find the latest order for the user and return the total price paid"""
```

Now, the function's frame doesn't have access to the `Order` class, so it won't understand how to find the appropriate order. To fix this, add `Order` to the function's frame.

```python
from codespeak import infer, Frame
...

@infer
def get_latest_order_total_for_user(session: Session, user: User) -> int:
  """Find the latest order for the user and return the total price paid"""
  frame = Frame.this()
  frame.add_type(Order)
```

Frames highlight an important property of Codespeak—infererred functions are easy to edit and reproduce, because their source material is declared concretely in your project.

### Share resources across many functions with module-level Frames.

Frames hold an inventory of resources that functions use when inferring logic. It's perfectly fine for a function to have types in its frame that aren't relevant to its goals—Codespeak will simply ignore them.

In some cases, one may choose to build a single set of resources and share it across several functions. For these cases, Codespeak offers module-level Frames.

```python
from codespeak import infer, Frame
from models.order import Order

# get the module's frame
module_frame = Frame.for_module(__name__)

# add types to it
module_frame.add_type(Order)
```

A module's frame is a parent to the Frames of each function in the module. Any resources added to a module's frame are available to every function in the module.

### Easily check and edit inferences in your filesystem.

Function inferences are written to the project's filesystem in a `codespeak_inferences/` directory, following the same hiearchy as the files in which they're defined.

Each function inference is written to its own file, named after the function. To view or edit an inference for a function, simply visit its file at [function_name].py.

### Maintain near-zero overhead in production.

The first time an inferred function is called, it writes its own logic and executes it. From then on, functions make new inferences whenever their declarations or their resources change. Otherwise, the function's previously generated inference is loaded and executed in real-time.

In production environments, Codespeak assumes all functions are unchanged and executes them with near-zero overhead—on an M2 Macbook Air, you would need to call an inferred function about 13 million times to generate 1 second of execution latency.

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

1. Use functions and modules as resources
2. Use module-level tests
3. Gain more control over the programming style of your inferences
