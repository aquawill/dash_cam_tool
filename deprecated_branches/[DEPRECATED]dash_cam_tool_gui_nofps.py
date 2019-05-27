import os
import time
from tkinter import *

import pynmea2
from ffmpy import FFmpeg

# arrays/lists
creation_time_list = []
movFiles = []
gpsFiles = []
htmlFiles = []
menuFiles = []
dmoGpsFiles = []
gpsFileName = []
gpsHtmlName = []
menuName = []

root = StringVar


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


def create_dir(rootdir):
    if not os.path.exists(rootdir):
        print('Invalid path, please try again...')
        quit()
    if not os.path.exists(rootdir + '\\gps\\'):
        os.mkdir(rootdir + '\\gps\\', mode=777)
    if not os.path.exists(rootdir + '\\audio\\'):
        os.mkdir(rootdir + '\\audio\\', mode=777)


def capture_frames(rootdir, res, extracting_video):
    app.destroy()
    counter = 0
    for dirPath, dirNames, fileNames in os.walk(rootdir):
        for fileName in fileNames:
            filePath = (os.path.join(dirPath, fileName))
            matchMov = re.match('.*.[Mm][Oo][Vv]', filePath)
            if str(matchMov) != 'None':
                movPath = str(matchMov.group())
                creation_time = time.strftime('%m_%d_%y', time.gmtime(os.path.getmtime(movPath)))
                dmo_gps_file_name = time.strftime('%Y%m%d', time.gmtime(os.path.getmtime(movPath)))
                if not dmo_gps_file_name in creation_time_list:
                    creation_time_list.append(dmo_gps_file_name)

                if not os.path.exists(rootdir + '\\gps\\' + dmo_gps_file_name + '.gps'):
                    open(rootdir + '\\gps\\' + dmo_gps_file_name + '.gps', mode='w', encoding='utf8')
                if not os.path.exists(rootdir + '\\images\\'):
                    os.mkdir(rootdir + '\\images\\', mode=777)
                if not os.path.exists(rootdir + '\\images\\' + creation_time + '/'):
                    os.mkdir(rootdir + '\\images\\' + creation_time + '/', mode=777)

                pic_path = str(rootdir + '\\images\\' + creation_time + str(matchMov.group()).replace(rootdir, ''))
                if not os.path.exists(pic_path[0:len(pic_path) - 4] + '/'):
                    os.mkdir(pic_path[0:len(pic_path) - 4] + '/', mode=777)
                movFiles.append(movPath)

                print(str(time.asctime()) + '\n' + movPath[0:len(movPath) - 4])

                ff = FFmpeg(
                    inputs={str(matchMov.group()): None},
                    outputs={str(pic_path[0:len(pic_path) - 4].replace('/', '//')) + '//' + str(
                        fileName[0:len(fileName) - 4]) + '-%d.jpg': '-vf fps=1 ' + res + ' -qscale:v 1 -loglevel 0'})

                # making trace files

                open((pic_path[0:len(pic_path) - 4] + '/' + fileName[0:len(fileName) - 4] + '.NMEA.csv'),
                     mode='w', encoding='utf-8')
                open((pic_path[0:len(pic_path) - 4] + '/' + fileName[0:len(fileName) - 4] + '.kml'),
                     mode='w', encoding='utf-8')
                open((rootdir + '\\images\\' + creation_time + '/MENU'), mode='w', encoding='utf-8')

                if extracting_video == '1':
                    ff.run()


# Locate gps trace products


def locate_files(filetype, matchfile, filepath, outputarray, rootdir):
    for dirPath, dirNames, fileNames in os.walk(rootdir):
        for fileName in fileNames:
            filePath = (os.path.join(dirPath, fileName))
            matchfile = re.match('.*' + filetype, filePath)
            if str(matchfile) != 'None':
                gpsFileName.append(fileName)
                filepath = (str(matchfile.group()))
                outputarray.append(filepath)


