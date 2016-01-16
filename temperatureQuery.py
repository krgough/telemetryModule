'''
Created on 2 Jan 2016

@author: keith
'''
import peeweeModule as pw
import pylab as plt

numberOfSensors = 5

sensorCalibration = {'sensor1':-172,
                     'sensor2':  61,
                     'sensor3': 248,
                     'sensor4': 266,
                     'sensor5':-403}

def getData():
    """
    """
    pw.sqlCredId = 'kg_aws_keith'
    pw.database = 'hotwater'
    resp,errStatus = pw.selectWhere(pw.db,pw.temperature,(pw.temperature.timestamp > "2016-01-12 20:15" ))

    if errStatus:
        print(errStatus)
        exit()
        
    """ Build a dict of the form:
    
        timestamp : {'sensor1':temperature1, 'sensor2':temperature2, ... ,'sensor5':temeprature5}    
        timestamps will not be sorted so we build an index later.
    """
    data = {}
    for r in resp:
        if not r.timestamp in data: 
            data[r.timestamp]={}
        data[r.timestamp][r.sensorName]=r.temperature 
    
    """ Now build an index. 
        Create a sorted list of timestamps.  Use this to index the data dict.
    """
    sortedTimestamps = sorted(data)
    
    """ Now we can print the data table
        and create a dict of lists for the data  
    """    
    sensorData={}
    for i in range(1,numberOfSensors+1):
        sensorName = 'sensor{}'.format(i)
        sensorData[sensorName]=[]
    
    print('Timestamp,sensor1,sensor2,sensor3,sensor4,sensor5')
    for ts in sortedTimestamps:
        print("{},{},{},{},{},{}".format(ts,data[ts]['sensor1'],
                                            data[ts]['sensor2'],
                                            data[ts]['sensor3'],
                                            data[ts]['sensor4'],
                                            data[ts]['sensor5']))
        
        for i in range(1,numberOfSensors+1):
            sensorName = 'sensor{}'.format(i)
            sensorData[sensorName].append(data[ts][sensorName])
    
    return sortedTimestamps, sensorData
def plotGraph(x_range,y_range,numberOfLines):
    """
    """
    for i in range(1,numberOfLines+1):
        sensorName = 'sensor{}'.format(i)
        plt.plot(x_range,y_range[sensorName],label=sensorName)

    # 111 = 1 row, 1 column, 1 plot
    ax = plt.subplot(111)
    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
     
    plt.legend(loc='center left',bbox_to_anchor=(1, 0.5))
     
    plt.grid()
    plt.show()
    return
    
def main():
    x_range,y_range=getData()
    plotGraph(x_range,y_range,numberOfSensors)
    return
        
if __name__ == "__main__":
    main()
    print('All Done')