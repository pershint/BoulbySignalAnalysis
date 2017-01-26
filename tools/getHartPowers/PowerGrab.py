
from __future__ import print_function
from bs4 import BeautifulSoup as bs
import urllib2
import logging
import sys, traceback
import os.path
import csv

basepath = os.path.dirname(__file__)
dbpath = os.path.abspath(os.path.join(basepath,"..","..","DB"))

POWER_DATA_FILE = dbpath + '/Hartlepool.csv'

LOGFILE = os.path.abspath(os.path.join(basepath, 'log')) + '/Hartlepoolget.log'
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename=LOGFILE, format=FORMAT)

def My_UEHandler(exectype, value, tb):
    logging.exception("UNCAUGHT EXCEPTION: ")
    logging.exception("type: " + str(exectype))
    logging.exception("value: " + str(value))
    logging.exception("Traceback: " + str(traceback.print_tb(tb)))
    traceback.print_exception(exectype, value, tb)


sys.excepthook = My_UEHandler


class EDFHartlepoolInfo(object):

    _homepage = 'https://www.edfenergy.com/energy/power-stations'
    _hartlepoolpg = '/hartlepool'

    def __init__(self):
        self.webpage = self.webpageconnect()
        self.soup = bs(self.webpage, 'html.parser')
        self.powerEntry = {}
        self.powerEntry['Hartlepool_turbines'] = 'none'

    def webpageconnect(self):
        try:
            return urllib2.urlopen(self._homepage + self._hartlepoolpg, timeout=5)
        except urllib2.URLError, e:
            logging.exception("Connection error: %r" % e)
            raise Exception("Connection error: %r" % e)

    def getCurrentDataDate(self):
        for div in self.soup.find_all('div'):
            divtypes = div.get('class')
            if divtypes != None:
                if 'status-banner' in divtypes:
                    status_banner = div
                    break
        banner_entries = []
        for span in status_banner.find_all('span'):
            banner_entries.append(span.get_text())
        for j,entry in enumerate(banner_entries):
            if entry.find('Last updated') != -1:
                entry = entry.rstrip(':\n ').lstrip('\n ')
                print("Date of power entry update: " + banner_entries[j+1])
                self.powerEntry[str(entry)] = str(banner_entries[j+1])
                

    def getHartlepoolPowers(self):
        #Get power information on the turbines for current log
        turbine_divs = []
        for div in self.soup.find_all('div'):
            divtypes = div.get('class')
            if divtypes != None:
                if 'l-grid-wrapper' and 'turbines' in divtypes:
                    turbine_divs.append(div)
        Turbine_power_info_entries = {}
        for turbine in turbine_divs:
            titleobj = turbine.find_all('h4')
            for t in titleobj:
                title = str(t.string.rstrip(' ').lstrip('\n '))
                Turbine_power_info_entries[title] = {}
            divobjs = turbine.find_all('div')
            for div in divobjs:
                if div.get('class') != None:
                    if 'generation-amount' in div.get('class'):
                        power = div.get_text().lstrip('\n ').rstrip(' \n ')
                        Turbine_power_info_entries[title]['power'] = str(power)
                    if 'field-name-field-status-description' in div.get('class'):
                        status = div.get_text()
                        Turbine_power_info_entries[title]['status'] = str(status)
        self.powerEntry['Hartlepool_turbines'] = Turbine_power_info_entries
            
def checkDuplicate(date):
    '''
    Opens the POWER_DATA file and checks for a duplicate data entry.  If therr
    is a duplicate, returns True.
    '''
    isduplicate = False
    f = open(POWER_DATA_FILE, 'r')
    for line in f:
        if date in line:
            isduplicate = True
    return isduplicate

if __name__=='__main__':
    EDFconn = EDFHartlepoolInfo()
    EDFconn.getCurrentDataDate()
    EDFconn.getHartlepoolPowers()
    isduplicate = checkDuplicate(EDFconn.powerEntry['Last updated'])
    if not isduplicate:
        with open(POWER_DATA_FILE, 'a') as outfile:
            outfile.write('\n')
            w = csv.DictWriter(outfile, EDFconn.powerEntry.keys())
            w.writeheader()
            w.writerow(EDFconn.powerEntry)
            print("New power information added to Hartlepool.csv in DB.")
    else:
        print("Current power data on EDF webpage already in DB.")
