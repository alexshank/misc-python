# imported modules
from list import List
from enum import Enum

# model of the data stored in the simple
# manager (leverages ListItem class)
class Model:
    # constructor
    def __init__(self):
        self.status = Status.Initialized
        self.lists = [List('L1'), List('L2')]
        self.active_list_index = 0

    # return sidebar names
    def getLists(self):
        list_titles = []
        for item in self.lists:
            list_titles.append(item.title)
        return list_titles 

    # return items of list given list name
    def getListItemsByTitle(self, title):
        list_items = []
        for list_ in self.lists:
            if list_.title == title:
                for item in list_.items:
                    list_items.append(item)
                break
        return list_items

    # return items of a list given list index
    def getListItemsByIndex(self, index):
        list_items = []
        for item in self.lists[index].items:
            list_items.append(item)
        return list_items

    # return items of the currently active list
    def getActiveListItems(self):
        return self.getListItemsByIndex(self.active_list_index)

    # add a list to the model
    def addList(self, tokens):
        self.lists.append(List(' '.join(tokens)))

    # add an item to a list given the list's index
    def addItemByListIndex(self, list_index, date, title):
        self.lists[list_index].addItem(date, title)

 # enums for the current model status
class Status(Enum):
    Initialized = 1
    Unsaved = 2
    Saved = 3
    Error = 4
    Loaded = 5
