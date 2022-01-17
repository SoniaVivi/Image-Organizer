## Getting Started

vivid_GUI is built using Kivy. Please refer to the [Kivy Documentation](https://kivy.org/doc/stable/gettingstarted/intro.html) for any general Kivy questions.

Vivid is made of two main parts: vivid handles all database operations and vivid_GUI handles all user interactions and inputs. vivid_GUI is restricted from implementing any methods or operations that directly uses the database. vivid_GUI can indirectly utilize the database by using classes in the vivid module, such as TagController or ImageController. It is furthermore restricted from utilizing most DatabaseController methods, please refer to `/vivid/docs/database_controller.md` for further details.

## Styling

Kivy styles are found in `/vivid.kv` or included in the widget class itself.

## Widget Layout

Not an all encompassing list. Excludes base Kivy widgets.

```
|-vivid.kv
|-Workspace
  |-Toolbar
    |-ToolbarSearch
    |-ToolbarModal
    |-PreferencesButton
    |-StatsButton
  |-Sidebar
    |-SidebarPreview
    |-SidebarField
      |-EditField
      |-SidebarText
  |-ImageIndexContainer
    |-ImageIndex
      |-Thumbnail
      |-ContextMenu
        |-AddTagPopup
        |-RemoveTagPopup
    |-TagList
      |-TagListChild
      |-ContextMenu
```

## Utility Classes

- Store: Stores "trigger" functions, globally accessed data, and subscriptions.

- ContextMenu: Adds a right click menu to widgets.

- SelectBehavior and SelectChildBehavior: Selects and highlights children for use by descendants.

- Any class present in vivid.
