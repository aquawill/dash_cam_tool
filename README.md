# dash_cam_tool

dash_cam_tool_161207
* Initial release.

dash_cam_tool_161222
* GUI for input and options.
* Image resolution can be selected, you can choose small size to preserve the disk usage or original for best quality. The default setting is resize to 720p for a quality/size balance.
* Now it produces Menu file of Altas, which means the log and image can be loaded with RDFViewer (Other -> DMO Projects -> Load DMO Project(s) then select the root directory of the video) and Atlas. Thus RMC/LMO members can also use this app if needed, and the video and trace can be easier shared. (Inspired by local LMO crews copied.)
* Now you can choose to extract video with GPS log or GPS log only.
* Now it produces a cumulated GPS log file “@GPSTraceMerged.log” in the folder of the video.
* All GPS logs (.gps) is now RME (Route Match Extension) compatible, you only need to add the column names (longitude,latitude,heading,null,speedkmh,timestamp) to the 1st line. Which can help identify potential database issues like missing turn restriction or incorrect restrictions, together with video.
* Minor bugs fixed.

dash_cam_tool_161228
* A critical bug fixed (file name recognization issue).

dash_cam_tool_170512
* Bug fixing release (incorrect speed value in CSV and KML traces).

dash_cam_tool_170911
* Adding new function of interpolation of GPS trace to provide double FPS of both trace and image.

dash_cam_tool_170914
* Minor bugs fixed (GPS trace interpolation errors).
* Add initial configuration storage to recall the previous setting.\
* Now frame capture will skip the corrupted video without quit.
* Add logging for corrupted video.
* Support GPX format trace and mp4 video input (for Garmin camcorder, run "run_gpx_mp4.bat").

dash_cam_tool_170922
* Add purging function to remove all gps/audio/image contents for re-processing or testing.
* Add EXIF injecting of GPS info to the jpeg images.

dash_cam_tool_180123
* New option to support VR image.
* Sync image file creation time with the video.
* Support more video formats (mpg, mov, avi, mpg, wmv).
* Can automatically detect video files without specifying file type.
* New option to extracting audio from video as MP3 files.
* New double check for purging.
* New button to send email to the author (me!).
* Improved UI representation.
* Several minor bugs fixed.

dash_cam_tool_v181023
* Fix miscellaneous issues.

dash_cam_tool_v181127
* Integrated Mapillary uploader (with Python 2.7 environment, bigger size).

dash_cam_tool_v190103
* Fix Mapillary Uploader issue.