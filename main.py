import os
import shutil
import webbrowser
from tkinter import *
from tkinter import filedialog, messagebox
import sys

import common_variables
import gps_trace_processor
from frame_capturer import capture_frames


def create_dir(root_path):
    if not common_variables.pm:
        if not os.path.exists(root_path + '/gps/'):
            os.mkdir(root_path + '/gps/', mode=777)
    if extracting_audio.get() == 1 and extracting_video.get() == 1:
        if not os.path.exists(root_path + '/audio/'):
            os.mkdir(root_path + '/audio/', mode=777)


def quit_app():
    global app
    app.destroy()
    sys.exit()


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
        if not common_variables.pm:
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
    # m_uid = mapillary_user_name.get()
    init_config_file = open('./config.ini', mode='w')
    init_config_file.write(
        '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n'.format(input_path, output_path, res,
                                                          extracting_audio.get(), mf, ev,
                                                          fr, ph))
    init_config_file.close()
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
    gps_trace_processor.locate_output_files('csv', common_variables.gps_trace_file_list,
                                            output_path)
    gps_trace_processor.locate_output_files('kml', common_variables.kml_file_list, output_path)
    gps_trace_processor.locate_output_files('MENU', common_variables.menu_file_list, output_path)
    gps_trace_processor.locate_output_files('gps', common_variables.dmo_trace_file_list,
                                            output_path)

    camera_orientation = 0
    if camera_direction.get() == '→ Right':
        camera_orientation = 90
    elif camera_direction.get() == '↓  Rear':
        camera_orientation = 180
    elif camera_direction.get() == '←  Left':
        camera_orientation = 270
    elif camera_direction.get() == '↑ Front':
        camera_orientation = 0

    gps_trace_processor.generate_kml_and_csv(output_path, frame_interval, camera_orientation)
    if not common_variables.pm:
        gps_trace_processor.dmo_trace_file_generator(output_path, mf, frame_interval,
                                                     camera_orientation)

    print('*** Process completed! ***\n')
    if os.path.exists(output_path + '/error_log.txt'):
        print('*** Some files couldn\'t be proccessed, Please check "error_log.txt". ***')
        os.system('notepad.exe ' + output_path + '/error_log.txt')
    # Mapillary uploader
    app.maxsize(0, 0)
    msg = messagebox.showinfo("Finished!", "Check folder: " + output_path)
    if msg == 'ok':
        quit_app()


if __name__ == '__main__':
    if len(sys.argv) > 1 and (
            str(sys.argv[1][1:]).lower() == 'gpx' or str(sys.argv[1][1:]).lower() == 'nmea') and (
            str(sys.argv[2][1:]).lower() == 'mov' or str(sys.argv[2][1:]).lower() == 'mp4'):
        trace_file_format = str(sys.argv[1][1:]).lower()
        video_file_format = str(sys.argv[2][1:]).lower()
    else:
        trace_file_format = ''
        video_file_format = ''

    if not common_variables.pm:
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

    app = common_variables.app
    app.resizable(0, 0)
    app.title(
        'Dashcam Video Tool {} {}'.format(trace_file_format.upper(), video_file_format.upper()))

    res_selection = StringVar()
    menu_format = StringVar()
    extracting_video = IntVar()
    # double_frame_rate = BooleanVar()
    frame_rate = IntVar()

    extracting_audio = IntVar()
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
            extract_original_button = Radiobutton(app, text='Original', variable=res_selection, value=' ')
            extract_original_button.grid(row=10, column=1, sticky=W)
            extract_720p_button = Radiobutton(app, text='720p', variable=res_selection, value='-s 1280x720')
            extract_720p_button.grid(row=10, column=2, sticky=W)
            extract_480p_button = Radiobutton(app, text='480p', variable=res_selection, value='-s 853x480')
            extract_480p_button.grid(row=10, column=3, sticky=W)
            extract_audio_check_button = Checkbutton(app, text="Extract\nAudio", variable=extracting_audio)
            if extracting_audio.get() == 1:
                extract_audio_check_button.select()
            extract_audio_check_button.grid(row=10, column=4, padx=10, pady=10, sticky=W)
            panorama_check_button = Checkbutton(app, text="Panorama", variable=pano_photo)
            if pano_photo.get() == 1:
                panorama_check_button.select()
            panorama_check_button.grid(row=2, column=4, padx=10, pady=10, sticky=W)
        elif value == 0:
            extract_original_button = Radiobutton(app, text='Original', variable=res_selection, value=' ', state='disabled')
            extract_original_button.grid(row=10, column=1, sticky=W)
            extract_720p_button = Radiobutton(app, text='720p', variable=res_selection, value='-s 1280x720', state='disabled')
            extract_720p_button.grid(row=10, column=2, sticky=W)
            extract_480p_button = Radiobutton(app, text='480p', variable=res_selection, value='-s 853x480', state='disabled')
            extract_480p_button.grid(row=10, column=3, sticky=W)
            extract_audio_check_button = Checkbutton(app, text="Extract\nAudio", variable=extracting_audio, state='disabled')
            extract_audio_check_button.grid(row=10, column=4, padx=10, pady=10, sticky=W)
            panorama_check_button = Checkbutton(app, text="Panorama", variable=pano_photo, state='disabled')
            panorama_check_button.grid(row=2, column=4, padx=10, pady=10, sticky=W)


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
    go_button.grid(row=50, column=3, padx=10, pady=10, sticky=E)

    if not common_variables.pm:
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
    interval_input.grid(row=40, column=4, pady=10, sticky=W)

    purge_button = Button(app, text='Purge Results', command=check_yesno, bg='pink')
    purge_button.grid(row=50, column=4, padx=10, pady=10, sticky=E)

    if not common_variables.pm:
        author_email = 'mailto:guan-ling.wu@here.com'
    else:
        author_email = 'mailto:dashcam_tool_report@outlook.com'

    mail_button = Button(app, text='☺', command=lambda: webbrowser.open(author_email), bd=0)
    mail_button.grid(row=60, column=5, padx=0, pady=0, sticky=E)

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
            mapillary_uid = ''
        user_input_path.insert(0, root)
        dest_path.insert(0, dest)
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
        mapillary_uid = ''

    app.mainloop()
