import datetime
import os
import shutil
import subprocess
import threading
import time
import webbrowser
from tkinter import *
from tkinter import filedialog, messagebox

import gpxpy
import piexif
from PIL import Image
from ffmpy import FFmpeg
from math import radians, cos, sin, degrees, atan2, atan, tan, acos
from win32file import CreateFile, SetFileTime, CloseHandle, GENERIC_WRITE, OPEN_EXISTING

pm = True
v_file_formats = ['mpg', 'avi', 'mp4', 'mov', 'wmv']
t_file_formats = ['nmea', 'gpx']


def create_dir(rootdir):
    if not pm:
        if not os.path.exists(rootdir + '/gps/'):
            os.mkdir(rootdir + '/gps/', mode=777)
    if extracting_audio.get() == 1 and extracting_video.get() == 1:
        if not os.path.exists(rootdir + '/audio/'):
            os.mkdir(rootdir + '/audio/', mode=777)


def capture_frames(input, output, res, v, a, frame_interval, ph):
    global input_video_file_path
    app.wm_withdraw()
    for dirPath, dirNames, fileNames in os.walk(input):
        for fileName in fileNames:
            video_file_name = fileName
            filePath = os.path.join(dirPath, video_file_name)
            if video_file_format != '':
                if v_file_formats.index(video_file_format):
                    file_type = v_file_formats[v_file_formats.index(video_file_format)]
                    if os.path.basename(filePath).split('.')[-1].lower() == file_type:
                        input_video_file_path = filePath
            else:
                input_video_file_path = None
                for file_type in v_file_formats:
                    if os.path.basename(filePath).split('.')[-1].lower() == file_type:
                        input_video_file_path = filePath
            if input_video_file_path:
                full_time = time.strftime('%m_%d_%Y',
                                          time.gmtime(os.path.getctime(input_video_file_path)))
                if not pm:
                    creation_time = full_time[:6] + full_time[8:]
                else:
                    creation_time = full_time
                dmo_gps_file_name = time.strftime('%Y%m%d', time.gmtime(
                    os.path.getctime(input_video_file_path)))
                if not pm:
                    if not dmo_gps_file_name in creation_time_list:
                        creation_time_list.append(dmo_gps_file_name)
                else:
                    creation_time_list.append(dmo_gps_file_name)
                if not pm:
                    if not os.path.exists(output + '/gps/' + dmo_gps_file_name + '.gps'):
                        open(output + '/gps/' + dmo_gps_file_name + '.gps', mode='w',
                             encoding='utf8')
                if not os.path.exists(output + '/images/'):
                    os.mkdir(output + '/images/', mode=777)
                if not os.path.exists(output + '/images/' + creation_time + '/'):
                    os.mkdir(output + '/images/' + creation_time + '/', mode=777)
                pic_path = '{}/images/{}/{}'.format(output, creation_time,
                                                    str(os.path.relpath(input_video_file_path,
                                                                        os.path.abspath(input))))
                if not os.path.exists(pic_path.split('.')[0] + '/'):
                    os.mkdir(pic_path.split('.')[0] + '/', mode=777)
                video_file_list.append(input_video_file_path)
                # making trace files
                open('{}/{}.csv'.format(pic_path.split('.')[0], video_file_name.split('.')[0]),
                     mode='w',
                     encoding='utf-8')
                open('{}/{}.kml'.format(pic_path.split('.')[0], video_file_name.split('.')[0]),
                     mode='w',
                     encoding='utf-8')
                if not pm:
                    open('{}/images/{}/MENU'.format(output, creation_time), mode='w',
                         encoding='utf-8')
                input_fps = 1 / float(frame_interval);
                ff = FFmpeg(
                    inputs={input_video_file_path: None},
                    outputs={'{}/{}-%d.jpg'.format(
                        os.path.join(output, '/images/', pic_path.split('.')[0]),
                        str(fileName.split('.')[0])):
                                 '-vf fps={} {} -qscale:v 1 -loglevel -8'.format(input_fps, res)})
                ff_a = FFmpeg(
                    inputs={input_video_file_path: None},
                    outputs={'{}/{}/{}.mp3'.format(output, 'audio', str(fileName.split('.')[0])):
                                 '-f mp3 -ab 64000 -vn -loglevel -8 -y'})
                t_v = threading.Thread(target=ff.run)
                t_a = threading.Thread(target=ff_a.run)
                if v == 1:
                    try:
                        print('{} --> Extracting {}'.format(time.asctime(), input_video_file_path),
                              end='')
                        if ph == 1:
                            print(' (Panorama)')
                        else:
                            print('')
                        # """
                        t_v.start()
                        if a == 1:
                            t_a.start()
                            t_a.join()
                        t_v.join()
                        # """
                        video_ctime = datetime.datetime.utcfromtimestamp(
                            os.path.getctime(input_video_file_path)).timestamp()
                        e_threads = []
                        for fileNames in os.walk(
                                os.path.join(output, '/images/', pic_path.split('.')[0])):
                            for fileName in fileNames:
                                for image_file in fileName:
                                    image_file = os.path.join(output, '/images/',
                                                              pic_path.split('.')[0], image_file)
                                    if os.path.isfile(image_file) and str(image_file).split('.')[
                                        1] == 'jpg':
                                        def post_process(input_image):
                                            if ph == 1:
                                                img = Image.open(input_image)
                                                img_w = img.size[0]
                                                img_h = int(img_w / 2)
                                                img = img.resize((img_w, img_h), Image.ANTIALIAS)
                                                img.save(input_image)
                                                exiftool_cmd = 'exiftool.exe -ProjectionType="equirectangular" ' \
                                                               '-CroppedAreaImageWidthPixels={} ' \
                                                               '-CroppedAreaImageHeightPixels={} ' \
                                                               '-FullPanoWidthPixels={} -FullPanoHeightPixels={} ' \
                                                               '-CroppedAreaLeftPixels=0 -CroppedAreaTopPixels=0 {} ' \
                                                               '-overwrite_original'.format(
                                                    img_w, img_h, img_w, img_h, input_image)
                                                print('{} --> Generating Panorama: {}'.format(
                                                    time.asctime(),
                                                    input_image))
                                                subprocess.call(exiftool_cmd,
                                                                stdout=subprocess.PIPE,
                                                                stderr=subprocess.PIPE)
                                            time_offset = (float(
                                                str(input_image).split('.')[0].split('-')[
                                                    -1]) - 1) / input_fps
                                            file_creation_time_modifier(input_image,
                                                                        video_ctime + time_offset)

                                        t_e = threading.Thread(
                                            target=lambda: post_process(image_file))
                                        e_threads.append(t_e)
                                        for t in e_threads:
                                            try:
                                                t.start()
                                                time.sleep(0.1)
                                                e_threads.remove(t)
                                            except Exception:
                                                pass
                                            while True:
                                                if len(threading.enumerate()) < 5:
                                                    break
                    except Exception:
                        print(Exception.with_traceback())
                        # print('* ALERT: Unable to process ' + fileName + ', file seems corrupted.')
                        # print('* Log added --> ' + output + '/error_log.txt\n')
                        error_log = open(output + '/error_log.txt', mode='a', encoding='utf-8')
                        error_log.write(Exception.with_traceback() + '\n')
                        error_log.write(
                            '* {}\t{} seems corrupted.\n'.format(str(time.asctime()), input))
                        pass


