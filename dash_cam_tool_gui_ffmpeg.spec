# -*- mode: python -*-

block_cipher = None


a = Analysis(['dash_cam_tool_gui_ffmpeg.py'],
             pathex=['C:\\Users\\guanlwu\\Desktop\\Python_src'],
             binaries=[],
             datas=[ ('./ffmpeg.exe', '.'), ('./exiftool.exe', '.'), ('./mapillary_tools.exe', '.') ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='dash_cam_tool',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
name='dash_cam_tool')