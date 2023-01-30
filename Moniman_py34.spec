# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Moniman.py'],
             pathex=['D:\\Data\\3Packages\\Moniman'],
             binaries=[],
             datas=[('common', 'common'), ('icons', 'icons'), ('dimensioning', 'dimensioning'), ('solver\plaxis2d\materials', 'solver\plaxis2d\materials'), 
			('solver\\plaxis2d\\tubes', 'solver\\plaxis2d\\tubes'), ('solver\plaxis2d\profile_steels', 'solver\plaxis2d\profile_steels'), ('__init__.py', '.'), ('moniman_logo.ico', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='MONIMAN_EXE',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='D:\\Data\\3Packages\\Moniman\\moniman_logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Moniman')