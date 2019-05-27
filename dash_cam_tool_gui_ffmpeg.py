import datetime
import os
import shutil
import subprocess
import threading
import time
import webbrowser
from tkinter import *
from tkinter import filedialog, messagebox

from PIL import Image
from ffmpy import FFmpeg

import gps_trace_processor

pm = True
v_file_formats = ['mpg', 'avi', 'mp4', 'mov', 'wmv']
t_file_formats = ['nmea', 'gpx']

creation_time_list = []
video_file_list = []
gps_trace_file_list = []
kml_file_list = []
menu_file_list = []
dmo_trace_file_list = []
csv_file_name_list = []


def create_dir(root_path):
    if not pm:
        if not os.path.exists(root_path + '/gps/'):
            os.mkdir(root_path + '/gps/', mode=777)
    if extracting_audio.get() == 1 and extracting_video.get() == 1:
        if not os.path.exists(root_path + '/audio/'):
            os.mkdir(root_path + '/audio/', mode=777)


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
                                            gps_trace_processor.file_creation_time_modifier(
                                                input_image,
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
    gps_trace_processor.locate_files('csv', 'matchGPS', 'gpsFilePath', gps_trace_file_list,
                                     output_path)
    gps_trace_processor.locate_files('kml', 'matchHtml', 'gpsHtmlPath', kml_file_list, output_path)
    gps_trace_processor.locate_files('MENU', 'matchmenu', 'menupath', menu_file_list, output_path)
    gps_trace_processor.locate_files('gps', 'match_dmogps', 'dmogps_path', dmo_trace_file_list,
                                     output_path)
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
        gps_trace_processor.generate_kml_and_csv(output_path, frame_interval, camera_orientation)
        if not pm:
            gps_trace_processor.generate_dmo_trace(output_path, mf, frame_interval,
                                                   camera_orientation)

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
