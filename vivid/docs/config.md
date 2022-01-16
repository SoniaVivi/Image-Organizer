# class Config

Config handles user settings and persistent runtime settings.

Current options:

- image_index
  - sort[str]. Default 'ASC'. Possible: 'DESC' or 'ASC'.
- image_controller
  - logging[str]. Default False. Possible: 'True' or 'False'.

## Setting

### set(section[str], attribute[str], value[str]) # => None

---

Sets section attribute to value.

## Reading

### read(section[str], attribute[str]) # => str

---

Returns section attribute value.
