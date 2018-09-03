import datetime
import os
import shutil
import time
from math import radians, cos, sin, degrees, atan2, atan, tan, acos
from tkinter import *

import cv2
import gpxpy
import progressbar


def create_dir(rootdir):
    if not os.path.exists(rootdir):
        print('Invalid path, please try again...')
        quit()
    if not os.path.exists(rootdir + '/gps/'):
        os.mkdir(rootdir + '/gps/', mode=777)
    if not os.path.exists(rootdir + '/audio/'):
        os.mkdir(rootdir + '/audio/', mode=777)


def capture_frames(rootdir, res, extracting_video, dfr):
    app.destroy()
    for dirPath, dirNames, fileNames in os.walk(rootdir):
        for fileName in fileNames:
            filePath = (os.path.join(dirPath, fileName))
            if video_file_format == 'mov':
                matching_video_file = re.match('.*.[Mm][Oo][Vv]', filePath)
            elif video_file_format == 'mp4':
                matching_video_file = re.match('.*.[Mm][Pp][4]', filePath)
            if str(matching_video_file) != 'None':
                video_file_path = str(matching_video_file.group())
                full_time = time.strftime('%m_%d_%Y', time.gmtime(os.path.getmtime(video_file_path)))
                dmo_gps_file_name = time.strftime('%Y%m%d', time.gmtime(os.path.getmtime(video_file_path)))
                creation_time = full_time[:6] + full_time[8:]
                if not dmo_gps_file_name in creation_time_list:
                    creation_time_list.append(dmo_gps_file_name)
                if not os.path.exists(rootdir + '/gps/' + dmo_gps_file_name + '.gps'):
                    open(rootdir + '/gps/' + dmo_gps_file_name + '.gps', mode='w', encoding='utf8')
                if not os.path.exists(rootdir + '/images/'):
                    os.mkdir(rootdir + '/images/', mode=777)
                if not os.path.exists(rootdir + '/images/' + creation_time + '/'):
                    os.mkdir(rootdir + '/images/' + creation_time + '/', mode=777)
                pic_path = str(
                    rootdir + '/images/' + creation_time + str(matching_video_file.group()).replace(rootdir, ''))
                if not os.path.exists(pic_path.split('.')[0] + '/'):
                    os.mkdir(pic_path.split('.')[0] + '/', mode=777)
                video_file_list.append(video_file_path)
                if dfr is True:
                    output_fps = 2
                else:
                    output_fps = 1
                # making trace files
                open((pic_path.split('.')[0] + '/' + fileName[0:len(fileName) - 4] + '.csv'), mode='w',
                     encoding='utf-8')
                open((pic_path.split('.')[0] + '/' + fileName[0:len(fileName) - 4] + '.kml'), mode='w',
                     encoding='utf-8')
                open((rootdir + '/images/' + creation_time + '/MENU'), mode='w', encoding='utf-8')
                if extracting_video == '1':
                    vid = cv2.VideoCapture(video_file_path)
                    input_fps = vid.get(cv2.CAP_PROP_FPS)
                    video_length = vid.get(cv2.CAP_PROP_FRAME_COUNT)
                    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                    ratio = width / height
                    bar = progressbar.ProgressBar(maxval=round(video_length / input_fps, 2))
                    print('{} --> {} ({} frames/{} secs)'.format(time.asctime(), video_file_path, video_length,
                                                                 round(video_length / input_fps, 2)))
                    image_number = 1
                    frame_time = 0
                    try:
                        while frame_time < (video_length / input_fps) * 1000:
                            vid.set(cv2.CAP_PROP_POS_MSEC, frame_time)
                            success, image = vid.read()
                            if success:
                                if res != ' ':
                                    dest_width = int(float(res) * ratio)
                                    resize = cv2.resize(image, (int(dest_width), int(res)))  # CV2
                                else:
                                    resize = cv2.resize(image, (int(width), int(height)))
                                output_image_path = '{}//{}-{}.jpg'.format(pic_path.split('.')[0].replace('/', '//'),
                                                                           str(fileName.split('.')[0]), image_number)
                                cv2.imwrite(output_image_path, resize, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                                bar.update(frame_time / 1000)
                            else:
                                print('failed')
                            frame_time += (1 / int(output_fps)) * 1000
                            image_number += 1
                        else:
                            bar.finish()
                            continue
                    except Exception:
                        print('* ALERT: Unable to process ' + fileName + ', file seems corrupted.')
                        print('* Log added --> ' + rootdir + '/error_log.txt\n')
                        error_log = open(rootdir + '/error_log.txt', mode='a', encoding='utf-8')
                        error_log.write('* {}\t{} seems corrupted.\n'.format(str(time.asctime()), video_file_path))
                        pass


def locate_files(filetype, matchfile, filepath, outputarray, rootdir):
    for dirPath, dirNames, fileNames in os.walk(rootdir):
        for fileName in fileNames:
            filePath = (os.path.join(dirPath, fileName))
            matchfile = re.match('.*' + filetype, filePath)
            if str(matchfile) != 'None':
                csv_file_name_list.append(fileName)
                filepath = (str(matchfile.group()))
                outputarray.append(filepath)


def gps_trace_interpolator(input_array):
    if input_array[-1][1] != '' and input_array[-2][1] != '':
        interpolating_time = str(float(input_array[-2][1]) + 0.5)
    else:
        interpolating_time = input_array[-1][1]
    if len(interpolating_time.split('.')[0]) == 5:
        interpolating_time = '0' + interpolating_time
    if input_array[-1][3] != '' and input_array[-2][3] != '':
        interpolating_lat = str((float(input_array[-1][3]) + float(input_array[-2][3])) / 2)
    else:
        interpolating_lat = input_array[-1][3]
    if input_array[-1][5] != '' and input_array[-2][5] != '':
        interpolating_lon = str((float(input_array[-1][5]) + float(input_array[-2][5])) / 2)
    else:
        interpolating_lon = input_array[-1][5]
    if input_array[-1][7] != '' and input_array[-2][7] != '':
        interpolating_speed = str((float(input_array[-1][7]) + float(input_array[-2][7])) / 2)
    else:
        interpolating_speed = input_array[-1][7]
    if input_array[-1][8] != '' and input_array[-2][8] != '':
        interpolating_bearing = str((float(input_array[-1][8]) + float(input_array[-2][8])) / 2)
    else:
        interpolating_bearing = input_array[-1][8]
    interpolating_date = input_array[-1][9]
    if input_array[-1][3] != '' and input_array[-2][3] != '':
        interpolating_array = [input_array[-1][0], interpolating_time, input_array[-1][2],
                               interpolating_lat, input_array[-1][4], interpolating_lon,
                               input_array[-1][6], interpolating_speed, interpolating_bearing,
                               interpolating_date, input_array[-1][10], input_array[-1][11],
                               input_array[-1][12]]
    else:
        interpolating_array = [input_array[-1][0], interpolating_time, input_array[-1][2],
                               input_array[-1][3], input_array[-1][4], input_array[-1][5],
                               input_array[-1][6], input_array[-1][7], input_array[-1][8],
                               interpolating_date, input_array[-1][10], input_array[-1][11],
                               input_array[-1][12]]
    return interpolating_array


def getDegree(latA, lonA, latB, lonB):
    """
    Args:
        point p1(latA, lonA)
        point p2(latB, lonB)
    Returns:
        bearing between the two GPS points,
        default: the basis of heading direction is north
    """
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)
    dLon = radLonB - radLonA
    y = sin(dLon) * cos(radLatB)
    x = cos(radLatA) * sin(radLatB) - sin(radLatA) * cos(radLatB) * cos(dLon)
    brng = degrees(atan2(y, x))
    brng = (brng + 360) % 360
    return brng


