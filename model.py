import math


def  calculateConcentration (D, T, resolution):
    """ dose, time, resolution >> concentration
        Returns the concentration of cocaine at time T given dose (D) at time zero.
        kel = 0.294  - rate constant for elimination from blood by metabolism and excretion
        Using the Pan equation for alpha as follows
        alpha := 0.5*((k12+k21+kel)+SQRT((k12+k21+kel)*(k12+k21+kel)-(4*k21*kel)));
        beta  := 0.5*((k12+k21+kel)-SQRT((k12+k21+kel)*(k12+k21+kel)-(4*k21*kel)));
        results in the alpha used by Nicola and Deadwyler
        alpha : real = 0.641901;   // per min
        beta : real = 0.097099;    // per min
        BTW Tsibulski and Norman (Brain Res Prot. 2005) say half life of cocaine is 480 sec.
        resolution (in seconds) converted to fraction of a minute (i.e. 60/resolution)
    """
    
    dv1 = 0.112444;   # blood
    dv2 = 0.044379;   # brain
    k12 = 0.233;      # rate constant for transfer from blood to brain
    k21 = 0.212;      # rate contant for transfer from brain to blood
    kel = 0.294                    # check with ModelTab_Kel_UpDown.position/10 
    alpha = 0.641901               # per min
    beta = 0.097099                # per min

    concentration = ((D*k12)/(dv2*(alpha-beta)))*((math.exp(-beta*(T*(resolution/60)))-math.exp(-alpha*(T*(resolution/60)))));

    return concentration


def calculateCocConc (aList, cocConc, pumpSpeed, resolution, bodyWeight = 0.330):
    """ dataList, cocConc, pumpSpeed, respultion >> list of cocaine concentrations
        Returns timestamp pairs corresponding to every 5 sec bin of a 6 hr session (4320 bins)
        resolution in seconds
    """
    # cocConc   Wake default = 5.0 mg/ml   
    # pumpSpeed Wake = 0.025 ml/mSec
    pumpSpeed = pumpSpeed/1000    # convert to ml/mSec
    # print("pumpSpeed = ",pumpSpeed)
    duration = 0            # LongWord
    dose = 0.0

    lastBin = int((60/resolution) * 360) #  ie. 5 sec = (60/5)* 360 = 4320          # 6 hours    choices : 2160, 4320, 17280
    pumpOn = False
    pumpOnTime = 0    

    modelList = []
    for i in range(lastBin+1):
        modelList.append([i*resolution*1000,0])
    # model5secBins[720][1] = 30
    for pairs in aList:
        if pairs[1] == "P":
            pumpOn = True
            pumpOnTime = pairs[0]
        elif pairs[1] == "p":
            if pumpOn:
                pumpOn = False
                duration = pairs[0]-pumpOnTime
                dose =  (duration * cocConc * pumpSpeed)/bodyWeight;
                # eg. 4000 mSec * 5 mg/ml *0.000025 mls/mSec / 0.330 kg = 1.5 mg/kg
                i = int(pairs[0]/(resolution*1000)+1)  # calculate which bin
                # print(i)
                if i < lastBin:
                    for t in range(lastBin-i):     # t would normally be every 5 sec
                        modelList[i+t][1] = modelList[i+t][1] + calculateConcentration(dose,t,resolution)
    returnlog = False
    if returnlog:
        for pairs in modelList:
            if pairs[1] > 0:
                print(pairs[1])
                # modelList[1] = math.log(modelList[1])                            

    return modelList
 

