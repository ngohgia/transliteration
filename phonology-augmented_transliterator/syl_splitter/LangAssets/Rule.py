class Rule:
  def __init__(self):
    self.prev = [];
    self.curr = [];
    self.next = [];

    self.role = [];

  def __eq__(self, other):
    if isinstance(other, Rule):
      if self.prev == other.prev and self.curr == other.curr and self.next == other.next and self.role == other.role:
        return True
      else:
        return False
    return NotImplemented

  def __ne__(self, other):
    result = self.__eq__(other)
    if result is NotImplemented:
        return result
    return not result

  def to_str(self):
    return str(self.prev) + " | " + str(self.curr) + " | " + str(self.next) + " => " + str(self.role)