def getDistance(latA, lonA, latB, lonB):
    ra = 6378140  # radius of equator: meter
    rb = 6356755  # radius of polar: meter
    flatten = (ra - rb) / ra  # Partial rate of the earth
    # change angle to radians
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)

    pA = atan(rb / ra * tan(radLatA))
    pB = atan(rb / ra * tan(radLatB))
    x = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(radLonA - radLonB))
    c1 = (sin(x) - x) * (sin(pA) + sin(pB)) ** 2 / cos(x / 2) ** 2
    c2 = (sin(x) + x) * (sin(pA) - sin(pB)) ** 2 / sin(x / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (x + dr)
    return distance


def gps_trace_iterator(trace_file_input, dfr):
    output_array = []
    print(trace_file_input.name)
    if trace_file_format == 'nmea':
        for nmea_line in trace_file_input.readlines():
            if nmea_line[0:6] == '$GPRMC':
                msg_seg = (str(nmea_line).split(','))
                if msg_seg[3] != '':
                    msg_seg[3] = float(msg_seg[3][0:2]) + float(msg_seg[3][2:]) / 60  # lat
                if msg_seg[4] == 'S':
                    msg_seg[3] *= -1
                if msg_seg[5] != '':
                    msg_seg[5] = float(msg_seg[5][0:3]) + float(msg_seg[5][3:]) / 60  # lon
                if msg_seg[6] == 'W':
                    msg_seg[3] *= -1
                if msg_seg[8] == '':
                    msg_seg[8] = '0'
                output_array.append(msg_seg)
                if dfr is True and len(output_array) > 1:  # Interpolation of the GPS trace
                    interpolating_array = gps_trace_interpolator(output_array)
                    output_array.insert(-1, interpolating_array)
    elif trace_file_format == 'gpx':
        gpx = gpxpy.parse(trace_file_input)
        for track in gpx.tracks:
            for segment in track.segments:
                for points in segment.points:
                    lat = points.latitude
                    if lat >= 0:
                        ns = 'N'
                    else:
                        ns = 'S'
                    lon = points.longitude
                    if lon >= 0:
                        ew = 'E'
                    else:
                        ew = 'W'
                    year = points.time.strftime("%y")
                    month = points.time.strftime("%m")
                    date = points.time.strftime("%d")
                    hour = points.time.strftime("%H")
                    min = points.time.strftime("%M")
                    sec = points.time.strftime("%S")
                    time = str(float('{}{}{}'.format(hour, min, sec)))
                    date = ('{}{}{}'.format(date, month, year))
                    output_array.append(
                        ['GPX', time, 'A', abs(lat), ns, abs(lon), ew, 0, 0, date, '', '', '\n'])
                    if len(output_array) > 1:
                        if output_array[-2][4] == 'S':
                            latA = output_array[-2][3] * -1
                        else:
                            latA = output_array[-2][3]
                        if output_array[-2][6] == 'W':
                            lonA = output_array[-2][5] * -1
                        else:
                            lonA = output_array[-2][5]
                        if output_array[-1][4] == 'S':
                            latB = output_array[-1][3] * -1
                        else:
                            latB = output_array[-1][3]
                        if output_array[-1][6] == 'W':
                            lonB = output_array[-1][5] * -1
                        else:
                            lonB = output_array[-1][5]
                        try:
                            if (latA != latB or lonA != lonB):
                                output_array[-2][7] = getDistance(latA, lonA, latB, lonB) * 3.6
                                output_array[-2][8] = float(getDegree(latA, lonA, latB, lonB))
                        except Exception:
                            pass
                        if dfr is True and len(output_array) > 1:  # Interpolation of the GPS trace
                            interpolating_array = gps_trace_interpolator(output_array)
                            output_array.insert(-1, interpolating_array)
    return output_array


def generate_kml_and_csv(rootdir, dfr):
    column_names = 'filename,latitude,longitude,speed_kmh,bearing,timestamp\n'
    merged_trace = open(rootdir + '/' + '@GPS_Trace_Merged.log', mode='w', encoding='utf-8')
    merged_trace.write(column_names)
    for gps_file_index in range(len(gps_trace_file_list)):
        gps_file = open(str(gps_trace_file_list[gps_file_index]), mode='w', encoding='utf-8')
        kml_file = open(str(kml_file_list[gps_file_index]), mode='w', encoding='utf-8')
        gps_file.write(column_names)
        # KML meta
        kml_meta_1 = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\" xmlns:kml=\"http://www.opengis.net/kml/2.2\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n<Document>\n ")
        kml_file.write(kml_meta_1)
        kml_file.write("<name>" + gps_trace_file_list[gps_file_index] + "</name>")
        kml_meta_2 = (
            "<Style id=\"sn_pink-blank\"><IconStyle><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/pink-blank.png</href></Icon><hotSpot x=\"32\" y=\"1\" xunits=\"pixels\" yunits=\"pixels\"/></IconStyle><ListStyle><ItemIcon><href>http://maps.google.com/mapfiles/kml/paddle/pink-blank-lv.png</href></ItemIcon></ListStyle></Style>\n<StyleMap id=\"msn_pink-blank\"><Pair><key>normal</key><styleUrl>#sn_pink-blank</styleUrl></Pair><Pair><key>highlight</key><styleUrl>#sh_pink-blank</styleUrl></Pair></StyleMap>")
        kml_file.write(kml_meta_2)
        # iterate GPS trace
        for mov_file_index in range(len(video_file_list)):
            mov_file_index = gps_file_index
            if trace_file_format == 'nmea':
                f = open(video_file_list[mov_file_index - 1].split('.')[0] + '.NMEA', mode='r', encoding='utf-8')
            elif trace_file_format == 'gpx':
                f = open(video_file_list[mov_file_index - 1].split('.')[0] + '.GPX', mode='r', encoding='utf-8')
            image_sn = 0
            msg_array = gps_trace_iterator(f, dfr)
            for msg_seg in msg_array:
                bearing = str(int(float(msg_seg[8])))
                speed = msg_seg[7]
                date_time_tuple = datetime.datetime.strptime(msg_seg[9].split('.')[0] + msg_seg[1].split('.')[0],
                                                             '%d%m%y%H%M%S')
                timestamp = (
                    str(date_time_tuple.strftime('%d/%m/%y %H:%M:%S')) + '.' + str(int(msg_seg[1].split('.')[1])))
                # CSV attributes
                gps_parsed = '{},{},{},{},{},{}\n'.format(
                    (csv_file_name_list[gps_file_index] + '-' + str(image_sn) + '.jpg').replace('.csv', ''),
                    str(msg_seg[3]), str(msg_seg[5]), speed, bearing, timestamp)
                gps_file.write(gps_parsed)
                merged_trace.write(gps_parsed)
                # KML attributes
                attrib = gps_parsed.split(',')
                if speed != '':
                    if attrib[1] != '0.0' and attrib[2] != '0.0' and float(speed) >= 2.0:
                        kml_file.write(
                            "<Placemark><description><![CDATA[<img src=\"./" + attrib[0] + "\" width=\"720\"/>" +
                            "<table><tr><th>filename</th><th>latitude</th><th>longitude</th><th>time_stamp"
                            "</th><th>speed_kmh</th><th>bearing</th></tr><tr><th>" + attrib[0] + "</th><th>" +
                            attrib[1] + "</th><th>" + attrib[2] + "</th><th>" + attrib[5] + "</th><th>" +
                            str(float(attrib[3]) * 1.852) + "</th><th>" + attrib[4] + "</th></tr></table>" +
                            "]]></description><LookAt><longitude>" + attrib[2] + "</longitude><latitude>" + attrib[1] +
                            "</latitude><altitude>0</altitude><gx:altitudeMode>relativeToSeaFloor"
                            "</gx:altitudeMode></LookAt><styleUrl>#sn_pink-blank</styleUrl><Point>"
                            "<gx:drawOrder>1</gx:drawOrder><coordinates>" +
                            attrib[2] + "," + attrib[1] + ",0</coordinates></Point></Placemark>")
                image_sn += 1
            break
        kml_file.write('</Document>\n</kml>')


