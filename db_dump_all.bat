@echo off
python tools\dump_dat.py data\database\Anime.dat --out data\database\Anime.json
python tools\dump_dat.py data\database\AnimeSet.dat --out data\database\AnimeSet.json
python tools\dump_dat.py data\database\Bgm.dat --out data\database\Bgm.json
python tools\dump_dat.py data\database\Bmp_CharaExc.dat --out data\database\Bmp_CharaExc.json
python tools\dump_dat.py data\database\CharaEffect.dat --out data\database\CharaEffect.json
python tools\dump_dat.py data\database\Effect.dat --out data\database\Effect.json
python tools\dump_dat.py data\database\Picture.dat --out data\database\Picture.json
python tools\dump_dat.py data\database\ScrEffect.dat --out data\database\ScrEffect.json
python tools\dump_dat.py data\database\Sound.dat --out data\database\Sound.json
python tools\dump_dat.py data\database\SwordType.dat --out data\database\SwordType.json