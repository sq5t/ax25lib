#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import struct
import binascii
import string
import re
import datetime
import threading
import time

class ax25lib:
    version = "0.1"
    host = ""
    port = 0
    type = ""
    def shift_data(self,data,direction,dr=""): # dr: destination or repeated, information needed to know where set bit
        if(direction=="rx"):
            return_data = ["" for x in range(10)]
            for x in range(6):
                return_data[x] = chr(ord(data[x])>>1)
            ssid_tmp = str((int(hex(ord(data[6])),16) & 15)>>1)
            if(ssid_tmp!="0"):
                return_data[6] = chr(ord("-"))
                for x in range(len(ssid_tmp)):
                    return_data[7+x] = ssid_tmp[x]
            return_data = [x.strip(' ') for x in return_data]
        elif(direction=="tx"):
            rpt_data = data.split(",")
            return_data = ["" for x in range(len(rpt_data)*7)]
            i = 0
            len_data = len(rpt_data)
            while i < len_data:
                call = rpt_data[i].split("-")
                callsign = call[0]
                while len(callsign) < 6:
                    callsign = callsign + chr(0x20)
                if(len(call)==1):
                    ssid = 0
                else:
                    ssid = int(call[1])
                ssid_bin = 0 ^ ssid<<1 ^ 96
                if(dr):
                    ssid_bin = ssid_bin ^ 128 # set bit if dr=True
                if not dr and (i == len_data -1):
                    ssid_bin = ssid_bin ^ 1
                y = (i+1)*7-1 # calculate byte with ssid included
                i_start = (i+1)*7-7
                i_stop = (i+1)*7
                z = 0
                for x in range(i_start,i_stop):
                    if (x != y):
                        # if not ssid byte do bitshift
                        return_data[x] = chr(ord(callsign[z])<<1)
                        z += 1
                    else:
                        # add ssid byte
                        return_data[x] = chr(ssid_bin)
                i += 1
        dane_wynikowe = "".join(return_data)
        return dane_wynikowe

    def special_chars(self,data):
        """
        Frame escape for tnc (FEND and FESC). Function not tested.
        """

        count = len([m.start() for m in re.finditer(b'\xdb\xdc', data)]) + len([m.start() for m in re.finditer(b'\xdb\xdd', data)])
        if (count > 0):
            return_data = [] * len(data) - count
            for x in range(len(return_data)-1):
                if(hex(ord(data[x])) == '0xdb' & hex(ord(data[x+1])) == '0xdc'):
                    return_data[x] = b'\xc0'
                elif(hex(ord(data[x])) == '0xdb' & hex(ord(data[x+1])) == '0xdd'):
                    return_data[x] = b'\xc0'
                else:
                    return_data[x] = data[x]
            return return_data
        else:
            return data


    def ax25(self,data):
        packet = {}
        self.special_chars(data)
        size = len(data)
        ile =  ((data.find(b'\x03\xf0')-2)/7)
        if(ile==-1): #if not UI frame
            exit()
        ax25data = data[2:2+7]
        packet['destination']=self.shift_data(ax25data,"rx")
        ax25data = data[9:9+7]
        packet['source']=self.shift_data(ax25data,"rx")
        packet['via'] = ""
        # up to 8 repeaters
        if (ile >= 3):
            ax25data = data[16:16+7]
            packet['via'] = self.shift_data(ax25data,"rx")
        if (ile >= 4):
            ax25data = data[23:23+7]
            packet['via'] = packet['via'] + "," + self.shift_data(ax25data,"rx")
        if (ile >= 5):
            ax25data = data[30:30+7]
            packet['via'] = packet['via'] + "," + self.shift_data(ax25data,"rx")
        if (ile >= 6):
            ax25data = data[37:37+7]
            packet['via'] = packet['via'] + "," + self.shift_data(ax25data,"rx")
        if (ile >= 7):
            ax25data = data[44:44+7]
            packet['via'] = packet['via'] + "," + self.shift_data(ax25data,"rx")
        if (ile >= 8):
            ax25data = data[51:51+7]
            packet['via'] = packet['via'] + "," + self.shift_data(ax25data,"rx")
        if (ile >= 9):
            ax25data = data[58:58+7]
            packet['via'] = packet['via'] + "," + self.shift_data(ax25data,"rx")
        if (ile == 10):
            ax25data = data[65:65+7]
            packet['via'] = packet['via'] + "," + self.shift_data(ax25data,"rx")
        packet['data'] = data[ile*7+4:size-1]
        packet['pid']='\x03';
        packet['control']='\xf0';

        return packet

    def send(self,source,destination,rpt,message): # create UI frame
        packet_to_send = b'\xc0\x00'
        packet_to_send += self.shift_data(destination,"tx",dr=True)
        packet_to_send += self.shift_data(source,"tx",dr=True)
        packet_to_send += self.shift_data(rpt,"tx",dr=False)
        packet_to_send += b'\x03\xf0'
        packet_to_send += message
        packet_to_send += b'\xc0'

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.send(packet_to_send)
        s.close()

    def __init__(self,type,host,port,callback=None):
        self.host = host
        self.port = port
        self.type = type
        thread = threading.Thread(target=self.run, args=(self.type,self.host,self.port,callback))
        thread.daemon = True
        thread.start()

    def run(self,type,host,port,callback=None):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        while True:
            data = ""
            try:
                data = s.recv(1500)
            except socket.error, (value,message):
                print 'socket.error - ' + message
            callback(self.ax25(data))
            print ""
        s.close()