def generate_dmo_trace(rootdir, format, dfr):
    for creation_type_index in range(len(creation_time_list)):
        menu_file = open(str(menu_file_list[creation_type_index]), mode='w', encoding='utf-8')
        dmo_gps_file = open(str(dmo_trace_file_list[creation_type_index]), mode='w', encoding='utf-8')
        for dirPath, dirNames, fileNames in os.walk(rootdir):
            for fileName in fileNames:
                filePath = (os.path.join(dirPath, fileName))
                if trace_file_format == 'nmea':
                    match_trace_file = re.match('.*\.[Nn][Mm][Ee][Aa]$', filePath)
                elif trace_file_format == 'gpx':
                    match_trace_file = re.match('.*\.[Gg][Pp][Xx]$', filePath)
                if str(match_trace_file) != 'None':
                    trace_file_path = str(match_trace_file.group())
                    trace_file_name = (trace_file_path.split('/')[-1].split('.'))[0]
                    trace_file_creation_time = time.strftime('%m_%d_%y', time.gmtime(os.path.getmtime(trace_file_path)))
                    mov_file_index = creation_type_index
                    trace_file_index = 0
                    if trace_file_creation_time == str(menu_file_list[mov_file_index]).split('/')[-2]:
                        trace_file_input = open(trace_file_path, mode='r', encoding='utf8')
                        image_sn = 1
                        msg_array = gps_trace_iterator(trace_file_input, dfr)
                        for msg_seg in msg_array:
                            bearing = str(int(float(msg_seg[8])))
                            speed = msg_seg[7]
                            date_time_tuple = datetime.datetime.strptime(
                                msg_seg[9].split('.')[0] + msg_seg[1].split('.')[0], '%d%m%y%H%M%S')
                            timestamp = (str(date_time_tuple.strftime('%d/%m/%y %H:%M:%S')) + '.' + str(
                                int(msg_seg[1].split('.')[1])))
                            if speed != '':
                                gps_parsed = '{},{},{},{},{},{}'.format(str(msg_seg[5]), str(msg_seg[3]), bearing, '1',
                                                                        str(float(msg_seg[7]) * 1.852),
                                                                        timestamp).replace(',,', ',0,')
                                menu_parsed_rdf = '{}|{}|{}|{}|{}|0|\n'.format(str(int(float(msg_seg[3]) * 100000.0)),
                                                                               str(int(float(msg_seg[5]) * 100000.0)),
                                                                               bearing, '0',
                                                                               ('./images/{}/{}/{}-{}.jpg'.format(
                                                                                   trace_file_creation_time,
                                                                                   trace_file_name, trace_file_name,
                                                                                   str(image_sn))).replace('.csv',
                                                                                                           ''),
                                                                               '0').replace('||', '|0|')
                                menu_parsed_atlas = '{}|{}|{}|{}|{}|0|\n'.format(str(int(float(msg_seg[3]) * 100000.0)),
                                                                                 str(int(float(msg_seg[5]) * 100000.0)),
                                                                                 bearing, '0',
                                                                                 (
                                                                                     '{}/images/{}/{}/{}-{}.jpg'.format(
                                                                                         rootdir,
                                                                                         trace_file_creation_time,
                                                                                         trace_file_name,
                                                                                         trace_file_name,
                                                                                         str(image_sn))).replace('.csv',
                                                                                                                 ''),
                                                                                 '0').replace('||', '|0|')
                                dmo_gps_file.write(gps_parsed + '\n')
                                if format == '1' and float(msg_seg[7]) >= 2:  # RDF
                                    menu_file.write(menu_parsed_rdf)
                                elif format == '2' and float(msg_seg[7]) >= 2:
                                    menu_file.write(menu_parsed_atlas)
                            image_sn += 1
                        trace_file_index += 1
                    else:
                        mov_file_index += 1
            break


