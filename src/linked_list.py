
class Node(object):
    def __init__(self, val):
        self.val = val
        self.next = None

    def remove_next(self):
        self.next = self.next.next

    def set_next(self, val):
        self.next = Node(val)
