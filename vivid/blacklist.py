class Blacklist():
  entry_node = None

  def add(self, path):
    path_segments = list(filter(lambda x: len(x), path.split('/')))
    if not Blacklist.entry_node:
      Blacklist.entry_node = BlacklistNode(path_segments[0])
      path_segments.pop(0)
    current_node = Blacklist.entry_node

    for segment in path_segments:
      if segment == current_node.text:
        if current_node.is_end_node:
          return
        else:
          current_node = current_node.find_or_add(segment)
    current_node.is_end_node = True

  def exists(self, path):
    if not Blacklist.entry_node:
      return False
    path_segments = list(filter(lambda x: len(x), path.split('/')))
    current_node = Blacklist.entry_node

    for segment in path_segments:
      if segment == current_node.text and current_node.is_end_node:
        return True
      current_node = current_node.find(segment)
      if not current_node:
        return False
    return current_node.is_end_node

  def bds(self):
    queue = [Blacklist.entry_node]
    while len(queue):
      node = queue.pop(0)

      for child in node.children.values():
        queue.append(child)

  def remove(self):
    pass

class BlacklistNode():
  def __init__(self, text, is_end_node=False):
    self.text = text
    self.children = {}
    self.is_end_node = is_end_node

  def find(self, text):
    return self.children[text] if text in self.children else None

  def find_or_add(self, text):
    if text not in self.children:
      self.children[text] = BlacklistNode(text=text)
    return self.children[text]
