import codecs, struct
import locale

def read_str_file(filepath):
    ''' (string) -> list of [int, char]

    filepath is a string containing a valid filepath to a .str data file.
    Returns a list of lists with each sublist containing an integer
    representing the timestamp and a char representing the type of event.
    
    B, b = Start and stop of a first lever block
    A, a = Start and stop of a second lever block
    L, l = First lever down and up
    J, j = Second lever down and up
    =, . = First lever extend (=) and retract (.)
    -, , = Second lever extend (-) and retract (,)
    T, t = Start and stop of a trial
    S, s = Stimulus light on and off
    P, p = Pump on and off
    E    = End of session
    R    = Restart session

    To do: make the function handle the "session info - x" stuff
    '''
    
    data = []

    #codecs.open() is a more powerful version of the built-in open() that can handle filestreams
    file = codecs.open(filepath, mode ='rb')

    #this code is just determining how long the file is
    file.read()     
    file_length = file.tell()
    file.seek(0)

    while file.tell() < file_length:
        #struct.unpack reads binary data and translates them into readable strings
        #The first parameter is a string that tells unpack what to look for
        #'I' is an unsigned integer of 4 bytes; 'c' is a string of length 1
        #unpack must receive the exact number of bytes it is looking for
        #since 'I c' = 5 bytes of information, you must pass exactly 5 bytes to it
        event = struct.unpack('I c', file.read(5))   

        # print(event)
    
        timestamp = int(str(event)[1:str(event).find(',')])
        char = str(event)[-3]
        data.append([timestamp, char])
    
        #there appear to be several 'padding' bytes; this makes it line up right
        file.read(3)

        if char == 'X':
            file.read(1)
            
            variable = struct.unpack('4s', file.read(4))
            omni_version = str(variable)[2:-2]
            
            file.read(5)
            variable = struct.unpack('20s', file.read(20))
            investigator = str(variable)[3:-3]

            file.read(1)
            variable = struct.unpack('8s', file.read(8))
            rack = str(variable)[3:-3]

            file.read(1)
            variable = struct.unpack('d', file.read(8))
            program_start_time = str(variable)[1:-2]
            basetime = 1900 + (int(float(program_start_time))/365.25)
            year = int(basetime)
            month = int((basetime - year)*12+1)
            day = int(((basetime - year)*12+1-month)*30+1)
            
            
            file.read(104) 
            # 
            print("Omni version:", omni_version)
            # print("Investigator:", investigator)
            # print("Rack:", rack)
            print("Program Start Time:", program_start_time)
            print("Date (y/m/d):", year, month, day)
            
            #print(event)
            

## The data following the "X" value is 152 bytes in total
##            SelectedStream.Read(SessionRecord, SizeOf(SessionRecord));
##            OMNI_Version     := SessionRecord.OMNI_Version;      // string [8];
##            Investigator     := SessionRecord.Investigator;      // string [20];
##            Rack             := SessionRecord.Rack;              // string[8];
##            ProgramStartTime := SessionRecord.ProgramStartTime;  // TDateTime;
##            Box_Number       := SessionRecord.Box_Number;        // integer;
##            RatID            := SessionRecord.RatID;             // string[6];
##            Body_weight      := SessionRecord.Body_weight;       // integer;
##            Drug             := SessionRecord.Drug;              // string[16];
##            Drug_Concentration := SessionRecord.Drug_Concentration; // real;
##            Pump_RPM         := SessionRecord.Pump_RPM;          // integer;
##            SessionStr       := SessionRecord.SessionStr;  // string [15];
    
    file.close()
    return data

#Example of using the function

"""
filepath = 'sep_30.str'
data1 = get_data(filepath)
mystring = ''
count = 0

for item in data1:
    if count < 20:
        mystring = mystring + str(item) + '\n'
    count = count + 1

print(mystring)

"""


##'X' : begin


##  SelectedStream.Read(SessionRecord, SizeOf(SessionRecord));
##  OMNI_Version     := SessionRecord.OMNI_Version;      // string [8];
##  Investigator     := SessionRecord.Investigator;      // string [20];
##  Rack             := SessionRecord.Rack;              // string[8];
##  ProgramStartTime := SessionRecord.ProgramStartTime;  // TDateTime;
##  Box_Number       := SessionRecord.Box_Number;        // integer;
##  RatID            := SessionRecord.RatID;             // string[6];
##  Body_weight      := SessionRecord.Body_weight;       // integer;
##  Drug             := SessionRecord.Drug;              // string[16];
##  Drug_Concentration := SessionRecord.Drug_Concentration; // real;
##  Pump_RPM         := SessionRecord.Pump_RPM;          // integer;
##  SessionStr       := SessionRecord.SessionStr;  // string [15];

