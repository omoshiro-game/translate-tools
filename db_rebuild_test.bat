@echo off

python tools\rebuild_dat.py data\database\Anime.json --out data\database\Anime.dat
python tools\rebuild_dat.py data\database\AnimeSet.json --out data\database\AnimeSet.dat
python tools\rebuild_dat.py data\database\Bgm.json --out data\database\Bgm.dat
python tools\rebuild_dat.py data\database\Bmp_CharaExc.json --out data\database\Bmp_CharaExc.dat
python tools\rebuild_dat.py data\database\CharaEffect.json --out data\database\CharaEffect.dat
python tools\rebuild_dat.py data\database\Effect.json --out data\database\Effect.dat
python tools\rebuild_dat.py data\database\Picture.json --out data\database\Picture.dat
python tools\rebuild_dat.py data\database\ScrEffect.json --out data\database\ScrEffect.dat
python tools\rebuild_dat.py data\database\Sound.json --out data\database\Sound.dat
python tools\rebuild_dat.py data\database\SwordType.json --out data\database\SwordType.dat