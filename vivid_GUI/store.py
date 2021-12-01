class Store():
  state = {'update_sort': lambda : None,
           'search_images': lambda *args, **kwargs: None,
           'set_preview_image': lambda : None,
           'update_thumbnail': lambda : None,
           'rename_image': lambda : None,
           'set_index': lambda : None,
           'current_index_child': "",
           'searchbar': lambda: None,
           'refresh': lambda: None,
           }
  subscriptions = {}

  def __init__(self):
    pass
  def dispatch(self, key, payload):
    print(f"Dispatch {payload} => {key}")
    Store.state[key] = payload
    if key in Store.subscriptions:
      for subscription in Store.subscriptions[key]:
        subscription['caller'].__dict__[subscription['caller_var']] = Store.state[key]

  def subscribe(self, caller, key, caller_var):
    if key not in Store.subscriptions:
      Store.subscriptions[key] = []
    Store.subscriptions[key].append({'caller': caller, 'caller_var': caller_var})
    if (key in Store.state):
      print(f"Subscribe => {key} by {caller}")
      return Store.state[key]

  def select(self, selector):
    return selector(Store.state)
