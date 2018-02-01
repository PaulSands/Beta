import stream01

"""
Notes Oct 8 prior to commit

count_

Lever             One      Two
----------------------------------
Lever Down          L       J
Lever Up            l       j
Start_Block_Char    B       A
End_Block_Char      b       a     = IBI
Insert Lever        =       -
Retract Lever       .       ,
StartTrial          T
EndTrial            t
PumpOn              P
PumpOff             p
StimOn              S
StimOff             s
StartSession        G
EndSession          E

"""

def count_char(letter_code, aList):
    ''' (letter, list) -> int
        Returns the number of times a letter_code occurs in a list.
    '''
    count = 0
    for timestamp in aList:
        if timestamp[1] == letter_code:
            count = count + 1
    return count

def get_time_list_for_code(letter_code, aList):
    ''' (letter, list) -> list

    Return a list of times corresponding to the letter_code.

    A timestamp is a pair of integer (time) and charcter (letter_code).
    The timestamp can be a list of lists or a list of tuples

    >>> find_code('B',[(1000, 'B'),(2000,'P'),(3000,'B')])
    [1000, 3000]
    '''
    return_list = []
    
    for timestamp in aList:
        if timestamp[1] == letter_code:
            return_list.append(timestamp[0])

    return return_list

def pump_durations_per_block(aList):
    ''' (list) -> list
        Returns a list of pump durations for each block
    '''
    durations = [0,0,0,0,0,0,0,0,0,0,0,0]
    duration = 0
    pumpOn = False
    block_index = -1
    for timestamp in aList:           
        if timestamp[1] == 'b':     # end of block
           block_index = block_index + 1
           durations[block_index] = duration  # Add to list
           duration = 0
        if timestamp[1] == 'P':
            pumpStartTime = timestamp[0]
            pumpOn = True
        if timestamp[1] == 'p':
            if pumpOn:
                duration = duration + (timestamp[0] - pumpStartTime)
                pumpOn = False
    return durations

def get_pump_count_per_block(aList):
    ''' (list) -> list
        Returns a list of pump durations for each block
    '''
    counts = [0,0,0,0,0,0,0,0,0,0,0,0]
    block_index = -1
    for timestamp in aList:           
        if timestamp[1] == 'B':     # end of block
           block_index = block_index + 1
        if timestamp[1] == 'P':
            counts[block_index] = counts[block_index] + 1
    return counts



def get_pump_timestamps (aList, block):
    ''' (list) -> list
        From a list of timestamps,  returns a list of
        timestamps for a selected block.

        All session times coverted to block times (0 - 5 min).
        
        A timestamp is a pair of integer (time) and charcter (letter codes).
        Letter codes for Pump On ("P") and Pump Off ("p")
        .
        The timestamp can be a list of lists or a list of tuples
    '''
    pump_timestamps = []
    pumpOn = False
    block_index = -1
    for timestamp in aList:
        if timestamp[1] == 'B':
            block_index = block_index + 1
            block_start_time = timestamp[0]
        if timestamp[1] == 'P':
            if (block_index == block):
                block_time = timestamp[0] - block_start_time
                pump_timestamps.append([block_time, 'P']) 
            pumpOn = True
        if timestamp[1] == 'p':
            if pumpOn:
                if (block_index == block):
                    block_time = timestamp[0] - block_start_time
                    pump_timestamps.append([block_time, 'p']) 
            pumpOn = False                                  
    return pump_timestamps 

    
def get_pump_duration_list(aList, block):
    ''' (list) -> list[int,int]
        From a datalist (of timestamps), returns a list of
        times for Pump On ("P") and duration calculated from Pump Off ("p").

        All times coverted to block times - therefore useful for
        creating event records for specific blocks

        A timestamp is a pair of integer (time) and charcter (letter_code).
        The timestamp can be a list of lists or a list of tuples

        block = -1  <- this accumulates all blocks, otherwise ..
        eg. Block
        
    '''
    pump_timelist = []
    duration = 0
    pumpOn = False
    block_index = -1
    for timestamp in aList:
        if timestamp[1] == 'B':
            block_index = block_index + 1
            block_start_time = timestamp[0]
        if timestamp[1] == 'P':
            pumpStartTime = timestamp[0]
            pumpOn = True
        if timestamp[1] == 'p':
            if pumpOn:
                duration = timestamp[0] - pumpStartTime
                pumpOn = False
                block_time = pumpStartTime - block_start_time
                if (block == -1):
                    pump_timelist.append([block_index,block_time, duration]) 
                elif (block_index == block):
                    pump_timelist.append([block_index,block_time, duration])               
    return pump_timelist    



