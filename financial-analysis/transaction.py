# imports
import datetime 
from dateutil.parser import parse
from constants import ACCOUNTS, CATAGORIES

# represents a single transaction recorded during the year
class Transaction():
    """
    Constructor
    """
    def __init__(self, line):
        # get each item of the CSV line
        items = line.split(",")

        # set properties
        self.date = __parseDate(self, items[0])
        self.amount = __parseDollarAmount(self, items[1])       # clean any dollar signs from amount
        self.account = __validateAccountType(self, items[2])        # make sure account type is valid     
        self.balance = __parseDollarAmount(self, items[3])      # clean any dollar signs from amount
        # TODO could be better as a tuple
        self.main_cat = __parseMainCatagory(self, items[4])
        self.sub_cat = __parseSubCatagory(self, items[5])
        self.from_venmo = items[6]
        self.to_venmo = items[7]
        self.details = ",".join(items[8:])          # make details a single string

    """
    Public Methods
    """
    # print all properties
    def print(self):
        print("Date   : {}".format(self.date))
        print("Amount : {}".format(self.amount))
        print("Account: {}".format(self.account))
        print("Balance: {}".format(self.balance))
        print("Main   : {}".format(self.main_cat))
        print("Sub    : {}".format(self.sub_cat))
        print("From   : {}".format(self.from_venmo))
        print("To     : {}".format(self.to_venmo))
        print("Details: {}".format(self.details))

    """
    Private Methods
    """
    # parse date object from date string
    def __parseDate(self, date_str):
        try:
            date_obj = parse(date_str)
        except:
            print("Error parsing date of transaction")
        return date_obj

    # check that a valid account type is listed
    def __validateAccountType(self, accountType):
        if accountType not in ACCOUNTS:
            raise Exception("Unknown account type of {}!".format(account))
        return accountType

    # clean any numbers of incorrect prefixes
    def __parseDollarAmount(self, str):
        new_str = "" 
        for i in range(len(str)):
            if str[i].isdigit() or str[i] == "-" or str[i] == ".":
                new_str += str[i]
        return new_str

    # validate the main catagory
    def __parseMainCatagory(self, main_catagory):
        main_catagories = list(CATAGORIES.keys())
        if main_catagory not in main_catagories:
            print("Main Catagories")
            for catagory in main_catagories:
                print(catagory)
            print("Given: " + main_catagory)
            main_catagory = input("New: ")
        return main_catagory

    # validate the sub catagory
    def __parseSubCatagory(self, sub_catagory):
        sub_catagories = CATAGORIES.get(self.main_cat)
        if sub_catagory not in sub_catagories:
            print("Sub Catagories")
            for catagory in sub_catagories:
                print(catagory)
            print("Given: " + sub_catagory)
            sub_catagory = input("New: ")
        return sub_catagory