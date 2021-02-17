import datetime
import os
import re
import time
from math import radians, cos, sin, degrees, atan2, atan, tan, acos

import gpxpy
import piexif
import platform
if platform.system() == 'Windows':
    from win32file import CreateFile, SetFileTime, CloseHandle, GENERIC_WRITE, OPEN_EXISTING


import common_variables


def locate_output_files(file_type, output_list, output):
    for dirPath, dirNames, fileNames in os.walk(output):
        for fileName in fileNames:
            input_file_path = os.path.join(dirPath, fileName)
            match_file = re.match('.*' + file_type, input_file_path)
            if match_file:
                common_variables.csv_file_name_list.append(fileName)
                file_path = str(match_file.group())
                output_list.append(file_path)


def gps_trace_interpolator(input_array):
    interpolating_date = input_array[-1][9]
    if input_array[-1][1] != '' and input_array[-2][1] != '':
        ahead_time = datetime.datetime.strptime('{:013.6f}'.format(float(interpolating_date + str(input_array[-1][1]))), '%d%m%y%H%M%S.%f')
        behind_time = datetime.datetime.strptime('{:013.6f}'.format(float(interpolating_date + str(input_array[-2][1]))), '%d%m%y%H%M%S.%f')
        interpolating_time = behind_time + ((ahead_time - behind_time) / 2)
        interpolating_time_str = interpolating_time.strftime('%H%M%S.%f')
    else:
        interpolating_time_str = float('{:013.6f}'.format(input_array[-1][1]))
    if input_array[-1][3] != '' and input_array[-2][3] != '':
        interpolating_lat = (float(input_array[-1][3]) + float(input_array[-2][3])) / 2
    else:
        interpolating_lat = input_array[-1][3]
    if input_array[-1][5] != '' and input_array[-2][5] != '':
        interpolating_lon = (float(input_array[-1][5]) + float(input_array[-2][5])) / 2
    else:
        interpolating_lon = input_array[-1][5]
    if input_array[-1][7] != '' and input_array[-2][7] != '':
        interpolating_speed = (float(input_array[-1][7]) + float(input_array[-2][7])) / 2
    else:
        interpolating_speed = str(input_array[-1][7])
    if input_array[-1][8] != '' and input_array[-2][8] != '':
        interpolating_bearing = (float(input_array[-1][8]) + float(input_array[-2][8])) / 2
    else:
        interpolating_bearing = input_array[-1][8]
    if input_array[-1][3] != '' and input_array[-2][3] != '':
        interpolating_array = [input_array[-1][0], interpolating_time_str, input_array[-1][2],
                               interpolating_lat, input_array[-1][4], interpolating_lon,
                               input_array[-1][6], interpolating_speed, interpolating_bearing,
                               interpolating_date, input_array[-1][10], input_array[-1][11],
                               input_array[-1][12]]
    else:
        interpolating_array = [input_array[-1][0], interpolating_time_str, input_array[-1][2],
                               input_array[-1][3], input_array[-1][4], input_array[-1][5],
                               input_array[-1][6], input_array[-1][7], input_array[-1][8],
                               interpolating_date, input_array[-1][10], input_array[-1][11],
                               input_array[-1][12]]
    return interpolating_array


def get_degree(lat_a, lng_a, lat_b, lng_b):
    radians_lat_a = radians(lat_a)
    radians_lon_a = radians(lng_a)
    radians_lat_b = radians(lat_b)
    rad_lon_b = radians(lng_b)
    distance_lon = rad_lon_b - radians_lon_a
    y = sin(distance_lon) * cos(radians_lat_b)
    x = cos(radians_lat_a) * sin(radians_lat_b) - sin(radians_lat_a) * cos(radians_lat_b) * cos(distance_lon)
    bearing = degrees(atan2(y, x))
    bearing = (bearing + 360) % 360
    return bearing


