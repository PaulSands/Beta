import ListLib
import stream01

"""
This library was created to help analyze HD data.

get_pump_timestamps() is used in Analysis200.py 


"""


if __name__ == '__main__':
    #import doctest
    #doctest.testmod(verbose=True)    

    datalist = stream01.read_str_file('3_I164_Oct_4.str')
    # aList = [(1900, 'P'),(5000,'p')]
    injection_count = ListLib.count_char('P',datalist)
    print('Number of injections:', injection_count)

    pump_timestamps = get_pump_timestamps(datalist,0)
    print(pump_timestamps)
    print(len(pump_timestamps))

    """
    times = ListLib.get_time_list_for_code('P', datalist)    
    # print('Pump start times: ',times)
    for b in range(12):
        pump_timelist = get_pump_timelist(datalist, block = b)
        # print("pump_timeiist:", pump_timelist)
        pumptimes_per_bin = get_pumptimes_per_bin(pump_timelist, bin_size = 10000)
        print('pumptimes_per_bin = ', pumptimes_per_bin)
    """

    


