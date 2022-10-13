Last Modified: 2.0-dev

# class Vivid Logger

Handles logging messages from vivid and vivid_GUI.

## General Usage

- Create Logger object with tag

1. Register reusable logger messages

2. Call registered messages in methods

--- or ---

1. Skip registering and write messages in methods

## Initializing

### init(tag[str]) # => None

---

Sets tag of logger object and sets all registered messages from VividLogger.tags[tag] as methods in format self.message_name

## Registering and Refreshing Messages

### register(name[str], message[str], \*\*kwargs) # => None

---

Sets message with name to VividLogger.tags[tag] and refreshes message for self.

Keyword Arguments:

- level[int] - Default 2 (warning).

### refresh(name[str]) # => None

---

Updates self.name to reflect that of VividLogger.tags[tag][name]

### refresh_all() # => None

---

Refreshes all registered messages.

## Printing

### write(message[str], level[int], \*text_args) # => None

---

Stores message inj history and potentially to the console if VividLogger.print_mode is equal to "console". All text arguments will be passed to message.

### print_history() # => None

---

Prints all messages from VividLogger.history[self.tag] to the console.

## Class Methods

### set_print_mode(mode[str]) # => None

---

Possible values are "history" and "console".
