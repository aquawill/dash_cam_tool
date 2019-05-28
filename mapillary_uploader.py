import os


def mapillary_uploader(image_path, uid):
    print('----------------------------')
    print('Start uploading to Mapillary')
    mapillary_tool_path = ''
    for dirPath, dirName, fileNames in os.walk(os.getcwd()):
        for fileName in fileNames:
            if fileName == 'mapillary_tools.exe':
                mapillary_tool_path = os.path.join(dirPath, fileName)
                break
    mapillary_command = '{} process_and_upload --rerun --import_path "{}/images/" --user_name "{}"'.format(
        mapillary_tool_path, image_path, uid)
    print(mapillary_command)
    os.system(mapillary_command)