def get_distance(lat_a, lon_a, lat_b, lon_b):
    equator_radius = 6378140  # radius of equator: meter
    polar_radius = 6356755  # radius of polar: meter
    flatten = (equator_radius - polar_radius) / equator_radius  # Partial rate of the earth
    # change angle to radians
    rad_lat_a = radians(lat_a)
    rad_lon_a = radians(lon_a)
    rad_lat_b = radians(lat_b)
    rad_lon_b = radians(lon_b)

    p_a = atan(polar_radius / equator_radius * tan(rad_lat_a))
    p_b = atan(polar_radius / equator_radius * tan(rad_lat_b))
    x = acos(sin(p_a) * sin(p_b) + cos(p_a) * cos(p_b) * cos(rad_lon_a - rad_lon_b))
    c1 = (sin(x) - x) * (sin(p_a) + sin(p_b)) ** 2 / cos(x / 2) ** 2
    c2 = (sin(x) + x) * (sin(p_a) - sin(p_b)) ** 2 / sin(x / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = equator_radius * (x + dr)
    return distance


def gps_trace_iterator(trace_file_input, fr, camera_orientation):
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
                                lat_last_1 = output_array[-2][3] * -1
                            else:
                                lat_last_1 = output_array[-2][3]
                            if output_array[-2][6] == 'W':
                                lng_last_1 = output_array[-2][5] * -1
                            else:
                                lng_last_1 = output_array[-2][5]
                            if output_array[-1][4] == 'S':
                                lat_last_2 = output_array[-1][3] * -1
                            else:
                                lat_last_2 = output_array[-1][3]
                            if output_array[-1][6] == 'W':
                                lng_last_2 = output_array[-1][5] * -1
                            else:
                                lng_last_2 = output_array[-1][5]
                            try:
                                if lat_last_1 != lat_last_2 or lng_last_1 != lng_last_2:
                                    output_array[-2][7] = str(
                                        get_distance(lat_last_1, lng_last_1, lat_last_2,
                                                     lng_last_2) * 3.6)
                                    oriented_camera_direction = float(
                                        get_degree(lat_last_1, lng_last_1, lat_last_2,
                                                   lng_last_2)) + camera_orientation
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


def generate_kml_and_csv(root_dir, frame_interval, camera_orientation):
    global merged_trace
    column_names = 'filename,latitude,longitude,speed_kmh,bearing,timestamp\n'
    if not common_variables.pm:
        merged_trace = open(root_dir + '/GPS_Trace_Merged.log', mode='w', encoding='utf-8')
        merged_trace.write(column_names)
    for gps_file_index in range(len(common_variables.gps_trace_file_list)):
        gps_file = open(str(common_variables.gps_trace_file_list[gps_file_index]), mode='w',
                        encoding='utf-8')
        image_folder_path = os.path.dirname(
            str(common_variables.gps_trace_file_list[gps_file_index]))
        kml_file = open(str(common_variables.kml_file_list[gps_file_index]), mode='w',
                        encoding='utf-8')
        gps_file.write(column_names)
        # KML meta
        kml_meta_1 = (
            '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n<Document>\n')
        kml_file.write(kml_meta_1)
        kml_file.write(
            "<name>" + common_variables.gps_trace_file_list[gps_file_index] + "</name>\n")
        kml_meta_2 = (
            '<Style id="arrow_icon"><IconStyle><scale>1</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/track.png</href></Icon><hotSpot x="32" y="32" xunits="pixels" yunits="pixels"/></IconStyle></Style><Style id="idle_icon"><IconStyle><scale>1</scale><Icon><href>http://earth.google.com/images/kml-icons/track-directional/track-none.png</href></Icon><hotSpot x="32" y="32" xunits="pixels" yunits="pixels"/></IconStyle></Style>\n')
        kml_file.write(kml_meta_2)
        # iterate GPS trace
        for video_file_index in range(len(common_variables.video_file_list)):
            source_trace = None
            if os.path.basename(
                    common_variables.kml_file_list[gps_file_index]).lower().split('.')[0] == \
                    os.path.basename(
                        common_variables.video_file_list[video_file_index]).lower().split('.')[0]:
                # video_file_index = gps_file_index
                if common_variables.trace_file_format == 'nmea':
                    source_trace = open(
                        common_variables.video_file_list[video_file_index].split('.')[
                            0] + '.NMEA', mode='r', encoding='utf-8')
                elif common_variables.trace_file_format == 'gpx':
                    source_trace = open(
                        common_variables.video_file_list[video_file_index].split('.')[
                            0] + '.GPX', mode='r', encoding='utf-8')
                else:
                    if os.path.exists(
                            common_variables.video_file_list[video_file_index].split('.')[
                                0] + '.NMEA'):
                        source_trace = open(
                            common_variables.video_file_list[video_file_index].split('.')[
                                0] + '.NMEA', mode='r', encoding='utf-8', errors='ignore')
                    elif os.path.exists(
                            common_variables.video_file_list[video_file_index].split('.')[
                                0] + '.GPX'):
                        source_trace = open(
                            common_variables.video_file_list[video_file_index].split('.')[
                                0] + '.GPX', mode='r', encoding='utf-8', errors='ignore')
                    else:
                        print('No GPS trace file.')
            image_sn = 1
            if source_trace:
                msg_array = gps_trace_iterator(source_trace, frame_interval, camera_orientation)
                for msg_seg in msg_array:
                    bearing = None
                    icon_style = '<styleUrl>#idle_icon</styleUrl><Style>{}</Style>'
                    if msg_seg[8] != '':
                        bearing = str(int(float(msg_seg[8])))
                        icon_style = '<styleUrl>#arrow_icon</styleUrl><Style><IconStyle><heading>{}</heading></IconStyle></Style>'
                    speed = msg_seg[7]  #
                    date_time_tuple = datetime.datetime.strptime(str(msg_seg[9]).split('.')[0] + msg_seg[1], '%d%m%y%H%M%S.%f').replace(tzinfo=datetime.timezone.utc)
                    # CSV attributes
                    gps_parsed = '{},{},{},{},{},{}\n'.format(
                        (common_variables.csv_file_name_list[gps_file_index] + '-' + str(
                            image_sn) + '.jpg').replace(
                            '.csv', ''),
                        str(msg_seg[3]), str(msg_seg[5]), speed, bearing, date_time_tuple)
                    gps_file.write(gps_parsed)
                    if not common_variables.pm:
                        merged_trace.write(gps_parsed)
                    # KML attributes
                    gps_info_list = gps_parsed.split(',')
                    if speed != '':
                        kml_file.write(
                            "<Placemark><description><![CDATA[<img src=\"./" + gps_info_list[
                                0] + "\" width=\"720\"/>" +
                            "<table><tr><th>filename</th><th>latitude</th><th>longitude</th><th>time_stamp_utc"
                            "</th><th>speed_kmh</th><th>bearing</th></tr><tr><th>" + gps_info_list[
                                0] + "</th><th>" +
                            gps_info_list[1] + "</th><th>" + gps_info_list[2] + "</th><th>" +
                            gps_info_list[5].replace(
                                '\n',
                                '') + "</th><th>" +
                            str(float(gps_info_list[3]) * 1.852) + "</th><th>" + gps_info_list[
                                4] + "</th></tr></table>" +
                            "]]></description><LookAt><longitude>" + gps_info_list[
                                2] + "</longitude><latitude>" + gps_info_list[1] +
                            "</latitude><altitude>0</altitude><gx:altitudeMode>relativeToSeaFloor"
                            "</gx:altitudeMode><heading>" + gps_info_list[
                                4] + "</heading><tilt>0</tilt><range>"
                            + str(float(gps_info_list[3]) * 1.852 * 4 + 20) +
                            "</range></LookAt><styleUrl>#arrow_icon</styleUrl>" + icon_style.format(
                                gps_info_list[4]) + "<Point>"
                                                    "<gx:drawOrder>1</gx:drawOrder><coordinates>" +
                            gps_info_list[2] + "," + gps_info_list[
                                1] + ",0</coordinates></Point></Placemark>\n")
                        image_file_abspath = os.path.join(image_folder_path, gps_info_list[0])
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
    geo_tag_info = piexif.dump({'GPS': gps_ifd, 'Exif': exif_ifd})
    if os.path.exists(image):
        piexif.insert(geo_tag_info, image)


def file_creation_time_modifier(file_name, time_stamp):
    if platform.system() == 'Windows':
        file_creation_time = datetime.datetime.utcfromtimestamp(time_stamp).replace(
            tzinfo=datetime.timezone(datetime.timedelta(seconds=time.timezone)))
        handler = CreateFile(file_name, GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, 0)
        try:
            SetFileTime(handler, file_creation_time, file_creation_time, file_creation_time)
        except Exception:
            pass
        finally:
            CloseHandle(handler)
    elif platform.system() == 'Darwin':
        file_creation_time = datetime.datetime.utcfromtimestamp(time_stamp).replace(tzinfo=datetime.timezone.utc)
        os.system('SetFile -d "{}" {}'.format(file_creation_time.astimezone().strftime('%m/%d/%Y %H:%M:%S'), file_name))
        


def dmo_trace_file_generator(root_dir, output_file_format, frame_interval, camera_orientation):
    match_trace_file = None
    for creation_time_index in range(len(common_variables.creation_time_list)):
        menu_file = open(common_variables.menu_file_list[creation_time_index], mode='w',
                         encoding='utf-8')
        dmo_gps_file = open(common_variables.dmo_trace_file_list[creation_time_index],
                            mode='w', encoding='utf-8')
        for dirPath, dirNames, fileNames in os.walk(root_dir):
            for fileName in fileNames:
                file_path = (os.path.join(dirPath, fileName))
                if common_variables.trace_file_format != '':
                    if common_variables.t_file_formats.index(
                            common_variables.trace_file_format):
                        file_type = common_variables.t_file_formats[
                            common_variables.v_file_formats.index(
                                common_variables.video_file_format)]
                        file_type = re.compile('.*.' + file_type)
                        match_trace_file = re.match(file_type, file_path)
                else:
                    for i in common_variables.t_file_formats:
                        file_type = re.compile('.*.' + i)
                        if re.match(file_type, file_path.lower()):
                            match_trace_file = re.match(file_type, file_path.lower())
                if match_trace_file:
                    trace_file_path = str(match_trace_file.group())
                    trace_file_name = \
                        (trace_file_path.replace('\\', '/').split('/')[-1].split('.'))[0]
                    trace_file_creation_time = time.strftime('%m_%d_%y', time.gmtime(
                        os.path.getmtime(trace_file_path)))
                    video_file_index = creation_time_index
                    trace_file_index = 0
                    if trace_file_creation_time == \
                            common_variables.menu_file_list[video_file_index].replace('\\',
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
                            timestamp = str(
                                date_time_tuple.strftime('%d/%m/%y %H:%M:%S')) + '.' + str(
                                int(msg_seg[1].split('.')[1]))
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
                                    (root_dir + image).replace('.csv', ''),
                                    '0').replace('||', '|0|')
                                dmo_gps_file.write(gps_parsed + '\n')
                                if output_file_format == '1' and float(msg_seg[7]) > 0:  # RDF
                                    menu_file.write(menu_parsed_rdf)
                                elif output_file_format == '2' and float(msg_seg[7]) > 0:
                                    menu_file.write(menu_parsed_atlas)
                            image_sn += 1
                        trace_file_index += 1
                    else:
                        video_file_index += 1
            break
