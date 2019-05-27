Dash Cam Tool
===

有時候會在網路上面看到有人在求行車紀錄器檔案，或是為了過往的行車紀錄器紀錄已經被刪除難以舉證而感到困擾，我常在想，如果有更多的人有備份行車紀錄器的檔案，這樣的問題應該會比較少吧！不過備份這件事情說起來很簡單，但是做起來問題卻很多，例如：

一、想要把每天的行車紀錄器影片都備份下來，但是影片太龐大，硬碟快被塞滿了，就算上傳到雲端，也要非常久的時間。
二、影片跟軌跡是分開的檔案，這樣一定要用原廠軟體才可以查到影片當下的拍攝位置。可是原廠軟體通常也不是那麼好用，如果影片數量多的話更是麻煩。
三、如果要把影片上傳到雲端，就沒辦法結合GPS的資料。
四、行車記錄器的GPS軌跡原始檔不知道要用什麼軟體開啟。
五、不想多花錢買額外的儲存設備，但又希望可以有一個簡單快速備份的方法。
六、希望可以隨時隨地查閱之前的行車紀錄器存檔，不用一定要回家開電腦。

因為有了以上的困擾，所以我開發了一個小小工具軟體，希望能夠節省大家的精力。這個小軟體主要的功能有：
一、把行車記錄器的影片，以一秒擷取一格或半秒擷取一格的方式存成JPG圖檔。
二、用影片拍攝的時間與GPS軌跡的時間來校正JPG圖檔的拍攝時間。
三、把GPS的位置資料寫入JPG圖檔。
四、綜合以上三點，我們可以把這些圖檔全部上傳到Google Photo無限量的網路空間進行備份，並且還帶有位置資料，如下圖：

