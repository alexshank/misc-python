#!/usr/bin/python3
# imported modules
from tkinter import *       # gui library
from tkinter import filedialog       # gui library
from controller import Controller # gui controller logic

# global variables
window = Tk() 
status_bind = StringVar()
list_area = Frame(window)
item_area = Frame(window)
console = Entry(window) 

# create instance of controller class
controller = Controller()

# setup program GUI
def main():
    # create main window
    window.title('List Manager')
    window.geometry('800x600')
    window.resizable(0, 0)

    # create sidebar area
    sidebar_title = Label(window, text='Lists')
    sidebar_title.grid(row=0, column=0)
    list_area.grid(row=1, column=0, sticky=N+S+E+W)

    # create content area 
    content_title = Label(window, text='Items')
    content_title.grid(row=0, column=1)
    item_area.grid(row=1, column=1, columnspan=2, sticky=N+S+E+W)
    item_area.bind('<<ListboxSelect>>', itemClick)
  
    # create status area
    status_label = Label(window, textvariable=status_bind, fg='white', bg='black')
    status_bind.set('Status')
    status_label.grid(row=0, column=2, sticky=N+S+E+W)

    # create user input area
    console.grid(row=2, columnspan=3, sticky=N+S+E+W) 
    window.bind('<Return>', consoleEntry)

    # configure grid
    window.columnconfigure(0, minsize=200)
    window.columnconfigure(1, minsize=300)
    window.columnconfigure(2, minsize=300)
    window.rowconfigure(0, minsize=25)
    window.rowconfigure(1, minsize=550)
    window.rowconfigure(2, minsize=25)

    # create menu bar and menu dropdown
    menubar = Menu(window)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open", command=openFile)
    filemenu.add_command(label="Save", command=saveFile)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=window.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    window.config(menu=menubar)

    # start the GUI 
    draw()
    mainloop()

# handle when the user enters a command
def consoleEntry(self):
    for slave in item_area.pack_slaves():
        slave.destroy()
    #controller.parseCommand(console.get())
    #draw()

# refresh the GUI with updated data model
def draw():
    drawLists()
    drawItems()
    status_bind.set(controller.getDisplayStatus())   # display updated status
    console.delete(0, END)          # clear user input area

# display sidebar items
def drawLists():
    i = 0
    for item in controller.getLists():
        prefix = '-' + '{:02}'.format(i) + ' '
        i = i + 1
        list_grid = Frame(list_area, bg="yellow")
        list_grid.pack(fill="x")
        list_grid.columnconfigure(0, weight=1)
        list_grid.columnconfigure(1, weight=10)
 
        label1 = Label(list_grid, text=prefix)
        label1.grid(row=0, column=0, sticky=N+S+E+W)
        label2 = Label(list_grid, text=item)
        label2.bind("<Button-1>", itemClick)
        label2.grid(row=0, column=1, sticky=N+S+E+W)

# display main content items
def drawItems():
    # get active list name and clear main content area
    items = controller.getFormattedItemStrings("L1")

    # add formatted string to main content area
    for item in items:
        item_grid = Frame(item_area, bg="yellow")
        item_grid.pack(fill="x")
        item_grid.columnconfigure(0, weight=1)
        item_grid.columnconfigure(1, weight=10)
        item_grid.columnconfigure(2, weight=5)
        item_grid.columnconfigure(3, weight=1)
        item_grid.columnconfigure(4, weight=1)
 
        item = item.split(" ")
        label1 = Label(item_grid, text=item[0])
        label1.grid(row=0, column=0, sticky=N+S+E+W)
        label2 = Label(item_grid, text=item[1])
        label2.bind("<Button-1>", itemClick)
        label2.grid(row=0, column=1, sticky=N+S+E+W)
        label3 = Label(item_grid, text=item[2])
        label3.grid(row=0, column=2, sticky=N+S+E+W)
        label4 = Label(item_grid, text=item[3])
        label4.grid(row=0, column=3, sticky=N+S+E+W)
        label5 = Label(item_grid, text=item[4])
        label5.grid(row=0, column=4, sticky=N+S+E+W)


# get save file location
def saveFile():
    window.filename = filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes=(('text files', '*.txt'),))
    controller.save_action(window.filename)

# get open file location
def openFile():
    window.filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes=(('text files', '*.txt'),))
    controller.open_action(window.filename)
    draw()

# handle sidebar click
def listClick(event):
    active_list_index = int(event.widget.curselection()[0])
    controller.setActiveListIndex(active_list_index)
    drawItems()

# handle content click
def itemClick(event):
    print("yes")
    #w = event.widget
    #contentIndex = int(w.curselection()[0])
    #contentValue = w.get(contentIndex)

# start the program by running the main function
if __name__ == '__main__':
    main()