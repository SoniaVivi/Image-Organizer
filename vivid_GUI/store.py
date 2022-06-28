initial_state = {
    "use_sort_from_config": lambda: None,
    "search_images": lambda *args, **kwargs: None,
    "set_preview_image": lambda: None,
    "update_thumbnail": lambda: None,
    "rename_image": lambda: None,
    "set_index": lambda: None,
    "current_index_child": "",
    "searchbar": lambda: None,
    "refresh": lambda: None,
    "active_widget": "workspace",
}


class Store:
    state = initial_state
    subscriptions = {}

    @classmethod
    def dispatch(self, key, payload):
        print(f"Dispatch {payload} => {key}")
        Store.state[key] = payload
        if key in Store.subscriptions:
            for subscription in Store.subscriptions[key]:
                subscription["caller"].__dict__[
                    subscription["caller_var"]
                ] = Store.state[key]

    @classmethod
    def subscribe(self, caller, key, caller_var):
        if key not in Store.subscriptions:
            Store.subscriptions[key] = []
        Store.subscriptions[key].append({"caller": caller, "caller_var": caller_var})
        if key in Store.state:
            print(f"Subscribe => {key} by {caller}")
            return Store.state[key]

    @classmethod
    def unsubscribe(self, caller, from_key=None):
        if from_key:
            Store.subscriptions[from_key] = [
                x for x in Store.subscriptions[from_key] if x["caller"] != caller
            ]
            return
        for key in Store.subscriptions:
            keep = []
            for subscription in Store.subscriptions[key]:
                if subscription["caller"] != caller:
                    keep.append(subscription)
            Store.subscriptions[key] = keep

    @classmethod
    def select(self, selector):
        return selector(Store.state)
