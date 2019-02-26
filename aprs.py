#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ax25lib import ax25lib
import time

def main():
    while True:
        time.sleep(1)

def dane(data):
    dane = ax25.ax25(data)
    print "Source: ",dane['source']
    print "Destination: ",dane['destination']
    print "VIA: ",dane['via']
    print "Data: ",dane['data']
    print "Control: ",dane['control']
    print "PID: ",dane['pid']

if __name__ == '__main__':
    # print ax25lib.version
    ax25 = ax25lib(type="tcp",host="192.168.0.55",port=8001,callback=dane)
    # if repeater is WIDEn-n than it need to be written with "-" , for example: "WIDE2-1"
    # ax25.send(source="SQ5T",destination="APSQ5T",rpt="RFONLY",message="}Python test")
    main()