def generate_kml_and_csv(rootdir):
    column_names = 'filename,latitude,longitude,speed_kmh,bearing,timestamp\n'
    merged_trace = open(rootdir + '/' + '@GPS_Trace_Merged.log', mode='w', encoding='utf-8')
    merged_trace.write(column_names)
    for i in range(len(gpsFiles)):
        # print("i= " + str(i))
        g = open(str(gpsFiles[i]), mode='w', encoding='utf-8')
        h = open(str(htmlFiles[i]), mode='w', encoding='utf-8')
        g.write(column_names)

        # KML meta
        kml_meta_1 = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\" xmlns:kml=\"http://www.opengis.net/kml/2.2\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n<Document>\n ")
        h.write(kml_meta_1)
        h.write("<name>" + gpsFiles[i] + "</name>")
        kml_meta_2 = (
            "<Style id=\"sn_pink-blank\"><IconStyle><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/pink-blank.png</href></Icon><hotSpot x=\"32\" y=\"1\" xunits=\"pixels\" yunits=\"pixels\"/></IconStyle><ListStyle><ItemIcon><href>http://maps.google.com/mapfiles/kml/paddle/pink-blank-lv.png</href></ItemIcon></ListStyle></Style>\n<StyleMap id=\"msn_pink-blank\"><Pair><key>normal</key><styleUrl>#sn_pink-blank</styleUrl></Pair><Pair><key>highlight</key><styleUrl>#sh_pink-blank</styleUrl></Pair></StyleMap>")
        h.write(kml_meta_2)

        # iterate NMEA
        for j in range(len(movFiles)):
            # print("J= " + str(j))
            j = i
            f = open(str(movFiles[j][:len(str(movFiles[j])) - 4]) + '.NMEA', mode='r', encoding='utf-8')
            k = 0
            for line in f.readlines():
                if line[0:6] == '$GPRMC':
                    k += 1
                    msg = pynmea2.parse(line)
                    msg_seg = (str(msg).split(','))
                    utc_time = (msg_seg[1])[:6]
                    utc_date = (msg_seg[9])
                    timestamp = (
                        (msg_seg[9])[0:2] + '/' + (msg_seg[9])[2:4] + '/20' + (msg_seg[9])[4:6] + ' ' +
                        ((msg_seg[1])[:6])[0:2] + ':' + ((msg_seg[1])[:6])[2:4] + ':' +
                        ((msg_seg[1])[:6])[4:6]).replace('//20 ::', '').replace('//20 ', '')
                    #print(msg_seg[7], type(msg_seg[7]))
                    if msg_seg[7] != '':
                        speed = str(float(msg_seg[7]) * 1.85)
                    else:
                        speed = ''

                    bearing = (msg_seg[8])
                    utc_date = (msg_seg[9])

                    # CSV attributes
                    gps_parsed = ((gpsFileName[i] + '-' + str(k) + '.jpg').replace('.NMEA.csv', '') + ',' + str(
                        msg.latitude) + ',' + str(
                        msg.longitude) + ',' + speed + ',' + bearing + ',' + timestamp + '\n')
                    g.write(gps_parsed)
                    merged_trace.write(gps_parsed)

                    # KML attributes
                    attrib = gps_parsed.split(',')
                    if attrib[1] != '0.0' and attrib[2] != '0.0' and float(attrib[3]) >= 2.0:
                        h.write("<Placemark><description><![CDATA[<img src=\"./" + attrib[
                            0] + "\" width=\"720\"/>" + "<table><tr><th>filename</th><th>latitude</th><th>longitude</th><th>time_stamp</th><th>speed_kmh</th><th>bearing</th></tr><tr><th>" +
                                attrib[0] + "</th><th>" + attrib[1] + "</th><th>" + attrib[2] + "</th><th>" + attrib[
                                    5] + "</th><th>" + str(float(attrib[3]) * 1.852) + "</th><th>" + attrib[
                                    4] + "</th></tr></table>" + "]]></description><LookAt><longitude>" + attrib[
                                    2] + "</longitude><latitude>" + attrib[
                                    1] + "</latitude><altitude>0</altitude><gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode></LookAt><styleUrl>#sn_pink-blank</styleUrl><Point><gx:drawOrder>1</gx:drawOrder><coordinates>" +
                                attrib[2] + "," + attrib[1] + ",0</coordinates></Point></Placemark>")

            break
        h.write('</Document>\n</kml>')


