import datetime
import os
import re
import time

import gpxpy
import piexif
from math import radians, cos, sin, degrees, atan2, atan, tan, acos
from win32file import CreateFile, SetFileTime, CloseHandle, GENERIC_WRITE, OPEN_EXISTING

import dash_cam_tool_gui_ffmpeg


def locate_files(file_type, match_file, file_path, output_list, output):
    for dirPath, dirNames, fileNames in os.walk(output):
        for fileName in fileNames:
            input_file_path = os.path.join(dirPath, fileName)
            match_file = re.match('.*' + file_type, input_file_path)
            if match_file:
                dash_cam_tool_gui_ffmpeg.csv_file_name_list.append(fileName)
                file_path = str(match_file.group())
                output_list.append(file_path)


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
    if not dash_cam_tool_gui_ffmpeg.pm:
        merged_trace = open(rootdir + '/GPS_Trace_Merged.log', mode='w', encoding='utf-8')
        merged_trace.write(column_names)
    for gps_file_index in range(len(dash_cam_tool_gui_ffmpeg.gps_trace_file_list)):
        gps_file = open(str(dash_cam_tool_gui_ffmpeg.gps_trace_file_list[gps_file_index]), mode='w',
                        encoding='utf-8')
        image_folder_path = os.path.dirname(
            str(dash_cam_tool_gui_ffmpeg.gps_trace_file_list[gps_file_index]))
        kml_file = open(str(dash_cam_tool_gui_ffmpeg.kml_file_list[gps_file_index]), mode='w',
                        encoding='utf-8')
        gps_file.write(column_names)
        # KML meta
        kml_meta_1 = (
            '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n<Document>\n')
        kml_file.write(kml_meta_1)
        kml_file.write(
            "<name>" + dash_cam_tool_gui_ffmpeg.gps_trace_file_list[gps_file_index] + "</name>\n")
        kml_meta_2 = (
            '<Style id="arrow_icon"><IconStyle><scale>1</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/track.png</href></Icon><hotSpot x="32" y="32" xunits="pixels" yunits="pixels"/></IconStyle></Style><Style id="idle_icon"><IconStyle><scale>1</scale><Icon><href>http://earth.google.com/images/kml-icons/track-directional/track-none.png</href></Icon><hotSpot x="32" y="32" xunits="pixels" yunits="pixels"/></IconStyle></Style>\n')
        kml_file.write(kml_meta_2)
        # iterate GPS trace
        for video_file_index in range(len(dash_cam_tool_gui_ffmpeg.video_file_list)):
            source_trace = None
            if \
                    os.path.basename(
                        dash_cam_tool_gui_ffmpeg.kml_file_list[gps_file_index]).lower().split(
                        '.')[0] == \
                            os.path.basename(
                                dash_cam_tool_gui_ffmpeg.video_file_list[
                                    video_file_index]).lower().split(
                                '.')[0]:
                # video_file_index = gps_file_index
                if dash_cam_tool_gui_ffmpeg.trace_file_format == 'nmea':
                    source_trace = open(
                        dash_cam_tool_gui_ffmpeg.video_file_list[video_file_index].split('.')[
                            0] + '.NMEA',
                        mode='r',
                        encoding='utf-8')
                elif dash_cam_tool_gui_ffmpeg.trace_file_format == 'gpx':
                    source_trace = open(
                        dash_cam_tool_gui_ffmpeg.video_file_list[video_file_index].split('.')[
                            0] + '.GPX',
                        mode='r',
                        encoding='utf-8')
                else:
                    if os.path.exists(
                            dash_cam_tool_gui_ffmpeg.video_file_list[video_file_index].split('.')[
                                0] + '.NMEA'):
                        source_trace = open(
                            dash_cam_tool_gui_ffmpeg.video_file_list[video_file_index].split('.')[
                                0] + '.NMEA', mode='r',
                            encoding='utf-8')
                    elif os.path.exists(
                            dash_cam_tool_gui_ffmpeg.video_file_list[video_file_index].split('.')[
                                0] + '.GPX'):
                        source_trace = open(
                            dash_cam_tool_gui_ffmpeg.video_file_list[video_file_index].split('.')[
                                0] + '.GPX', mode='r',
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
                        (dash_cam_tool_gui_ffmpeg.csv_file_name_list[gps_file_index] + '-' + str(
                            image_sn) + '.jpg').replace(
                            '.csv', ''),
                        str(msg_seg[3]), str(msg_seg[5]), speed, bearing, date_time_tuple)
                    gps_file.write(gps_parsed)
                    if not dash_cam_tool_gui_ffmpeg.pm:
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
    for creation_time_index in range(len(dash_cam_tool_gui_ffmpeg.creation_time_list)):
        menu_file = open(dash_cam_tool_gui_ffmpeg.menu_file_list[creation_time_index], mode='w',
                         encoding='utf-8')
        dmo_gps_file = open(dash_cam_tool_gui_ffmpeg.dmo_trace_file_list[creation_time_index],
                            mode='w', encoding='utf-8')
        for dirPath, dirNames, fileNames in os.walk(rootdir):
            for fileName in fileNames:
                filePath = (os.path.join(dirPath, fileName))
                if dash_cam_tool_gui_ffmpeg.trace_file_format != '':
                    if dash_cam_tool_gui_ffmpeg.t_file_formats.index(
                            dash_cam_tool_gui_ffmpeg.trace_file_format):
                        file_type = dash_cam_tool_gui_ffmpeg.t_file_formats[
                            dash_cam_tool_gui_ffmpeg.v_file_formats.index(
                                dash_cam_tool_gui_ffmpeg.video_file_format)]
                        file_type = re.compile('.*.' + file_type)
                        match_trace_file = re.match(file_type, filePath)
                else:
                    for i in dash_cam_tool_gui_ffmpeg.t_file_formats:
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
                            dash_cam_tool_gui_ffmpeg.menu_file_list[video_file_index].replace('\\',
                                                                                              '/').split(
                                '/')[-2]:
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