def locate_files(filetype, matchfile, filepath, outputarray, output):
    for dirPath, dirNames, fileNames in os.walk(output):
        for fileName in fileNames:
            input_file_path = os.path.join(dirPath, fileName)
            matchfile = re.match('.*' + filetype, input_file_path)
            if matchfile:
                csv_file_name_list.append(fileName)
                filepath = str(matchfile.group())
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
        interpolating_speed = str(input_array[-1][7])
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


def get_distance(lat_a, lon_a, lat_b, lon_b):
    ra = 6378140  # radius of equator: meter
    rb = 6356755  # radius of polar: meter
    flatten = (ra - rb) / ra  # Partial rate of the earth
    # change angle to radians
    radLatA = radians(lat_a)
    radLonA = radians(lon_a)
    radLatB = radians(lat_b)
    radLonB = radians(lon_b)

    pA = atan(rb / ra * tan(radLatA))
    pB = atan(rb / ra * tan(radLatB))
    x = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(radLonA - radLonB))
    c1 = (sin(x) - x) * (sin(pA) + sin(pB)) ** 2 / cos(x / 2) ** 2
    c2 = (sin(x) + x) * (sin(pA) - sin(pB)) ** 2 / sin(x / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (x + dr)
    return distance


def gps_trace_iterator(trace_file_input, fr, camera_orientation):
    data_rate = 0
    if fr >= 1:
        data_rate = int(fr)
    else:
        data_rate = 1
    output_array = []
    file_type = trace_file_input.name.split('.')[-1].lower()
    line_number = 0
    if file_type == 'nmea':
        for nmea_line in trace_file_input.readlines():
            if nmea_line[0:6] == '$GPRMC':
                msg_seg = str(nmea_line).split(',')
                if float(msg_seg[1]) % 1.0 != 0:
                    msg_seg[1] = str(round(float(msg_seg[1]), 0))
                if msg_seg[3] != '':
                    msg_seg[3] = float(msg_seg[3][0:2]) + float(msg_seg[3][2:]) / 60  # lat
                if msg_seg[4] == 'S':
                    msg_seg[3] *= -1
                if msg_seg[5] != '':
                    msg_seg[5] = float(msg_seg[5][0:3]) + float(msg_seg[5][3:]) / 60  # lon
                if msg_seg[6] == 'W':
                    msg_seg[3] *= -1
                if msg_seg[7] == '':  # speed
                    msg_seg[8] = '0'
                if msg_seg[8] != '':  # bearing
                    oriented_camera_direction = int(float(msg_seg[8])) + camera_orientation
                    if oriented_camera_direction >= 360:
                        oriented_camera_direction -= 360
                    msg_seg[8] = oriented_camera_direction
                else:
                    msg_seg[8] = ''
                if line_number % data_rate == 0:
                    output_array.append(msg_seg)
                line_number += 1
                if fr == 0.5 and len(output_array) > 1:  # Interpolation of the GPS trace
                    interpolating_array = gps_trace_interpolator(output_array)
                    output_array.insert(-1, interpolating_array)
    elif file_type == 'gpx':
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
                    minute = points.time.strftime("%M")
                    sec = points.time.strftime("%S")
                    time_str = str(float('{}{}{}'.format(hour, minute, sec)))
                    date = ('{}{}{}'.format(date, month, year))
                    if line_number % data_rate == 0:
                        output_array.append(
                            ['GPX', time_str, 'A', abs(lat), ns, abs(lon), ew, '0.0', '0', date, '',
                             '', '\n'])
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
                                if latA != latB or lonA != lonB:
                                    output_array[-2][7] = str(
                                        get_distance(latA, lonA, latB, lonB) * 3.6)
                                    oriented_camera_direction = float(
                                        getDegree(latA, lonA, latB, lonB)) + camera_orientation
                                    if oriented_camera_direction > 360:
                                        oriented_camera_direction -= 360
                                    output_array[-2][8] = oriented_camera_direction
                            except Exception:
                                pass
                            if fr == 0.5 and len(
                                    output_array) > 1:  # Interpolation of the GPS trace
                                interpolating_array = gps_trace_interpolator(output_array)
                                output_array.insert(-1, interpolating_array)
                    line_number += 1
    return output_array


def generate_kml_and_csv(rootdir, frame_interval, camera_orientation):
    global merged_trace
    column_names = 'filename,latitude,longitude,speed_kmh,bearing,timestamp\n'
    if not pm:
        merged_trace = open(rootdir + '/GPS_Trace_Merged.log', mode='w', encoding='utf-8')
        merged_trace.write(column_names)
    for gps_file_index in range(len(gps_trace_file_list)):
        gps_file = open(str(gps_trace_file_list[gps_file_index]), mode='w', encoding='utf-8')
        image_folder_path = os.path.dirname(str(gps_trace_file_list[gps_file_index]))
        kml_file = open(str(kml_file_list[gps_file_index]), mode='w', encoding='utf-8')
        gps_file.write(column_names)
        # KML meta
        kml_meta_1 = (
            '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n<Document>\n')
        kml_file.write(kml_meta_1)
        kml_file.write("<name>" + gps_trace_file_list[gps_file_index] + "</name>\n")
        kml_meta_2 = (
            '<Style id="arrow_icon"><IconStyle><scale>1</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/track.png</href></Icon><hotSpot x="32" y="32" xunits="pixels" yunits="pixels"/></IconStyle></Style><Style id="idle_icon"><IconStyle><scale>1</scale><Icon><href>http://earth.google.com/images/kml-icons/track-directional/track-none.png</href></Icon><hotSpot x="32" y="32" xunits="pixels" yunits="pixels"/></IconStyle></Style>\n')
        kml_file.write(kml_meta_2)
        # iterate GPS trace
        for video_file_index in range(len(video_file_list)):
            source_trace = None
            if os.path.basename(kml_file_list[gps_file_index]).lower().split('.')[0] == \
                    os.path.basename(video_file_list[video_file_index]).lower().split('.')[0]:
                # video_file_index = gps_file_index
                if trace_file_format == 'nmea':
                    source_trace = open(video_file_list[video_file_index].split('.')[0] + '.NMEA',
                                        mode='r',
                                        encoding='utf-8')
                elif trace_file_format == 'gpx':
                    source_trace = open(video_file_list[video_file_index].split('.')[0] + '.GPX',
                                        mode='r',
                                        encoding='utf-8')
                else:
                    if os.path.exists(video_file_list[video_file_index].split('.')[0] + '.NMEA'):
                        source_trace = open(
                            video_file_list[video_file_index].split('.')[0] + '.NMEA', mode='r',
                            encoding='utf-8')
                    elif os.path.exists(video_file_list[video_file_index].split('.')[0] + '.GPX'):
                        source_trace = open(
                            video_file_list[video_file_index].split('.')[0] + '.GPX', mode='r',
                            encoding='utf-8')
            image_sn = 1
            if source_trace:
                msg_array = gps_trace_iterator(source_trace, frame_interval, camera_orientation)
                for msg_seg in msg_array:
                    bearing = None
                    icon_style = '<styleUrl>#idle_icon</styleUrl><Style>{}</Style>'
                    if msg_seg[8] != '':
                        bearing = str(int(float(msg_seg[8])))
                        icon_style = '<styleUrl>#arrow_icon</styleUrl><Style><IconStyle><heading>{}</heading></IconStyle></Style>'
                    speed = msg_seg[7]  # knots
                    date_time_tuple = datetime.datetime.strptime(
                        msg_seg[9].split('.')[0] + msg_seg[1].split('.')[0] + str(
                            int(msg_seg[1].split('.')[1]) * 100000), '%d%m%y%H%M%S%f')

                    # CSV attributes
                    gps_parsed = '{},{},{},{},{},{}\n'.format(
                        (csv_file_name_list[gps_file_index] + '-' + str(image_sn) + '.jpg').replace(
                            '.csv', ''),
                        str(msg_seg[3]), str(msg_seg[5]), speed, bearing, date_time_tuple)
                    gps_file.write(gps_parsed)
                    if not pm:
                        merged_trace.write(gps_parsed)
                    # KML attributes
                    attrib = gps_parsed.split(',')
                    if speed != '':
                        kml_file.write(
                            "<Placemark><description><![CDATA[<img src=\"./" + attrib[
                                0] + "\" width=\"720\"/>" +
                            "<table><tr><th>filename</th><th>latitude</th><th>longitude</th><th>time_stamp_utc"
                            "</th><th>speed_kmh</th><th>bearing</th></tr><tr><th>" + attrib[
                                0] + "</th><th>" +
                            attrib[1] + "</th><th>" + attrib[2] + "</th><th>" + attrib[5].replace(
                                '\n',
                                '') + "</th><th>" +
                            str(float(attrib[3]) * 1.852) + "</th><th>" + attrib[
                                4] + "</th></tr></table>" +
                            "]]></description><LookAt><longitude>" + attrib[
                                2] + "</longitude><latitude>" + attrib[1] +
                            "</latitude><altitude>0</altitude><gx:altitudeMode>relativeToSeaFloor"
                            "</gx:altitudeMode><heading>" + attrib[
                                4] + "</heading><tilt>0</tilt><range>"
                            + str(float(attrib[3]) * 1.852 * 4 + 20) +
                            "</range></LookAt><styleUrl>#arrow_icon</styleUrl>" + icon_style.format(
                                attrib[4]) + "<Point>"
                                             "<gx:drawOrder>1</gx:drawOrder><coordinates>" +
                            attrib[2] + "," + attrib[1] + ",0</coordinates></Point></Placemark>\n")
                        image_file_abspath = os.path.join(image_folder_path, attrib[0])
                        if os.path.exists(image_file_abspath):
                            try:
                                exif_injector(image_file_abspath, float(msg_seg[3]),
                                              float(msg_seg[5]), bearing,
                                              date_time_tuple, speed)
                                file_creation_time_modifier(image_file_abspath,
                                                            date_time_tuple.timestamp())
                            except Exception:
                                pass
                    image_sn += 1
                break
        kml_file.write('</Document>\n</kml>')


def exif_injector(image, decimal_lat, decimal_lon, direction, datetime_obj, speed):
    dms_formatter = lambda decimal: (int(decimal), int((float(decimal) - int(decimal)) * 60), round(
        (float((float(decimal) - int(decimal)) * 60) - int(
            (float(decimal) - int(decimal)) * 60)) * 6000))
    dms_lat = dms_formatter(decimal_lat)
    dms_lon = dms_formatter(decimal_lon)
    if decimal_lat >= 0:
        ns = b'N'
    else:
        ns = b'S'
    if decimal_lon >= 0:
        ew = b'E'
    else:
        ew = b'W'
    exif_datetime = datetime_obj.strftime(u'%Y:%m:%d %H:%M:%S')
    gps_ifd = {1: ns, 2: ((int(dms_lat[0]), 1), (int(dms_lat[1]), 1), (int(dms_lat[2]), 100)),
               3: ew,
               4: ((int(dms_lon[0]), 1), (int(dms_lon[1]), 1), (int(dms_lon[2]), 100)),
               13: (int(float(speed) * 100), 100), 12: b'K', 15: (int(direction), 1), 14: b'T'}

    exif_ifd = {piexif.ExifIFD.DateTimeOriginal: exif_datetime}
    geotag_info = piexif.dump({'GPS': gps_ifd, 'Exif': exif_ifd})
    if os.path.exists(image):
        piexif.insert(geotag_info, image)


def file_creation_time_modifier(file_name, time_stamp):
    file_creation_time = datetime.datetime.utcfromtimestamp(time_stamp).replace(
        tzinfo=datetime.timezone(datetime.timedelta(seconds=time.timezone)))
    handler = CreateFile(file_name, GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, 0)
    try:
        SetFileTime(handler, file_creation_time, file_creation_time, file_creation_time)
    except Exception:
        pass
    finally:
        CloseHandle(handler)


def generate_dmo_trace(rootdir, format, frame_interval, camera_orientation):
    match_trace_file = None
    for creation_time_index in range(len(creation_time_list)):
        menu_file = open(menu_file_list[creation_time_index], mode='w', encoding='utf-8')
        dmo_gps_file = open(dmo_trace_file_list[creation_time_index], mode='w', encoding='utf-8')
        for dirPath, dirNames, fileNames in os.walk(rootdir):
            for fileName in fileNames:
                filePath = (os.path.join(dirPath, fileName))
                if trace_file_format != '':
                    if t_file_formats.index(trace_file_format):
                        file_type = t_file_formats[v_file_formats.index(video_file_format)]
                        file_type = re.compile('.*.' + file_type)
                        match_trace_file = re.match(file_type, filePath)
                else:
                    for i in t_file_formats:
                        file_type = re.compile('.*.' + i)
                        if re.match(file_type, filePath.lower()):
                            match_trace_file = re.match(file_type, filePath.lower())
                if match_trace_file:
                    trace_file_path = str(match_trace_file.group())
                    trace_file_name = \
                        (trace_file_path.replace('\\', '/').split('/')[-1].split('.'))[0]
                    trace_file_creation_time = time.strftime('%m_%d_%y', time.gmtime(
                        os.path.getmtime(trace_file_path)))
                    video_file_index = creation_time_index
                    trace_file_index = 0
                    if trace_file_creation_time == \
                            menu_file_list[video_file_index].replace('\\', '/').split('/')[-2]:
                        trace_file_input = open(trace_file_path, mode='r', encoding='utf8')
                        image_sn = 1

                        msg_array = gps_trace_iterator(trace_file_input, frame_interval,
                                                       camera_orientation)
                        for msg_seg in msg_array:
                            bearing = None
                            if msg_seg[8] != '':
                                bearing = str(int(float(msg_seg[8])))
                            speed = msg_seg[7]
                            date_time_tuple = datetime.datetime.strptime(
                                msg_seg[9].split('.')[0] + msg_seg[1].split('.')[0], '%d%m%y%H%M%S')
                            timestamp = (str(
                                date_time_tuple.strftime('%d/%m/%y %H:%M:%S')) + '.' + str(
                                int(msg_seg[1].split('.')[1])))
                            image = '/images/{}/{}/{}-{}.jpg'.format(trace_file_creation_time,
                                                                     trace_file_name,
                                                                     trace_file_name, str(image_sn))
                            if speed != '' and int(float(speed)) != 0:
                                gps_parsed = '{},{},{},{},{},{}'.format(str(msg_seg[5]),
                                                                        str(msg_seg[3]), bearing,
                                                                        '1',
                                                                        str(float(
                                                                            msg_seg[7]) * 1.852),
                                                                        timestamp).replace(',,',
                                                                                           ',0,')
                                menu_parsed_rdf = '{}|{}|{}|{}|{}|0|\n'.format(
                                    str(int(float(msg_seg[3]) * 100000.0)),
                                    str(int(float(msg_seg[5]) * 100000.0)),
                                    bearing, '0',
                                    ('.' + image).replace('.csv', ''),
                                    '0').replace('||', '|0|')
                                menu_parsed_atlas = '{}|{}|{}|{}|{}|0|\n'.format(
                                    str(int(float(msg_seg[3]) * 100000.0)),
                                    str(int(float(msg_seg[5]) * 100000.0)),
                                    bearing, '0',
                                    (rootdir + image).replace('.csv', ''),
                                    '0').replace('||', '|0|')
                                dmo_gps_file.write(gps_parsed + '\n')
                                if format == '1' and float(msg_seg[7]) > 0:  # RDF
                                    menu_file.write(menu_parsed_rdf)
                                elif format == '2' and float(msg_seg[7]) > 0:
                                    menu_file.write(menu_parsed_atlas)
                            image_sn += 1
                        trace_file_index += 1
                    else:
                        video_file_index += 1
            break


def mapillary_uploader(image_path, uid):
    print('----------------------------')
    print('Start uploading to Mapillary')
    mapillary_tool_path = ''
    for dirPath, dirName, fileNames in os.walk(os.getcwd()):
        for fileName in fileNames:
            if fileName == 'mapillary_tools.exe':
                print(dirPath, fileName)
                mapillary_tool_path = os.path.join(dirPath, fileName)
                break
    mapillary_command = '{} process_and_upload --rerun --import_path "{}/images/" --user_name "{}"'.format(
        mapillary_tool_path, image_path, uid)
    print(mapillary_command)
    os.system(mapillary_command)


def quit():
    global app
    app.destroy()


def check_yesno():
    root_path = dest_path.get()
    if os.path.exists(dest_path.get()):
        if messagebox.askyesno("ARE YOU SURE?",
                               "CAUTION!\nALL EXISTING RESULTS WILL BE DELETED:\n{}\n{}\n{}".format(
                                   os.path.join(root_path, 'audio'),
                                   os.path.join(root_path, 'gps'),
                                   os.path.join(root_path, 'image')).replace('\\', '/')):
            purge()
    else:
        messagebox.showwarning("Error", "Invalid destination path, please check.")


def purge():
    finished = False
    root_path = dest_path.get()
    if os.path.exists(root_path + '/audio'):
        print('Purge all existing results - audio')
        shutil.rmtree(root_path + '/audio', ignore_errors=True)
        finished = True
    if os.path.exists(root_path + '/gps'):
        if not pm:
            print('Purge all existing results - gps')
        shutil.rmtree(root_path + '/gps', ignore_errors=True)
        finished = True
    if os.path.exists(root_path + '/images'):
        print('Purge all existing results - images')
        shutil.rmtree(root_path + '/images', ignore_errors=True)
        finished = True
    if os.path.exists(root_path + '/error_log.txt'):
        os.remove(root_path + '/error_log.txt')
        finished = True
    if os.path.exists(root_path + '/GPS_Trace_Merged.log'):
        os.remove(root_path + '/GPS_Trace_Merged.log')
        finished = True
    if finished:
        print('Done.')
    else:
        print('Results are empty.')


def runner():
    print('Task Starts!\n----------------------------')
    fr = frame_rate.get()
    ev = extracting_video.get()
    input_path = user_input_path.get().replace('\\', '/')
    output_path = dest_path.get().replace('\\', '/')
    mf = menu_format.get()
    res = res_selection.get()
    ph = pano_photo.get()
    m_uid = mapillary_user_name.get()
    init_config = open('./config.ini', mode='w')
    init_config.write(
        '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format(input_path, output_path, res,
                                                          extracting_audio.get(), mf, ev,
                                                          fr, ph, mapillary_uploader_switch.get(),
                                                          m_uid))
    init_config.close()
    if ev == 0:
        ea = 0
    else:
        ea = extracting_audio.get()
    create_dir(output_path)
    if frame_rate.get() == 2:
        frame_interval = 0.5
    elif frame_rate.get() == 1:
        frame_interval = 1.0
    else:
        frame_interval = float(interval_input.get())
    capture_frames(input_path, output_path, res, ev, ea, frame_interval, ph)
    locate_files('csv', 'matchGPS', 'gpsFilePath', gps_trace_file_list, output_path)
    locate_files('kml', 'matchHtml', 'gpsHtmlPath', kml_file_list, output_path)
    locate_files('MENU', 'matchmenu', 'menupath', menu_file_list, output_path)
    locate_files('gps', 'match_dmogps', 'dmogps_path', dmo_trace_file_list, output_path)
    # '↑ Front', '↓  Rear', '←  Left', '→ Right'
    camera_orientation = 0
    if camera_direction.get() == '→ Right':
        camera_orientation = 90
    elif camera_direction.get() == '↓  Rear':
        camera_orientation = 180
    elif camera_direction.get() == '←  Left':
        camera_orientation = 270
    elif camera_direction.get() == '↑ Front':
        camera_orientation = 0

    def trace_processor(output_path, mf, frame_interval, camera_orientation):
        generate_kml_and_csv(output_path, frame_interval, camera_orientation)
        if not pm:
            generate_dmo_trace(output_path, mf, frame_interval, camera_orientation)

    trace_processor(output_path, mf, frame_interval, camera_orientation)
    print('*** Process completed! ***\n')
    if os.path.exists(output_path + '/error_log.txt'):
        print('*** Some files couldn\'t be proccessed, Please check "error_log.txt". ***')
        os.system('notepad.exe ' + output_path + '/error_log.txt')
    # Mapillary uploader
    if mapillary_uploader_switch.get() == 1:
        mapillary_uploader(input_path, mapillary_uid)
    app.maxsize(0, 0)
    msg = messagebox.showinfo("Finished!", "Check folder: " + output_path)
    if msg == 'ok':
        quit()

