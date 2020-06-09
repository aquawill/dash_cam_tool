import datetime
import os
import subprocess
import threading
import time
from tkinter import *

from PIL import Image
from ffmpy import FFmpeg
from pexpect import popen_spawn, EOF
from progressbar import ProgressBar

import common_variables
import gps_trace_processor

input_video_file_path = None


def ffmpeg_show_progress(cmd):
    video_duration = 0
    time_stamp = ''
    progress = 0
    thread = popen_spawn.PopenSpawn(cmd)
    cpl = thread.compile_pattern_list([EOF, 'time= *\d+', '.+'])
    while True:
        i = thread.expect_list(cpl, timeout=None)
        if thread.match.__class__.__name__ == 'Match':
            time_stamp = re.search('\d\d:\d\d:\d\d\.\d\d', thread.match.group(0).decode('utf-8'))
        if time_stamp:
            if i == 0:  # EOF
                print('')
                break
            elif i == 1:
                pass
            elif i == 2:
                time_stamp_list = time_stamp.group(0).split(':')
                hours = int(time_stamp_list[0])
                minutes = int(time_stamp_list[1])
                seconds = int(float(time_stamp_list[2]))
                if video_duration == 0:
                    video_duration = hours * 3600 + minutes * 60 + seconds
                    progress_bar = ProgressBar(maxval=video_duration)
                    progress_bar.start()
                else:
                    progress = hours * 3600 + minutes * 60 + seconds
                progress_bar.update(progress)


def capture_frames(input_dir, output_dir, resolution, extract_video, extract_audio, frame_interval, panorama):
    global input_video_file_path
    common_variables.app.wm_withdraw()
    for dirPath, dirNames, file_names in os.walk(input_dir):
        for file_name in file_names:
            video_file_name = file_name
            video_file_path = os.path.join(dirPath, video_file_name)
            if common_variables.video_file_format != '':
                if common_variables.v_file_formats.index(common_variables.video_file_format):
                    file_type = common_variables.v_file_formats[
                        common_variables.v_file_formats.index(common_variables.video_file_format)]
                    if os.path.basename(video_file_path).split('.')[-1].lower() == file_type:
                        input_video_file_path = video_file_path
            else:
                input_video_file_path = None
                for file_type in common_variables.v_file_formats:
                    if os.path.basename(video_file_path).split('.')[-1].lower() == file_type:
                        input_video_file_path = video_file_path
            if input_video_file_path:
                full_time = time.strftime('%m_%d_%Y',
                                          time.gmtime(os.path.getctime(input_video_file_path)))
                if not common_variables.pm:
                    creation_time = full_time[:6] + full_time[8:]
                else:
                    creation_time = full_time
                dmo_gps_file_name = time.strftime('%Y%m%d', time.gmtime(
                    os.path.getctime(input_video_file_path)))
                if not common_variables.pm:
                    if dmo_gps_file_name not in common_variables.creation_time_list:
                        common_variables.creation_time_list.append(dmo_gps_file_name)
                else:
                    common_variables.creation_time_list.append(dmo_gps_file_name)
                if not common_variables.pm:
                    if not os.path.exists(output_dir + '/gps/' + dmo_gps_file_name + '.gps'):
                        open(output_dir + '/gps/' + dmo_gps_file_name + '.gps', mode='w',
                             encoding='utf8')
                if not os.path.exists(output_dir + '/images/'):
                    os.mkdir(output_dir + '/images/', mode=777)
                if not os.path.exists(output_dir + '/images/' + creation_time + '/'):
                    os.mkdir(output_dir + '/images/' + creation_time + '/', mode=777)
                pic_path = '{}/images/{}/{}'.format(output_dir, creation_time,
                                                    str(os.path.relpath(input_video_file_path,
                                                                        os.path.abspath(input_dir))))
                if not os.path.exists(pic_path.split('.')[0] + '/'):
                    os.mkdir(pic_path.split('.')[0] + '/', mode=777)
                common_variables.video_file_list.append(input_video_file_path)
                # making trace files
                open('{}/{}.csv'.format(pic_path.split('.')[0], video_file_name.split('.')[0]),
                     mode='w',
                     encoding='utf-8')
                open('{}/{}.kml'.format(pic_path.split('.')[0], video_file_name.split('.')[0]),
                     mode='w',
                     encoding='utf-8')
                if not common_variables.pm:
                    open('{}/images/{}/MENU'.format(output_dir, creation_time), mode='w',
                         encoding='utf-8')
                input_fps = 1 / float(frame_interval);
                ff = FFmpeg(
                    inputs={input_video_file_path: None},
                    outputs={'{}/{}-%d.jpg'.format(
                        os.path.join(output_dir, '/images/', pic_path.split('.')[0]),
                        str(file_name.split('.')[0])):
                                 '-vf fps={} {} -qscale:v 1'.format(input_fps, resolution)})
                ff_a = FFmpeg(
                    inputs={input_video_file_path: None},
                    outputs={'{}/{}/{}.mp3'.format(output_dir, 'audio', str(file_name.split('.')[0])):
                                 '-f mp3 -ab 64000 -vn -y'})

                if extract_video == 1:
                    try:
                        print('{} --> Extracting {}'.format(time.asctime(), input_video_file_path),
                              end='')
                        if panorama == 1:
                            print(' (Panorama)')
                        else:
                            print('')
                        # """
                        print('Video: ')
                        ffmpeg_show_progress(ff.cmd)
                        if extract_audio == 1:
                            print('Audio: ')
                            ffmpeg_show_progress(ff_a.cmd)
                        # """
                        video_creation_time = datetime.datetime.utcfromtimestamp(
                            os.path.getctime(input_video_file_path)).timestamp()
                        e_threads = []
                        for file_names in os.walk(
                                os.path.join(output_dir, '/images/', pic_path.split('.')[0])):
                            for file_name in file_names:
                                for image_file in file_name:
                                    image_file = os.path.join(output_dir, '/images/',
                                                              pic_path.split('.')[0], image_file)
                                    if os.path.isfile(image_file) and str(image_file).split('.')[1] == 'jpg':
                                        def post_process(input_image):
                                            if panorama == 1:
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
                                            gps_trace_processor.file_creation_time_modifier(
                                                input_image,
                                                video_creation_time + time_offset)

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
                    except Exception as e:
                        print(e)
                        error_log = open(output_dir + '/error_log.txt', mode='a', encoding='utf-8')
                        error_log.write(e.__str__() + '\n')
                        error_log.write(
                            '* {}\t{} seems corrupted.\n'.format(str(time.asctime()), input_dir))
                        pass