def quit():
    global app
    app.destroy()


def purge():
    finished = False
    root_path = user_input_path.get()
    if os.path.exists(root_path + '/audio'):
        print('Purge all existing results - audio')
        shutil.rmtree(root_path + '/audio', ignore_errors=True)
        finished = True
    if os.path.exists(root_path + '/gps'):
        print('Purge all existing results - gps')
        shutil.rmtree(root_path + '/gps', ignore_errors=True)
        finished = True
    if os.path.exists(root_path + '/images'):
        print('Purge all existing results - images')
        shutil.rmtree(root_path + '/images', ignore_errors=True)
        finished = True
    if finished:
        print('Done.')
    else:
        print('Results are empty.')


def runner():
    print('----------------------------')
    dfr = double_frame_rate.get()
    ev = extracting_video.get()
    root_path = user_input_path.get()
    mf = menu_format.get()
    res = res_selection.get()

    init_config = open('./config.ini', mode='w')
    init_config.write(root_path + '\n')
    init_config.write(res + '\n')
    init_config.write(mf + '\n')
    init_config.write(ev + '\n')
    init_config.write(str(dfr) + '\n')
    init_config.close()

    create_dir(root_path)
    capture_frames(root_path, res, ev, dfr)
    print('Converting GPS traces...')
    locate_files('csv', 'matchGPS', 'gpsFilePath', gps_trace_file_list, root_path)
    locate_files('kml', 'matchHtml', 'gpsHtmlPath', kml_file_list, root_path)
    locate_files('MENU', 'matchmenu', 'menupath', menu_file_list, root_path)
    locate_files('gps', 'match_dmogps', 'dmogps_path', dmo_trace_file_list, root_path)
    generate_kml_and_csv(root_path, dfr)
    generate_dmo_trace(root_path, mf, dfr)
    print('*** Process completed! ***\n')
    if os.path.exists(root_path + '/error_log.txt'):
        print('*** Some files couldn\'t be proccessed, Please check "error_log.txt". ***')
        os.system('notepad.exe ' + root_path + '/error_log.txt')