if __name__ == '__main__':
    if len(sys.argv) > 1 and (
            str(sys.argv[1][1:]).lower() == 'gpx' or str(sys.argv[1][1:]).lower() == 'nmea') and (
            str(sys.argv[2][1:]).lower() == 'mov' or str(sys.argv[2][1:]).lower() == 'mp4'):
        trace_file_format = str(sys.argv[1][1:]).lower()
        video_file_format = str(sys.argv[2][1:]).lower()
    else:
        trace_file_format = ''
        video_file_format = ''

    if not pm:
        print("  **********************************************")
        print("  **       Dashcam video conversion tool      **")
        print('  **      Press "GO!" to start extraction.    **')
        print("  **********************************************")
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
    app.title(
        'Dashcam Video Tool {} {}'.format(trace_file_format.upper(), video_file_format.upper()))

    creation_time_list = []
    video_file_list = []
    gps_trace_file_list = []
    kml_file_list = []
    menu_file_list = []
    dmo_trace_file_list = []
    csv_file_name_list = []

    res_selection = StringVar()
    menu_format = StringVar()
    extracting_video = IntVar()
    # double_frame_rate = BooleanVar()
    frame_rate = IntVar()

    extracting_audio = IntVar()
    mapillary_uploader_switch = IntVar()
    pano_photo = IntVar()
    Label(app, text='Video Source:').grid(row=0, column=0, padx=10, pady=10, sticky=E)
    user_input_path = Entry(app, width=50)
    user_input_path.grid(row=0, padx=10, pady=10, column=1, columnspan=3, sticky=W)


    def path_selector(path):
        currdir = path.get()
        target = filedialog.askdirectory(parent=app, initialdir=currdir,
                                         title='Please select a directory')
        if len(target) > 0:
            path.delete(0, END)
            path.insert(0, target)
            return path


    Button(app, text='   ...   ', command=lambda: path_selector(user_input_path)).grid(row=0,
                                                                                       column=3,
                                                                                       padx=10,
                                                                                       pady=10,
                                                                                       sticky=E)
    Label(app, text='Destination:').grid(row=1, column=0, padx=10, pady=10, sticky=E)
    dest_path = Entry(app, width=50)
    dest_path.grid(row=1, padx=10, pady=10, column=1, columnspan=3, sticky=W)


    def copy_source_path():
        dest_path.delete(0, END)
        dest_path.insert(0, user_input_path.get())


    Button(app, text='   ...   ', command=lambda: path_selector(dest_path)).grid(row=1, column=3,
                                                                                 padx=10, pady=10,
                                                                                 sticky=E)
    Button(app, text='As Source', command=copy_source_path).grid(row=1, column=4, padx=10, pady=10,
                                                                 sticky=E)
    audio_switch = Checkbutton(app, text="Extract\nAudio", variable=extracting_audio,
                               state='disabled')
    audio_switch.select()
    audio_switch.grid(row=10, column=4, padx=10, pady=10, sticky=W)

    Label(app, text='Image Resolution:').grid(row=10, column=0, padx=10, pady=10, sticky=E)

    Label(app, text='Extractions:').grid(row=2, padx=10, pady=10, sticky=E)
    Radiobutton(app, text='Video and GPS Trace', variable=extracting_video, value=1,
                command=lambda: change_gps_state(1)).grid(row=2, column=1, sticky=W)
    Radiobutton(app, text='GPS Trace Only', variable=extracting_video, value=0,
                command=lambda: change_gps_state(0)).grid(row=2, column=2, sticky=W)


    def change_gps_state(value):
        if value == 1:
            ori = Radiobutton(app, text='Original', variable=res_selection, value=' ')
            ori.grid(row=10, column=1, sticky=W)
            e720p = Radiobutton(app, text='720p', variable=res_selection, value='-s 1280x720')
            e720p.grid(row=10, column=2, sticky=W)
            e480p = Radiobutton(app, text='480p', variable=res_selection, value='-s 853x480')
            e480p.grid(row=10, column=3, sticky=W)
            audio_switch = Checkbutton(app, text="Extract\nAudio", variable=extracting_audio)
            if extracting_audio.get() == 1:
                audio_switch.select()
            audio_switch.grid(row=10, column=4, padx=10, pady=10, sticky=W)
            pano_switch = Checkbutton(app, text="Panorama", variable=pano_photo)
            if pano_photo.get() == 1:
                pano_switch.select()
            pano_switch.grid(row=2, column=4, padx=10, pady=10, sticky=W)
        elif value == 0:
            ori = Radiobutton(app, text='Original', variable=res_selection, value=' ',
                              state='disabled')
            ori.grid(row=10, column=1, sticky=W)
            e720p = Radiobutton(app, text='720p', variable=res_selection, value='-s 1280x720',
                                state='disabled')
            e720p.grid(row=10, column=2, sticky=W)
            e480p = Radiobutton(app, text='480p', variable=res_selection, value='-s 853x480',
                                state='disabled')
            e480p.grid(row=10, column=3, sticky=W)
            audio_switch = Checkbutton(app, text="Extract\nAudio", variable=extracting_audio,
                                       state='disabled')
            audio_switch.grid(row=10, column=4, padx=10, pady=10, sticky=W)
            pano_switch = Checkbutton(app, text="Panorama", variable=pano_photo, state='disabled')
            pano_switch.grid(row=2, column=4, padx=10, pady=10, sticky=W)


    if extracting_video.get() == 0:
        change_gps_state(0)
    else:
        change_gps_state(1)


    def prerun():
        if frame_rate.get() == 0.0:
            if not int(float(interval_input.get())) >= 1:
                messagebox.showwarning("Error", "Invalid interval, please check.")
            else:
                if os.path.exists(user_input_path.get()) and os.path.exists(dest_path.get()):
                    runner()
                else:
                    messagebox.showwarning("Error", "Invalid path, please check.")
        else:
            if os.path.exists(user_input_path.get()) and os.path.exists(dest_path.get()):
                runner()
            else:
                messagebox.showwarning("Error", "Invalid path, please check.")


    go_button = Button(app, text='        GO!        ', command=prerun, bg='lightgreen')
    go_button.grid(row=40, column=4, padx=10, pady=10, sticky=E)

    if not pm:
        Label(app, text='Menu File Format:').grid(row=20, padx=10, pady=10, sticky=E)
        Radiobutton(app, text='Relative Path (RDFViewer)', variable=menu_format, value='1').grid(
            row=20, column=1,
            sticky=W)
        Radiobutton(app, text='Absolute Path (Atlas)', variable=menu_format, value='2').grid(row=20,
                                                                                             column=2,
                                                                                             sticky=W)

    Label(app, text='Orientation:').grid(row=20, column=3, sticky=E)
    camera_direction = StringVar(app)
    camera_direction.set('↑ Front')
    direction_selection = OptionMenu(app, camera_direction, '↑ Front', '↓  Rear', '←  Left',
                                     '→ Right').grid(row=20,
                                                     column=4)

    Label(app, text='Data Rate:').grid(row=40, padx=10, pady=10, sticky=E)
    fps_1 = Radiobutton(app, text='1 FPS (Default)', variable=frame_rate, value=1)
    fps_1.grid(row=40, column=1, sticky=W)
    fps_2 = Radiobutton(app, text='2 FPS', variable=frame_rate, value=2)
    fps_2.grid(row=40, column=2, sticky=W)
    time_lapse = Radiobutton(app, text='Time Lapse (Sec)', variable=frame_rate, value=0)
    time_lapse.grid(row=40, column=3, sticky=W)
    interval_input = Entry(app, width=3)
    interval_input.grid(row=40, padx=10, pady=10, column=3, sticky=E)

    purge_button = Button(app, text='Purge Results', command=check_yesno, bg='pink')
    purge_button.grid(row=50, column=4, padx=10, pady=10, sticky=E)

    Label(app, text='User Name:').grid(row=50, column=2, padx=10, pady=10, sticky=E)
    mapillary_user_name = Entry(app, width=20)
    mapillary_user_name.grid(row=50, padx=10, pady=10, column=3, sticky=W)
    mapillary_check_button = Checkbutton(app, text="Mapillary Uploader",
                                         variable=mapillary_uploader_switch)
    mapillary_check_button.grid(row=50, column=1, padx=10, pady=10, sticky=E)

    if not pm:
        author_email = 'mailto:guan-ling.wu@here.com'
    else:
        author_email = 'mailto:dashcam_tool_report@outlook.com'

    purge_button = Button(app, text='☺', command=lambda: webbrowser.open(author_email), bd=0)
    purge_button.grid(row=60, column=5, padx=0, pady=0, sticky=E)

    if os.path.exists('./config.ini'):
        init_config = open('./config.ini', mode='r')
        f = init_config.readlines()

        if len(f) > 8:
            root = f[0].replace('\n', '')
            dest = f[1].replace('\n', '')
            res_selection.set(f[2].replace('\n', ''))
            extracting_audio.set(int(f[3].replace('\n', '')))
            if extracting_audio.get() == 0:
                audio_switch.deselect()
            else:
                audio_switch.select()
            menu_format.set(f[4].replace('\n', ''))
            if int(f[5].replace('\n', '')) == 0:
                change_gps_state(0)
            else:
                change_gps_state(1)
            extracting_video.set(int(f[5].replace('\n', '')))
            frame_rate.set(int(f[6].replace('\n', '')))
            pano_photo.set(int(f[7].replace('\n', '')))
            mapillary_uploader_switch.set(int(f[8].replace('\n', '')))
            if mapillary_uploader_switch.get() == 1:
                mapillary_check_button.select()
            else:
                mapillary_check_button.deselect()
            mapillary_uid = f[9].replace('\n', '')
        else:
            root = ''
            dest = ''
            res_selection.set('-s 1280x720')
            change_gps_state(1)
            menu_format.set('1')
            pano_photo.set(0)
            extracting_video.set(1)
            extracting_audio.set(1)
            audio_switch.select()
            frame_rate.set(1)
            pano_photo.set(0)
            mapillary_uploader_switch.set(0)
            mapillary_uid = ''
        user_input_path.insert(0, root)
        dest_path.insert(0, dest)
        mapillary_user_name.insert(0, mapillary_uid)
    else:
        open('./config.ini', mode='w').close()
        root = ''
        dest = ''
        res_selection.set('-s 1280x720')
        change_gps_state(1)
        menu_format.set('1')
        extracting_video.set(1)
        extracting_audio.set(1)
        audio_switch.select()
        frame_rate.set(1)
        user_input_path.insert(0, '')
        pano_photo.set(0)
        mapillary_uploader_switch.set(0)
        mapillary_uid = ''

    app.mainloop()
