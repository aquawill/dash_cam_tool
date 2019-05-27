import os
import shutil
import time
from tkinter import *

import cv2
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
