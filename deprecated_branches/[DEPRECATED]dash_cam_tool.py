import os
import re

import pynmea2
from ffmpy import FFmpeg

# welcome message
print("**********************************************")
print("** Welcome to dashcam video conversion tool **")
print("**********************************************")
print("")

# user input destination dir
rootdir = input('Please input the root dir of dashcam video then press enter:\n')

# use current dir
# rootdir = os.getcwd()

# lat/lon formation conversion
def to_deg(value, loc):
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value - deg) * 60
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    return deg, min, sec, loc_value

# arrays
movFiles = []
gpsFiles = []
htmlFiles = []
gpsFileName = []
gpsHtmlName = []

print("Now starting video conversion...")
# Capture frames of MOV per second
def capture_frames():
    for dirPath, dirNames, fileNames in os.walk(rootdir):
        for fileName in fileNames:
            filePath = (os.path.join(dirPath, fileName))
            matchMov = re.match('.*.MOV', filePath)
            if str(matchMov) != 'None':
                picPath = (str(matchMov.group())[0:(len(matchMov.group()) - 4)])
                print(picPath)
                movFiles.append(picPath)
                if not os.path.exists(picPath + '/'):
                    os.mkdir(picPath + '/', mode=777)
                print('Now Processing: ' + picPath)
                ff = FFmpeg(
                    inputs={str(matchMov.group()): None},
                    outputs={str(picPath.replace('/', '//')) + '//' + str(
                        fileName[0:len(fileName) - 4]) + '-%d.jpg': '-vf fps=1 -qscale:v 1 -loglevel 0'}
                )
                gpsFile = open((picPath + '/' + fileName[0:len(fileName) - 4] + '.NMEA.csv'),
                               mode='w', encoding='utf-8')
                gpsHtml = open((picPath + '/' + fileName[0:len(fileName) - 4] + '.kml'),
                               mode='w', encoding='utf-8')
                ff.run()

# Locate CSV files
def locate_csv():
    for dirPath, dirNames, fileNames in os.walk(rootdir):
        for fileName in fileNames:
            filePath = (os.path.join(dirPath, fileName))
            matchGps = re.match('.*.csv', filePath)
            if str(matchGps) != 'None':
                gpsFileName.append(fileName)
                gpsFilePath = (str(matchGps.group()))
                gpsFiles.append(gpsFilePath)

# Locate KML files
def local_kml():
    for dirPath, dirNames, fileNames in os.walk(rootdir):
        for fileName in fileNames:
            filePath = (os.path.join(dirPath, fileName))
            matchHtml = re.match('.*.kml', filePath)
            if str(matchHtml) != 'None':
                gpsHtmlName.append(fileName)
                gpsHtmlPath = (str(matchHtml.group()))
                htmlFiles.append(gpsHtmlPath)

# Decode NMEA files to CSV and kml
# column_names = 'filename,lat_demical,lon_demical,lat_degree,lon_degree,time_stamp,speed,bearing\n'
def decode_nmea():
    column_names = 'filename,lat_demical,lon_demical,time_stamp,speed,bearing\n'
    mergedTrace = open(rootdir + '/' + 'GPS_Trace_Merged.csv', mode='a', encoding='utf-8')
    mergedTrace.write(column_names)
    for i in range(len(gpsFiles)):
        # print("i= " + str(i))
        g = open(str(gpsFiles[i]), mode='w', encoding='utf-8')
        h = open(str(htmlFiles[i]), mode='w', encoding='utf-8')
        g.write(column_names)
        h.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        h.write(
            "<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\" xmlns:kml=\"http://www.opengis.net/kml/2.2\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n")
        h.write("<Document>")
        h.write("<name>" + gpsFiles[i] + "</name>")
        h.write(
            "<Style id=\"sn_pink-blank\"><IconStyle><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/pink-blank.png</href></Icon><hotSpot x=\"32\" y=\"1\" xunits=\"pixels\" yunits=\"pixels\"/></IconStyle><ListStyle><ItemIcon><href>http://maps.google.com/mapfiles/kml/paddle/pink-blank-lv.png</href></ItemIcon></ListStyle></Style>")
        h.write(
            "<StyleMap id=\"msn_pink-blank\"><Pair><key>normal</key><styleUrl>#sn_pink-blank</styleUrl></Pair><Pair><key>highlight</key><styleUrl>#sh_pink-blank</styleUrl></Pair></StyleMap>")
        fileNameGroup = []
        for j in range(len(movFiles)):
            # print("J= " + str(j))
            j = i
            f = open(str(movFiles[j]) + '.NMEA', mode='r', encoding='utf-8')
            k = 0
            for line in f.readlines():
                if line[0:6] == '$GPRMC':
                    k += 1
                    msg = pynmea2.parse(line)
                    msg_seg = (str(msg).split(','))
                    speed = (msg_seg[7])
                    bearing = (msg_seg[8])
                    # gps_parsed = (((gpsFiles[i] + '-' + str(k) + '.jpg').replace('.NMEA.csv', '') + ',' + str(msg.latitude) + ',' + str(msg.longitude) + ',\"' + str(to_deg(msg.latitude, ["S", "N"])) + '\",\"' + str(to_deg(msg.longitude, ["W", "E"])) + '\",' + str(msg.timestamp)) + ',' + speed + ',' + bearing + '\n')
                    gps_parsed = (((gpsFileName[i] + '-' + str(k) + '.jpg').replace('.NMEA.csv', '') + ',' + str(msg.latitude) + ',' + str(msg.longitude) + ',' + str(msg.timestamp)) + ',' + speed + ',' + bearing + '\n')
                    gps_parsed_merged = ((('./' + gpsFileName[i] + '/' + gpsFileName[i] + '-' + str(k) + '.jpg').replace('.NMEA.csv', '') + ',' + str(msg.latitude) + ',' + str(msg.longitude) + ',' + str(msg.timestamp)) + ',' + speed + ',' + bearing + '\n')
                    g.write(gps_parsed)
                    mergedTrace.write(gps_parsed_merged)
                    attrib = gps_parsed.split(',')
                    if attrib[1] != '0.0' and attrib[2] != '0.0':
                        h.write("<Placemark><description><![CDATA[<img src=\"./" + attrib[
                            0] + "\" width=\"720\"/>" + "<table><tr><th>filename</th><th>lat_demical</th><th>lon_demical</th><th>time_stamp</th><th>speed</th><th>bearing</th></tr><tr><th>" +
                                attrib[0] + "</th><th>" + attrib[1] + "</th><th>" + attrib[2] + "</th><th>" + attrib[
                                    3] + "</th><th>" + attrib[4] + "</th><th>" + attrib[
                                    5] + "</th></tr></table>" + "]]></description><LookAt><longitude>" + attrib[
                                    2] + "</longitude><latitude>" + attrib[
                                    1] + "</latitude><altitude>0</altitude><gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode></LookAt><styleUrl>#sn_pink-blank</styleUrl><Point><gx:drawOrder>1</gx:drawOrder><coordinates>" +
                                attrib[2] + "," + attrib[1] + ",0</coordinates></Point></Placemark>")

            break
        h.write('</Document>')
        h.write('</kml>')

capture_frames()
locate_csv()
local_kml()
decode_nmea()

print('')
print('Process completed!')