def generate_dmo_trace(rootdir, format):
    for i in range(len(creation_time_list)):
        # print("i= " + str(i))
        g = open(str(menuFiles[i]), mode='w', encoding='utf-8')
        h = open(str(dmoGpsFiles[i]), mode='w', encoding='utf-8')
        for dirPath, dirNames, fileNames in os.walk(rootdir):
            for fileName in fileNames:
                filePath = (os.path.join(dirPath, fileName))
                matchnmea = re.match('.*\.[Nn][Mm][Ee][Aa]$', filePath)
                if str(matchnmea) != 'None':
                    nmeapath = str(matchnmea.group())
                    nmea_file_name = nmeapath.split('\\')[len(nmeapath.split('\\')) - 1][
                                     :len(nmeapath.split('\\')[len(nmeapath.split('\\')) - 1]) - 5]
                    nmea_creation_time = time.strftime('%m_%d_%y', time.gmtime(os.path.getmtime(nmeapath)))
                    j = i
                    l = 0
                    if nmea_creation_time == str(menuFiles[j]).split('\\')[len(str(menuFiles[j]).split('\\')) - 2]:
                        nmea_iterate = open(nmeapath, mode='r', encoding='utf8')
                        k = 1
                        for line in nmea_iterate.readlines():
                            if line[0:6] == '$GPRMC':
                                msg = pynmea2.parse(line)
                                msg_seg = (str(msg).split(','))
                                if msg_seg[8] != '':
                                    bearing = str(int(float(msg_seg[8])))
                                else:
                                    bearing = '0'
                                utc_time = (msg_seg[1])[:6]
                                utc_date = (msg_seg[9])
                                timestamp = (
                                    (msg_seg[9])[0:2] + '/' + (msg_seg[9])[2:4] + '/20' + (msg_seg[9])[4:6] + ' ' +
                                    ((msg_seg[1])[:6])[0:2] + ':' + ((msg_seg[1])[:6])[2:4] + ':' +
                                    ((msg_seg[1])[:6])[4:6])
                                if msg_seg[7] != '':
                                    gps_parsed = (str(msg.longitude) + ',' + str(
                                        msg.latitude) + ',' + bearing + ',1,' + str(
                                        float(msg_seg[7]) * 1.852) + ',' + timestamp + '\n').replace(',,', ',0,')
                                menu_parsed_rdf = (str(int(msg.latitude * 100000.0)) + '|' + str(
                                    int(msg.longitude * 100000.0)) + '|' + bearing + '|0|' + (
                                                       '.\\images\\' + nmea_creation_time + '\\' + nmea_file_name + '\\' + nmea_file_name + '-' + str(
                                                           k) + '.jpg').replace('.NMEA.csv', '') + '|0|\n').replace(
                                    '||', '|0|')
                                menu_parsed_atlas = (str(int(msg.latitude * 100000.0)) + '|' + str(
                                    int(msg.longitude * 100000.0)) + '|' + bearing + '|0|' + (
                                                         rootdir + '\\images\\' + nmea_creation_time + '\\' + nmea_file_name + '\\' + nmea_file_name + '-' + str(
                                                             k) + '.jpg').replace('.NMEA.csv', '') + '|0|\n').replace(
                                    '||', '|0|')
                                if (msg_seg[7]) != '':
                                    h.write(gps_parsed)
                                    if format == '1' and float(msg_seg[7]) >= 2:  # RDF
                                        g.write(menu_parsed_rdf)
                                    elif format == '2' and float(msg_seg[7]) >= 2:
                                        g.write(menu_parsed_atlas)
                                k += 1
                        l += 1
                    else:
                        j += 1
            break


