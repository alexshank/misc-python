from datetime import date, timedelta

# -----CONSTANTS-----
valid_commands = ['add', 'del', 'edit', 'date', 'priority']
weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

# -----PARSING FUNCTIONS-----
# parse a given command
def parse(model, raw_string):
    # break up input
    tokens = raw_string.split(' ')
    index = tokens[0]
    command = tokens[1].lower()
    args = tokens[2:]

    # check if list, item, or special index 
    isItemIndex = (index[0] != '-')

    # branches to run each command
    if command == 'add' and not isItemIndex:
        model = parseAdd(model, index, args)
    elif command == 'del':
        return
    elif command == 'edit':
        return
    elif command == 'date' and isItemIndex:
        return
    elif command == 'priority' and isItemIndex:
        return
    else:
        print('invalid command')

    # return the modified model
    return model

# parse the add command
def parseAdd(model, index, args):
    # $ index for adding new list
    if index[0] == '$':
        model.addList(args)
    # add item to given list index
    else:
        date = createDateObject(args[0])
        index = int(index[1:])
        model.addItemByListIndex(index, date, ' '.join(args[1:]))
    return model
            

# -----UTILITY FUNCTIONS-----
# ensure that passed in index is valid
def validateIndex(model, isListIndex, index):
    # get max list or item index
    max_index = 0
    if isListIndex:
        max_index = len(model.getLists()) - 1
    else:
        max_index = len(model.getActiveListItems()) - 1

    # check that index is within [0, max_index)
    if index > max_index or index < 0:
        raise Exception

# create date object from given arg
def createDateObject(date_arg):
    # weekday given (monday, tuesday, etc)
    temp_date = date_arg.lower()
    if (temp_date in weekdays):
        temp_date = date(temp_date)            
    # relative date given (+/-days)
    elif len(temp_date) <= 3:
        try:
            relative_days = int(temp_date)
            temp_date = date.today()
            delta = timedelta(days=relative_days)
            temp_date = temp_date + delta
        except:
            print('not a relative date')
    # absolute date given (mm/dd/yyyy)
    elif len(temp_date) == len('mm/dd/yyyy'):
        try:
            day = int(temp_date[0:1])
            month = int(temp_date[3:4])
            year = int(temp_date[6:9])
            temp_date = date(year, month, day)
        except:
            print('not an absolute date')
    else:
        temp_date = date.today()
        print('failed to parse date argument')

    return temp_date