![](https://i.imgur.com/BsQSRKZ.jpg)

範例一: https://photos.app.goo.gl/41phWYD2MyxQn2LP2
範例二: https://photos.app.goo.gl/TkrnWXR4Ulc8I6xT2

另外，這個小工具也有以下特色：

1. 如果您的行車記錄器本身有GPS的功能，此軟體會把軌跡轉成KML格式，用Google Earth開啟，可連結到照片。
    ![](https://i.imgur.com/sGQa2MM.png)

2. 如果沒有GPS軌跡可以用來校正影像的拍攝時間也沒關係，程式會使用影片的拍攝時間來計算，因此只要確定您的行車記錄器時間是準的就可以了。例如下圖是一秒擷取一張圖檔的成果，編號相差20號的「建立時間（也就是換算出的拍攝時間）」也會差20秒。
    ![](https://i.imgur.com/ipFE3zO.jpg)

3. 如果您使用的是全景攝影機拍攝全景影片（如Garmin Virb 360），此軟體也可以把轉出的影像檔轉成全景格式，因此備份到Google Photo、Facebook、Flickr的時候也可以用VR模式瀏覽。
例如（[下圖](https://flic.kr/p/22maft4)）:
    ![](https://i.imgur.com/SSK8otE.jpg)

4. 您也可以使用此軟體把行車記錄器的影像備份到Mapillay （https://www.mapillary.com/）。
    ![](https://i.imgur.com/b2d6aRR.png)

此軟體開放個人免費使用，請勿用於商業用途，謝謝。


## UI

![](https://i.imgur.com/0oQzdeo.png)

* Video Source： 存放行車記錄器影片的資料夾。
* Destination： 轉出後的影像檔預計存放的資料夾。
* As Source：將Destination設定與Video Source一致。
* Extractions：選擇同時處理 1)影片與GPS軌跡，或是 2)只處理GPS軌跡。
* Image Resolution：輸出圖檔的解析度。
* Panorama：如果您的攝影機是全景攝影機（如GARMIN Virb 360）請選擇此選項。
* Extract Audio：將影片檔的音軌另存成mp3檔。
* Data Rate：可選擇 1)每秒一格 2)每秒兩格 3)縮時攝影（自訂秒數）
* Mapillary Uploader：若您想把影像上傳到Mapillary，請勾選此選項，並在User Name輸入您在Mapillary的帳號名稱。
* Orientation：可用來設定攝影機的拍攝方向，有前後左右可選，此選項適用於車上有不只一個行車記錄器的使用者，在轉出後的KML可以顯示拍攝方向。
* Purge Results：清除Destination之中已經轉出過的影像、軌跡、音軌等資料。 
* Go：設定完畢後，開始作業。

## 使用方法

1. 下載後解壓縮到您想要的任何地方，執行「行車紀錄器轉檔工具.bat」或「run.bat」。
2. 請確定所有的軌跡跟行車記錄器都放在同一個資料夾下，軌跡檔跟對應的行車記錄器影片必須相同檔名！
    ![](https://i.imgur.com/jF3MrfA.jpg)

4. 把Video Source指定為您放置行車記錄器影片跟軌跡的資料夾，Destination指定到您要輸出的目的地資料夾，並依照您的需求設定相關選項。
5. 按下GO之後就會開始處理，會有一個黑色終端機視窗顯示目前進度，結束後會自動關閉。您可在目的地資料夾的Images --> 拍攝日期 --> 影片檔名中看到轉出的JPG圖檔與軌跡。

    ![](https://i.imgur.com/y9DIbf6.jpg)

5. 如果有轉出聲音為MP3檔的話，則會在目的地資料夾中的audio資料夾。

6. 縮時攝影的功能，可以指定自訂的秒數間隔來擷取影像（感謝熱心使用者回報此需求）。請選擇Time Lapse之後輸入您要自訂的間隔秒數，秒數的長短並沒有限制。
    ![](https://i.imgur.com/eWkpR1d.png)

7. 要把影像備份到Mapillary的話，請先到Mapillary申請帳號，之後再使用這個工具上傳。如果要啟用這個功能，請先勾選Mapillary Uploader，然後在右邊輸入自己在Mapillary的帳號名稱。
    ![](https://i.imgur.com/eD3M3k2.png)

    第一次使用這功能的時候，會在上傳之前提示需要輸入您在Mapillary上面註冊的電子郵件信箱以及密碼，請輸入後按下enter，就會繼續處理。
    ![](https://i.imgur.com/Rkh1fZY.png)



8. 您可以使用Google Photo軟體(https://photos.google.com/apps?hl=zh-TW)，設定自動上傳的目錄為您的目的地資料夾，就可以把所有的行車紀錄器影像都備份到Google Photo上面。

    ![](https://i.imgur.com/mLMroDD.jpg)

* 相關說明: http://www.playpcesor.com/2017/07/google-Backup-and-Sync-from-download.html
* 不管在手機上還是電腦上，都可以直接在Google Photo裡面直接輸入年月，甚至是地名來查詢影像。

    ![](https://i.imgur.com/YCFeSQm.jpg)
    ![](https://i.imgur.com/EWbvMxx.jpg)




## FAQ

1. 怎麼知道我的行車紀錄器能不能相容這個工具?
    * 只要符合以下規則就可以相容:
        * 影片格式:MOV、AVI、WMV、MP4、MPG。
        * GPS軌跡格式:GPX、MNEA。
        * GPS軌跡的長度與影片相等。
        * GPS軌跡每秒紀錄一點。
        * 影片與GPS軌跡,檔名必須相同。
        * 影片與GPS軌跡,必須擺在同一個資料夾下。
        * 作者無法一一買來測試,因此只能麻煩您自己試試看了。
2. 如果我的行車紀錄器沒有GPS功能,可以使用這個工具嗎?
    * 可以,不過就沒有GPS軌跡轉檔跟對應的功能。
3. 此工具程式支援多核心嗎?
    * 可以。
4. 為什麼我的電腦不能跑?
    * 僅支援Windows 64位元系統。
    * 如果您的電腦為Windows 64位元系統但不能執行,請聯絡作者協助診斷。
5. 為什麼有些影片無法轉檔?
    * 可能格式不相容( MOV、AVI、WMV、MP4、MPG )
    * 可能影片檔損壞,例如還在錄影中就拔出記憶卡會造成影片寫入不完全而無法讀取。這種壞檔會被跳過。
6. 為什麼轉檔這麼慢?
    * 轉檔功能使用的是FFMPEG(https://www.ffmpeg.org/)。愈快的電腦，轉檔當然愈快。
    * 使用Panorama全景模式轉檔會更耗時間,因為要把影像檔轉換成可以支援VR功能的格式。
7. 為什麼影像檔的GPS位置不正確。
    * GPS資訊來自於行車紀錄器所記錄的GPS資料,而GPS是可能會有誤差的。
    * 如果實在相差太遠,請聯絡作者協助分析。
8. 為什麼影像的建立時間跟行車紀錄器的顯示在影片上面的有誤差?
    * 由於影像的建立時間是用影片的拍攝時間換算,經過實測,可能會有一秒至一秒半的誤差。
9. 為何KML上面記錄的速度跟行車紀錄器顯示在影片上面的不同。
    * KML上面記錄的速度是從GPS軌跡上面擷取下來的,有可能是原始紀錄時就有誤差,但不至於相差太遠。
    * 如果原始軌跡沒有速度值,此程式會自動用兩點之間的距離算出速度,可能與行車紀錄器寫在影片上面的有一點誤差。
10. 如何使用 Google Photo 自動備份所有影像?
    * http://bit.ly/2Bex3Hg
11. 如何使用 Google Maps 查詢門牌?
    * 在地圖畫面上要查詢的位置上按下右鍵,選擇「這是哪裡」,位置資料即會顯示在下方。
    * 如果該地點沒有門牌,則可能會查詢不到(只能查到道路名稱),請換一個位置。
12. 為什麼KML檔跟CSV檔都沒有內容?
    * 如果原本就沒有GPS軌跡,輸出的KML跟CSV就不會有內容。
    * 如果有GPS軌跡但KML/CSV沒有內容,應該是GPS軌跡檔名跟影片不相同,或是格式不相容。

13. 如果我的錄影機沒有GPS功能,但我用其他的GPS紀錄器記錄下軌跡,該怎麼辦?
    * 此工具可以用影片的拍攝時間來校正轉檔後影像的時間資訊,因此只要您的錄影機時間是正確的,應該就可以用轉出的JPG影像檔,再搭配其他的工具軟體來加上GPS軌跡資料。
    * 請上網搜尋「GPS軌跡 相片 同步」來獲得相關說明。
14. Google Earth不會用,怎麼辦？
    * 請上網搜尋「Google Earth 教學」
15. 我需要付費才能使用嗎?
    * 個人使用不須付費。
    * 如果您喜歡這個小軟體，也歡迎請我喝一杯咖啡：https://www.buymeacoffee.com/aquawill
16. 我可以分享這個軟體給其他人使用嗎?
    * 可以,但建議附上出處與說明文件。
17. 為什麼作者回信這麼慢?
    * 基本上作者是用空閒時間來開發這個小工具,因此有空的時候才能回信,請見諒。
18. 如果我想把這個工具軟體用在商業用途上?
    * 請聯絡作者。
19. 如果我希望作者可以加新功能,支援新格式?
    * 請聯絡作者。
20. 如果我覺得很難用怎麼辦?
    * 可以跟作者抱怨,不過請手下留情。

## Changelog
Ver. 161207
* Initial release.

Ver. 161222
* GUI for input and options.
* Image resolution can be selected, you can choose small size to preserve the disk usage or original for best quality. The default setting is resize to 720p for a quality/size balance.
* Now it produces Menu file of Altas, which means the log and image can be loaded with RDFViewer (Other -> DMO Projects -> Load DMO Project(s) then select the root directory of the video) and Atlas. Thus RMC/LMO members can also use this app if needed, and the video and trace can be easier shared. (Inspired by local LMO crews copied.)
* Now you can choose to extract video with GPS log or GPS log only.
* Now it produces a cumulated GPS log file “@GPSTraceMerged.log” in the folder of the video.
* All GPS logs (.gps) is now RME (Route Match Extension) compatible, you only need to add the column names (longitude, latitude ,heading ,null, speedkmh, timestamp) to the 1st line. Which can help identify potential database issues like missing turn restriction or incorrect restrictions, together with video.
* Minor bugs fixed.

Ver. 161228
* A critical bug fixed (file name recognition issue).

Ver. 170512
* Bug fixing release (incorrect speed value in CSV and KML traces).

Ver. 170911
* Adding new function of interpolation of GPS trace to provide double FPS of both trace and image.

Ver. 170914
* Minor bugs fixed (GPS trace interpolation errors).
* Add initial configuration storage to recall the previous setting.
* Now frame capture will skip the corrupted video without quit.
* Add logging for corrupted video.
* Support GPX format trace and mp4 video input (for Garmin camcorder, run "run_gpx_mp4.bat").

Ver. 170922
* Add purging function to remove all gps/audio/image contents for re-processing or testing.
* Add EXIF injecting of GPS info to the jpeg images.

Ver. 180123
* New option to support VR image.
* Sync image file creation time with the video.
* Support more video formats (mpg, mov, avi, mpg, wmv).
* Can automatically detect video files without specifying file type.
* New option to extracting audio from video as MP3 files.
* New double check for purging.
* New button to send email to the author (me!).
* Improved UI representation.
* Several minor bugs fixed.

Ver. v181023
* Add camera direction override function.
* Fix GPS trace value extraction issues.
* Improved KML style to show the direction of camera.

Ver. v181127
* Integrated Mapillary uploader (with Python 2.7 environment)

Ver. v181205
*  Add camera direction override function.
*  Fix GPS trace value extraction issues.
*  Improved KML style to show the direction of camera.

Ver. v190103
*  Fix Mapillary Uploader issue.

Ver. v190103
*  Fix Mapillary Uploader issue.

Ver. v190523
*  Add "Time Lapse" mode with customizable interval (seconds).
*  Compiled with Python 3.7.

---
<a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/aquawill"><img src="https://www.buymeacoffee.com/assets/img/BMC-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px">Buy me a coffee</span></a>