def get_pumptimes_per_bin(pump_timelist, bin_size = 5000):
    ''' (list) -> (list)
        From a pump_duration_list, returns a list of cummulative pump durations
        per one second bins.
        >>> get_pumptime_per_bin([(1900, 2600])  # (start_time, duration)
        [0,100,1000,1000,500]
    '''
    durations_per_bin = []

    # calculate number of bins required and initialize list
    access_period = 1000*60*5  # 5 minutes
    number_of_bins = access_period // bin_size
    for bin in range(number_of_bins):
        durations_per_bin.append(0)

    for pair in pump_timelist:    # step through list
        start_time = pair[1]
        duration = pair[2]
        bin_num = pair[1]//bin_size
        remaining_bin_time = ((bin_num+1) * bin_size) - start_time
        # If the duration fits within one bin then add it to that bin and you are done
        if duration < remaining_bin_time:     # done
            durations_per_bin[bin_num] = durations_per_bin[bin_num] + duration
        # But if the pump duration spans two or more bins then..
        # split the duration into consecutive bins
        else:                                 
            durations_per_bin[bin_num] = durations_per_bin[bin_num] + remaining_bin_time
            duration = duration - remaining_bin_time
            bin_num = bin_num + 1
            while duration > 0:
                if duration > bin_size:
                    durations_per_bin[bin_num] = durations_per_bin[bin_num] + 1000                    
                    duration = duration - 1000
                    bin_num = bin_num + 1
                else:
                    durations_per_bin[bin_num] = durations_per_bin[bin_num] + duration
                    duration = 0  
    return durations_per_bin
    
   


"""
    Stuff moved ...
    #import doctest
    #doctest.testmod(verbose=True)    

    aList = []
    aFile = open('IntA_Example_File.dat','r')
    for line in  aFile:
        pair = line.split()
        pair[0] = int(pair[0])
        aList.append(pair)
    aFile.close()
"""


if __name__ == '__main__':
    """ test of each function above in order

    """    
    aList = stream01.read_str_file('TH_OMNI_test.str')

    # count_char() 
    response_count = count_char('L',aList)
    print('Number of Responses: ', response_count)
    injection_count = count_char('P',aList)
    print('Number of Injections:', injection_count)
    block_count = count_char('B',aList)
    print('Number of Blocks:', block_count)
    #get_pump_count_per_block()
    pump_count_list = get_pump_count_per_block(aList)
    print("Pump_counts: ", pump_count_list)

    # get_time_list_for_code()
    times = get_time_list_for_code('B', aList)    
    print('Block start times: ',times)
    # pump_durations_per_block()
    durations_list = pump_durations_per_block(aList)   
    print("Total durations per block:", durations_list)
    # get_pump_timestamps()
    for b in range (1):    # change to 12 to see all blocks
        timestamps = get_pump_timestamps (aList, b)
        print("Block "+str(b), timestamps)
    # get_pump_duration_list()
    print("pump_duration_list stuff")
    for b in range (1):    # change to 12 to see all blocks
        pump_duration_list = get_pump_duration_list(aList, b)
        list_item = pump_duration_list[2]
        print(list_item[2])
        #print("Block "+str(b), pump_duration_list)

    """    
    pump_duration_list = get_pump_duration_list(aList, -1)
    single_entry_list = []
    for data in pump_duration_list:
        single_entry_list.append(data[2]) 
    single_entry_list.sort()
    print("length:", len(single_entry_list))


      
    # get_pumptimes_per_bin()
    pump_duration_list = get_pump_duration_list(aList, 0)
    print(pump_duration_list)
    # get_pumptimes_per_list()
    pumptimes_per_bin = get_pumptimes_per_bin(pump_duration_list)
    print(pumptimes_per_bin)
    """
    


