#! /bin/bash
# simple Python class for Bolt IoT API interaction
import requests
import uuid

# The BoltAPI object has two main purposes.
# 1) it keeps an internal list of devices to run commands against (must be associated with the API key)
# 2) it provides methods for invoking various Bolt API calls and getting responses
# 
# When a device name is added ot the list, it is verified by making a 'version' call
# if this succeeds, it is added
#
# if no args are given to the various methods, all devices in the list are sent the command
# if a device is named, only that device is used in the API call


class BoltAPI:
    def __init__(self, key):
        self.__apiVersion = '1.0.0'
        self.__baseURL = 'https://cloud.boltiot.com/remote/'
        self.__apiKey = ''
        self.__deviceIDs = list()
        self.__commands = []
        self.__debug_flag = True
        self.setKey(key)

    def setDebug(self, val):
        self.__debug_flag = val
        return self.__debug_flag

    def addDevice(self, id):
        id = str(id)
        valid = self.__isValidDevice(id)
        if(valid):
            self.__deviceIDs.append(id)
        return valid

    def removeDevice(self, id):
        valid = id in self.__deviceIDs
        if valid:
            self.__deviceIDs.remove(id)
        return valid

    def setKey(self, key):
        self.__pifd("Setting Key : "+key)
        try:
            self.__apiKey = uuid.UUID(key)
        except:
            self.__pifd("Key not a valid UUID")
            return False
        self.__pifd("Key Set : "+self.__getKeyString())
        return True

    def __getKey(self):
        return self.__apiKey

    def __getKeyString(self):
        return str(self.__apiKey)

    def listDevices(self):
        return self.__deviceIDs

    def __isValidDevice(self, id):
        if self.__call('version',id)['success']=="1":
            return True
        else:
            return False

    def version(self, **kwargs):
        results = list()
        if self.__deviceIDs:
            for dev in self.__deviceIDs:
                results.append(self.__call('version',dev))
            return results
        else:
            return []

    def isOnline(self, **kwargs):
        results = list()
        if self.__deviceIDs:
            for dev in self.__deviceIDs:
                results.append(self.__call('isOnline', dev))
        return results

    def restart(self, **kwargs):
        results = list()
        if self.__deviceIDs:
            for dev in self.__deviceIDs:
                results.append(self.__call('restart', dev))
        return results

    def analogRead(self, **kwargs):
        results = list()
        if self.__deviceIDs:
            for dev in self.__deviceIDs:
                results.append(self.__call('analogRead', dev, pin="A0" )) 
        return results

    def analogWrite(self, **kwargs):
        results = list()
        if ('pinNum' in kwargs and 
            'pinValue' in kwargs and
            kwargs['pinNum'] in range(0,4) and
            kwargs['pinValue'] in range(0,255)):
            if self.__deviceIDs:
                for dev in self.__deviceIDs:
                    results.append(self.__call('analogWrite', dev, pin=kwargs['pinNum'], value=kwargs['pinValue'] )) 
        return results

# TODO: incomplete and untested
    def digitalRead(self, **kwargs):
        results = list()
        if ('pinNum' in kwargs and 
            kwargs['pinNum'] in range(0,4)):
            if self.__deviceIDs:
                for dev in self.__deviceIDs:
                    results.append(self.__call('digitalRead', dev, pin=kwargs['pinNum'] )) 
        return results

# TODO: incomplete and untested
    def digitalWrite(self, **kwargs):
        results = list()
        paramStates = ['HIGH', 'LOW']
        if ('pinNum' in kwargs and 
            'pinValue' in kwargs and
            kwargs['pinNum'] in range(0,4) and
            kwargs['pinValue'] in paramStates):
            if self.__deviceIDs:
                for dev in self.__deviceIDs:
                    results.append(self.__call('digitalWrite', dev, pin=kwargs['pinNum'], value=kwargs['pinValue'] )) 
        return results

#TODO: implement UART calls


# main API workhorse, makes the actual remote calls
    def __call(self, command, device, **kwargs):
        self.__pifd("Call to: "+command+" : Device : "+device)
        uri = ''+self.__baseURL+self.__getKeyString()+'/'+command+'?deviceName='+device
        if kwargs:
            for param, value in kwargs.items():
                uri = uri+'&'+str(param)+'='+str(value)
        self.__pifd("Calling :"+uri)
        try:
            res = requests.get(uri)
        except:
            self.__pifd("Request Failed:")
        self.__pifd("Status :"+str(res.status_code))
        self.__pifd("Result :"+res.text)
        return res.json()

    #Print if Debug helper function
    def __pifd(self, msg):
        if self.__debug_flag:
            print msg

#just for easy smoke test
if __name__ == "__main__":
    #put a valid Bolt API key and associated device name here
    key = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    device = 'BOLTxxxxxxx'
    bolt = BoltAPI(key)
    bolt.setDebug(True)
    if (bolt.addDevice(device)):
        print bolt.listDevices()
        for res in bolt.version():
            print res
        for res in bolt.analogRead():
            print res
        for res in bolt.restart():
            print res
        for res in bolt.isOnline():
            print res