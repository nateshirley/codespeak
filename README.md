





# Codespeak

Write python logic in natural language.





To use Codespeak, declare a function and describe its goal with a docstring. Then, call the function. Let's look at a simple example:

```python
@codespeak()
def add_two(x: int, y: int) -> int:
  """add two numbers together"""
  
 
result = add_two(1, 3) 
print(result) # output: 4  
```

Codespeak uses a function's declaration to understand its intent and write an appropriate implementation. When the function is called, the generated implementation is executed.





With Codespeak, proper type hints expand the reliability and capability of functions. Let's look at a more complex example:

```python
from sqlalchemy.orm.session import Session
from datetime import datetime
from my_models import User, Order

@codespeak()
def orders_for_user_since_date(session: Session, user: User, since_date: datetime) -> List[Order]:
  """return all of the orders for the user placed after the given date"""


```

When compared to the first example, this function requires more advanced logic, but its type hints contain much richer information about the data that the function is operating on. To write an implementation for this function, Codespeak will navigate through its types and use them to understand how to accomplish the function's goal. Here, the types should contain plenty of information to generate an appropriate function body. 

To use this function, simply declare it as shown above, and then call it.





### Determinism and real-time execution

As long as a function's declaration remain constant, it will be executed deterministically and in real-time. 



Here's fizzbuzz in Codespeak.

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

The first time fizzbuzz() is called, Codespeak will generate its implementation and execute it. When the function is called anytime thereafter, a checksum of the declaration in the project's filesystem is compared with the current declaration. If the declaration has changed, new code will be generated and executed. Otherwise, the previous implementation is immediately retrieved and re-used.

In production environments, Codespeak assumes all functions have unchanged, existing logic. Therefore, they are executed with near-zero overhead. 





### Testing

Besides type hints, tests can be used to ensure accuracy of codegen.

....pass tests into decorator...codegen runs tests and re-uses the results to generate new code until the tests are satisfied









### Why

- It's easier to write english than code

- Explicitly pairing prompt-context to programming logic ensures that any information used to create a block of code is easily accessible and editable in the future
- Programmers have full control over the quantity of work they are abstracting to an LLM

- Automated file management



















At run-time, the generated function body is automatically executed in-place of the em



 When a declaration changes, Codespeak generates new logic to satisfy it. Otherwise, 







- Deterministic
- Zero-latency & minimal overhead
- No untrusted execution with exec()







