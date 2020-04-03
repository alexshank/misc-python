# module for getting command line arguments
import sys

# open file and create variables
file = open(sys.argv[1])
line = file.readline()
line_list = []

# get all lines from file
while line:
    words = line.split()
    line_list.append(words)
    line = file.readline()

# close file and filter blank data
file.close()
line_list = list(filter(None, line_list))

# print new CSV data to file
new_file = open(sys.argv[2], "w+")
for line in line_list:
    # get relevant data from lines
    date = "{} {}".format(line[0], line[1])
    money = line[-1]
    description = " ".join(line[4:-1])

    # create new line with retrieved data
    new_line = "{},{},Discover 9225,,,,,,{}".format(date + " 2019", money, description)
    new_file.write("{}\n".format(new_line))

# close newly created csv file
new_file.close()