'''
class PrintToApp(object):
    def write(self, s):
        console_window.insert(END, s)

def printtoapp():
    sys.stdout = PrintToApp()
'''
print("*************************************************")
print("** Welcome to dashcam video conversion tool V3 **")
print("*************************************************")
print("\n1. Input the valid root folder/directory of the video.")
print("\n2. Select the size of the image, the default is 720p."
      "\n(Or choose \"Original\" to have the best quality.)")
print("\n3. Select the style of Menu file of Atlas Project, the"
      "\ndeault is \"Relative path\", or choose \"Absolute Path\""
      "\nwhich is compatible for Atlas.")
print("\n4. Choose to extract the video or only extract/refresh"
      "\nthe GPS trace files.")
print("\n5. Press \"Go\" to start processing.")
print("\nFor any inquiry please contact: guan-ling.wu@here.com\n")

app = Tk()
app.resizable(0, 0)
app.title('Dashcam Video Tool')
app.geometry('580x240+600+300')


def quit():
    global app
    app.destroy()


def runner():
    print('----------------------------')
    ev = extracting_video.get()
    path = userInputString.get()
    mf = menu_format.get()
    create_dir(userInputString.get())
    res = res_selection.get()
    # app.wm_state('iconic')
    capture_frames(path, res, ev)
    locate_files('csv', 'matchGPS', 'gpsFilePath', gpsFiles, path)
    locate_files('kml', 'matchHtml', 'gpsHtmlPath', htmlFiles, path)
    locate_files('MENU', 'matchmenu', 'menupath', menuFiles, path)
    locate_files('gps', 'match_dmogps', 'dmogps_path', dmoGpsFiles, path)
    generate_kml_and_csv(path)
    generate_dmo_trace(path, mf)
    print('Process completed!')


dir_path = StringVar()
res_selection = StringVar()
res_selection.set('-s 1280x720')
menu_format = StringVar()
menu_format.set('1')
extracting_video = StringVar()
extracting_video.set('1')

Label(app, text='Root Dir of video:').grid(row=0, column=0, padx=10, pady=10, sticky=W)
userInputString = Entry(app, width=60)
userInputString.grid(row=0, padx=10, pady=10, column=1, columnspan=3, sticky=W)

Label(app, text='Image Resolution:').grid(row=1, column=0, padx=10, pady=10, sticky=W)
Radiobutton(app, text='Original', variable=res_selection, value=' ').grid(row=1, column=1, sticky=W)
Radiobutton(app, text='720p', variable=res_selection, value='-s 1280x720').grid(row=1, column=2, sticky=W)
Radiobutton(app, text='480p', variable=res_selection, value='-s 720x480').grid(row=1, column=3, sticky=W)
Label(app, text='').grid(row=1, column=4, padx=10, pady=10, sticky=W)

Label(app, text='Menu File Format:').grid(row=2, padx=10, pady=10, sticky=W)
Radiobutton(app, text='Relative Path (RDFViewer)', variable=menu_format, value='1').grid(row=2, column=1, sticky=W)
Radiobutton(app, text='Absolute Path (Atlas)', variable=menu_format, value='2').grid(row=2, column=2, sticky=W)

Label(app, text='Video or GPS Trace?').grid(row=3, padx=10, pady=10, sticky=W)
Radiobutton(app, text='Extract Video and GPS Trace', variable=extracting_video, value='1').grid(row=3, column=1, sticky=W)
Radiobutton(app, text='Only Extract GPS Trace', variable=extracting_video, value='0').grid(row=3, column=2, sticky=W)

go_button = Button(app, text='\n      GO!      \n', command=runner)
go_button.grid(row=4, columnspan=6, padx=10, pady=10, sticky=E)

app.mainloop()
