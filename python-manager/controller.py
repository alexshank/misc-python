# imported modules
from model import Model, Status
import pickle
from datetime import date
from c_parser import parse

# controller class for view (leverages Model class)
class Controller():
    # constructor
    def __init__(self):
        self.model = Model()

    # open function found in File menu
    def open_action(self, filename):
        print('Open: ' + filename)
        file = open(filename, 'rb')
        self.model = pickle.load(file)
        file.close()
        self.model.status = Status.Loaded

    # save function found in File menu
    def save_action(self, filename):
        print('Save: ' + filename)
        file = open(filename, 'wb')
        pickle.dump(self.model, file, pickle.HIGHEST_PROTOCOL)
        file.close()
        self.model.status = Status.Saved

    # parses all commands entered by the user
    def parseCommand(self, command):
        self.model = parse(self.model, command)

    # get the sidebar items
    def getLists(self):
        return self.model.getLists()

    # get the model status
    def getDisplayStatus(self):
        return self.model.status.name

    # set the currently active list index
    def setActiveListIndex(self, index):
        self.model.active_list_index = index

    # get formatted strings for content area
    def getFormattedItemStrings(self, list_title):
        # get longest title string (could store for efficiency later)
        maxTitleLength = 0
        for item in self.model.getListItemsByTitle(list_title):
            if len(item.title) > maxTitleLength:
                maxTitleLength = len(item.title)
        
        # return list of formatted strings
        formattedStrings = []
        i = 0
        for item in self.model.getListItemsByTitle(list_title):
            formattedStrings.append(item.getDisplayString(i, maxTitleLength))
            i = i + 1
        return formattedStrings

