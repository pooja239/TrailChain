from web3 import Web3
hex2bin = dict('{:x} {:04b}'.format(x,x).split() for x in range(16))
bin2hex = dict('{:04b} {:x}'.format(x,x).split() for x in range(16))

def addWatermark(K, filename):

    tempList = []#a = []
    dataList = []
    dataList1 = [] #b = []
    dataList2 = []
    joinedsamples = ''
    watermarkeddataList = []
    
    ##open dataset file and read samples in local variable
    f = open(filename, "r") 
    for ele in f:
        tempList.append(ele.split("\n"))
    for ele in tempList:
        dataList.append(ele[0].split("\t"))
    tempList = []
    
    batch1 = True
    for ele in dataList:
        if(batch1):
            if(ele[0] != 'FFFFFFFFFFF'):
                dataList1.append(ele)
            else:
                #dataList1.append(ele)
                batch1 = False
        else:
            if(ele[0] != 'FFFFFFFFFFF'):
                dataList2.append(ele)
    dataList = []

    # cocaternate samples(without LSB and LSB-1) in each batch -> joinedsamples
    # take the hash of each concatenation -> list d
    for ele in dataList1:
        joinedsamples = joinedsamples + ele[0][:-1] + ele[1][:-1]

    # convert the hash to binary -> list datahash_binary
    
    dataHash = Web3.toHex(Web3.soliditySha3(['string'], [joinedsamples]))

    datahash_binary = ''.join(hex2bin.get(char, char) for char in dataHash[2:])

    k_binary = ''.join(hex2bin.get(char, char) for char in K[2:])

    i = 0
    for ele in dataList2:
        ele1 = hex2bin.get(ele[0][-1:]) 
        ele2 = hex2bin.get(ele[1][-1:])
        
        #replace LSB-1 with previous batch hash and LSB with K
        x1 = ele[0][:-1] + bin2hex.get('00'+datahash_binary[i]+k_binary[i])
        x2 = ele[1][:-1] + bin2hex.get('00'+datahash_binary[i]+k_binary[i])
        
        ####embeeded watermark data batch
        watermarkeddataList.append([x1,x2])
        i = i+1

    textfile = open("watermarkedData.txt", "w")
    for element in dataList1:
        textfile.write(str(element[0]) + "\t" + str(element[1]) + "\n")
    textfile.write('FFFFFFFFFFF' + "\t" + 'FFFFFFFFFFF' + "\n")
    for element in watermarkeddataList:
        textfile.write(str(element[0]) + "\t" + str(element[1]) + "\n")
    textfile.write('FFFFFFFFFFF' + "\t" + 'FFFFFFFFFFF' + "\n")
    textfile.close()
    return "watermarkedData.txt"


def DetectExtractWatermark(filename):
    
    watermarkDetected = False
    batchTampered = False
    dataList = []
    tempList = []
    dataList1 = [] #b = []
    dataList2 = []
    joinedsamples = ''
    watermarked_samples = []
    
    f = open(filename, "r")
    
    # read line by line samples from file -> list b
    for ele in f:
        tempList.append(ele.split("\n"))
    for ele in tempList:
        dataList.append(ele[0].split("\t"))
    
    tempList = []

    batch1 = True
    for ele in dataList:
        if(batch1):
            if(ele[0] != 'FFFFFFFFFFF'):
                dataList1.append(ele)
            else:
                #dataList1.append(ele)
                batch1 = False
        else:
            if(ele[0] != 'FFFFFFFFFFF'):
                dataList2.append(ele)

    dataList = []

    # cocaternate samples(without LSB and LSB-1) in each batch -> joinedsamples
    # take the hash of each concatenation -> list d
    for ele in dataList1:
        joinedsamples = joinedsamples + ele[0][:-1] + ele[1][:-1]
    # convert the hash to binary -> list datahash_binary
    
    dataHash = Web3.toHex(Web3.soliditySha3(['string'], [joinedsamples]))

    datahash_binary = ''.join(hex2bin.get(char, char) for char in dataHash[2:])

    #k_hash = []
    
    k1 = '' #k1 is K of sample 1.1
    k2 = '' #k2 is K of sample 1.2
    d1 = '' #d1 is data hash of sample 1.1
    d2 = '' #d2 is data hash of sample 1.2


    #batchCount = 0
    for ele in dataList2:
        ele1 = hex2bin.get(ele[0][-1:])
        ele2 = hex2bin.get(ele[1][-1:])
        d1 = d1 + ele1[-2:-1]
        d2 = d2 + ele2[-2:-1]
        k1 = k1 + ele1[-1:]
        k2 = k2 + ele2[-1:]

    if(d1 == d2): ###if data hash of both the sample 1.1 and 1.2 are same that means data integrity
        if(datahash_binary == d1): #### if data Hash is same as the extracted data hash that means watermark detected               
            #watermarkDetected = True
            if(k1 == k2):
                k_hash = ''.join(bin2hex.get(k1[i:i+4],k1[i]) for i in range(0, len(k1), 4))
                result = "0x" + k_hash
            else:
                result = "Watermark tampered"
        else:
            result = "Watermark not detected"
    else:
        #batchTampered = True
        result = "Samples are tampered"

    return result

#K = '0xef914666118d548ecdd69a3f1e93d3c1c4aaabda22c097404c53dbc22f808c4f'
#addWatermark(K, "data.txt")
#print(DetectExtractWatermark("watermarketData.txt"))
