from datetime import date

class Item():
    # constructor
    def __init__(self, pTitle, date=date.today()):
        self.title = pTitle
        self.details = ''
        self.date = date
        self.priority = 0

    # return string to display in content area
    def getDisplayString(self, index, maxStringLength):
        # get date difference
        diff = (self.date - date.today()).days

        # return the formatted string
        returnStr = '{:02}'.format(index) + ' ' + self.title.ljust(maxStringLength) + ' '
        return returnStr + self.date.isoformat() + ' ' + str(diff)