from transaction import Transaction

"""
parsing input data
"""
# open the CSV file and get all lines
file = open("data.csv")
lines = file.readlines()
file.close()

# get the headers from the first line
headers = lines[0].split(",")

# create transaction objects
transactions = []
try:
    # create transacation objects (exclude first header line)
    for line in lines[1:]:
        transaction = Transaction(line)
        transactions.append(transaction)
except Exception as e:
    print(e)
    
"""
analyzing parsed data
"""