if __name__ == '__main__':
    if len(sys.argv) > 1 and (str(sys.argv[1][1:]).lower() == 'gpx' or str(sys.argv[1][1:]).lower() == 'nmea') and (
                    str(sys.argv[2][1:]).lower() == 'mov' or str(sys.argv[2][1:]).lower() == 'mp4'):
        trace_file_format = str(sys.argv[1][1:]).lower()
        video_file_format = str(sys.argv[2][1:]).lower()
    else:
        trace_file_format = 'nmea'
        video_file_format = 'mov'

    print("  *************************************************")
    print("  ** Welcome to dashcam video conversion tool V3 **")
    print("  *************************************************")
    print("\n1. Input the valid root folder/directory of the video.")
    print("\n2. Select the size of the image, the default is 720p."
          "\n   (Or choose \"Original\" to have the best quality.)")
    print("\n3. Select the style of Menu file of Atlas Project, the"
          "\n   default is \"Relative path\", or choose \"Absolute Path\""
          "\n   which is compatible for Atlas.")
    print("\n4. Choose to extract the video or only extract/refresh"
          "\n   the GPS trace files.")
    print("\n5. Choose the frame rate per second/FPS, 1(Default) or 2.")
    print("\n6. Press \"Go\" to start processing.")
    print("\nFor any inquiry please contact: guan-ling.wu@here.com\n")

    app = Tk()
    app.resizable(0, 0)
    app.title('Dashcam Video Tool -{} -{}'.format(trace_file_format.upper(), video_file_format.upper()))
    app.geometry('700x240+600+300')

    creation_time_list = []
    video_file_list = []
    gps_trace_file_list = []
    kml_file_list = []
    menu_file_list = []
    dmo_trace_file_list = []
    csv_file_name_list = []

    res_selection = StringVar()
    menu_format = StringVar()
    extracting_video = StringVar()
    double_frame_rate = BooleanVar()

    Label(app, text='Root Path of Video:').grid(row=0, column=0, padx=10, pady=10, sticky=W)
    user_input_path = Entry(app, width=60)
    user_input_path.grid(row=0, padx=10, pady=10, column=1, columnspan=3, sticky=W)

    Label(app, text='Image Resolution:').grid(row=1, column=0, padx=10, pady=10, sticky=E)
    Radiobutton(app, text='Original', variable=res_selection, value=' ').grid(row=1, column=1, sticky=W)
    Radiobutton(app, text='720p', variable=res_selection, value='720').grid(row=1, column=2, sticky=W)
    Radiobutton(app, text='480p', variable=res_selection, value='480').grid(row=1, column=3, sticky=W)
    Label(app, text='').grid(row=1, column=4, padx=10, pady=10, sticky=W)

    Label(app, text='Menu File Format:').grid(row=2, padx=10, pady=10, sticky=E)
    Radiobutton(app, text='Relative Path (RDFViewer)', variable=menu_format, value='1').grid(row=2, column=1, sticky=W)
    Radiobutton(app, text='Absolute Path (Atlas)', variable=menu_format, value='2').grid(row=2, column=2, sticky=W)

    Label(app, text='Extractions:').grid(row=3, padx=10, pady=10, sticky=E)
    Radiobutton(app, text='Video and GPS Trace', variable=extracting_video, value='1').grid(row=3, column=1,
                                                                                            sticky=W)
    Radiobutton(app, text='GPS Trace Only', variable=extracting_video, value='0').grid(row=3, column=2, sticky=W)

    Label(app, text='Frame Rate:').grid(row=4, padx=10, pady=10, sticky=E)
    Radiobutton(app, text='1 FPS (Default)', variable=double_frame_rate, value=FALSE).grid(row=4, column=1, sticky=W)
    Radiobutton(app, text='2 FPS (Interpolation)', variable=double_frame_rate, value=TRUE).grid(row=4, column=2,
                                                                                                sticky=W)

    go_button = Button(app, text='        GO!        ', command=runner)
    go_button.grid(row=3, column=3, padx=10, pady=10, sticky=E)

    purge_button = Button(app, text='Purge Results', command=purge)
    purge_button.grid(row=4, column=3, padx=10, pady=10, sticky=E)

    if os.path.exists('./config.ini'):
        init_config = open('./config.ini', mode='r')
        f = init_config.readlines()
        if len(f) == 5:
            root = (f[0].replace('\n', ''))
            res_selection.set(f[1].replace('\n', ''))
            menu_format.set(f[2].replace('\n', ''))
            extracting_video.set(f[3].replace('\n', ''))
            double_frame_rate.set(f[4].replace('\n', ''))
        else:
            root = ''
            res_selection.set('720')
            menu_format.set('1')
            extracting_video.set('1')
            double_frame_rate.set(FALSE)
        user_input_path.insert(0, root)
    else:
        open('./config.ini', mode='w').close()
        root = ''
        res_selection.set('720')
        menu_format.set('1')
        extracting_video.set('1')
        double_frame_rate.set(FALSE)
        user_input_path.insert(0, '')
    app.mainloop()
