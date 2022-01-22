Last Modified: 1.5.0

## Store

The Store class serves to provide access to a nested widget's state, variables, and methods to another nested widget in a different branch or tree. Use Store if a widget requires access to another widget's state or methods instead of passing instance variables through multiple widgets.

Ex.

```
|-ExampleWidgetContainer
  |-Toolbar
    |-ToolbarNested
  |-NestedWidget
    |-AnotherNestedWidget
```

```
# Bad

class ExampleWidgetContainer():
  def __init__(self):
    self.toolbar = Toolbar()
    self.nested_widget = NestedWidget(passed_var=self.toolbar.passed_var)
......
class Toolbar():
  def __init__(self):
    self.toolbar_nested_widget = ToolbarNested()
    self.passed_var = self.toolbar_nested_Widget.send_this_var_up
......
class NestedWidget():
  def __init__(self, passed_var):
    self.another_nested_widget = AnotherNestedWidget(passed_var=passed_var)

# Good

class ToolbarNested():
  def __init__(self):
    Store.dispatch('helpful_var', helpful_var)
......
class AnotherNestedWidget():
  def __init__(self):
    Store.subscribe(self, 'helpful_var', 'is_modal_open')
```

## Class Variables

**Do not modify any class variables directly.**

### state[dict]

---

Keeps track of variables that have been dispatched to the Store. The initial value is in the initial_state variable initialized at the top of `store.py`. Please modify initial_state when adding a key to the Store to prevent crashes.

### subscriptions[dict]

---

Keeps track of widgets that have called subscribe().

Structure

```
state = {'key_a': 'a', 'key_b': 'b'}

{
  'key_a': [SubscribedWidget1, SubscribedWidget2,..., SubscribedWidget9],
  'key_b': [SubscribedWidget49]
}

```

## Class Methods

### dispatch(key[str], payload[any]) # => None

---

Dispatches a new value to state[key]. Any widget that has subscribed to state[key] receives the updated value.

```
# state = {}
Store.dispatch("refresh_func", self.refresh)
# state = {"refresh_func": <function <refresh> at 0xaddress> }
# Any widgets that had subscribed to the "refresh_func" key get the previous value overridden.
```

### subscribe(caller[object], key[str], caller_var[str]) # => Store.state[key]

---

Returns the current value of Store.state[key]. Any number of widgets can be subscribed to a key.

How it works:

1. widget_a calls Store.subscribe and receives the current value of Store.state['example_var'] and saves it as self.caller_var.

2. widget_b dispatches a value to Store.state['example_var'].

3. Store sets widget_a.caller_var to equal the updated value of Store.state['example_var'].

```
class ExampleWidget():
  def __init__(self):
    self.well_named_var = Store.subscribe(self, 'store_var', 'well_named_var')
```

### unsubscribe(caller[object], from_key[str]=None) # => None

---

Removes caller from all subscriptions if from_key is falsey, otherwise unsubscribes caller from Store.state[from_key].

```
Store.unsubscribe(self, 'active_widget')
```

### select(selector[lambda, function]) # => dict

---

Returns the current state. Used to retrieve the current value of a key without subscribing.

```
def example_func(self):
  if Store.select(lambda state: state['current_page']) == 'image_index':
    self.hello_world_popup()
```
