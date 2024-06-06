# pydeco
Usefull Decorators!

Need: Pandas

```py
from pydeco import ProgrammAnalyzer

az = ProgrammAnalyzer()
em = EmailEventTrigger("host", "username", "password", ["test@google.de"])
@az.analyze
def test():
  return 2*2

print(az.get_report())

@event("Function", "Action on function")
def test2():
  return 2*2

```
Made to Teach!
