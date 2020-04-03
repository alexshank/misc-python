from item import Item

class List():
    # constructor
    def __init__(self, pTitle):
        # keep updated indices for each item
        self.title = pTitle
        self.items = [Item('item one'), Item('item two')]
        #self.max_desc_len = 0

    # add an item to the list
    def addItem(self, date, title):
        self.items.append(Item(title, date))
