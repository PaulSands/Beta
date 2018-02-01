from tkinter import *

def showTextFormatExamples(textBox):
    textBox.insert(END,"For tutorial on formatting output see:\n")
    textBox.insert(END,"http://www.python-course.eu/python3_formatted_output.php\n")
    textBox.insert(END,"Or:       https://pyformat.info\n\n")

    """
    General form of a format is:   "{" [name] ["!" conversion] [":" spec] "}"
    Each of the three parts is optional.
    Empty braces "{}" would simply point to an element in the format tuple

    """
    textBox.insert(END,"Examples of substitution\n")

    myString = "arg0 = {}, arg1 = {}, arg2 = {}     - simple substitution of elements".format("A","B","C") 
    textBox.insert(END,myString+"\n")

    myString = "arg0 = {0}, arg1 = {1}, arg2 = {2}     - use numbered elements".format("A","B","C") 
    textBox.insert(END,myString+"\n")

    myString = "arg2 = {2}, arg1 = {1}, arg0 = {0}     - use a different order".format("A","B","C") 
    textBox.insert(END,myString+"\n")

    myString = "arg1 = {1}, arg1 = {1}, arg1 = {1}     - use one variable many times".format("A","B","C") 
    textBox.insert(END,myString+"\n")

    x = 29
    y = 123.456
    z = 1.23456789
        
    myString = "arg0 = {0}, arg1 = {1}, x = {2}       - using a defined variable".format("A","B",x) 
    textBox.insert(END,myString+"\n")

    myList = ["Toronto", "Chicago", "New York"]
    myString = "My favorite city is {}     - using an element from list".format(myList[2]) 
    textBox.insert(END,myString+"\n")

    myString = "My favorite city is {[2]}     - alternative method of pointing to element".format(myList) 
    textBox.insert(END,myString+"\n")
        
    myString = "First name: {firstName}                - using keyword to substitute".format(firstName="Betty")
    textBox.insert(END,myString+"\n\n")

    textBox.insert(END,"Examples of formatting\n")
    myString = "y = {0:f}   print float (123.456) with default formating (6 decimal places)".format(y)         
    textBox.insert(END,myString+"\n")

    myString = "z = {0:f}     print float (1.23456789) wth default formating (note rounding)".format(z)         
    textBox.insert(END,myString+"\n")

    myString = "y = {0:10.3f}  with 3 decimal places in a 10 character field".format(y)     
    textBox.insert(END,myString+"\n")

    myString = "y = {0:10.2f}  with 2 decimal places in a 10 character field".format(y)      
    textBox.insert(END,myString+"\n")

    myString = "x = {0:6d}      format the int to an 6 character field".format(x)      
    textBox.insert(END,myString+"\n")
 
    myString = "y = {0:8d}    format the int to an 8 character field".format(x)    
    textBox.insert(END,myString+"\n")

    myString = "y = {0:<20}     left justified in 20 character field".format(y)      
    textBox.insert(END,myString+"\n")

    myString = "y = {0:^20}     center in 20 character field".format(y)      
    textBox.insert(END,myString+"\n")       

    myString = "y = {0:>20}     right justified in 20 character field".format(y)      
    textBox.insert(END,myString+"\n")

    myString = "Chapter 1 {0:.>14}     right justified with character fill".format(1)      
    textBox.insert(END,myString+"\n")

    myString = "Chapter 2 {0:.>14}     right justified with character fill".format(24)      
    textBox.insert(END,myString+"\n\n")

    textBox.insert(END,"Examples of conversion with variable = 255 \n")
    myString = "int: {0:3d};  hex: {0:#x};  oct: {0:#o};  bin: {0:#b}".format(255)
    textBox.insert(END,myString+"\n\n")

    # the whole point of this is to be able to iterate through the code and generate, for example, a table
    textBox.insert(END,"Example of a table\n")
    for x in range(1, 11):
        myString = "{0:2d} {1:3d} {2:4d}".format(x, x*x, x*x*x)
        textBox.insert(END,myString+"\n")
