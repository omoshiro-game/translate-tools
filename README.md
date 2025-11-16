# Aquedi4 translate tools

## Prerequites

<details>
  <summary>This is automatically done by the installer !</summary>
    <p>
    All the tools needs to work with the latest version of the editor, and the latest version of the editor needs to work with the latest version of the game engine. Be sure to download them from <a href="omoshiro-game.github.io/en/menu_game/ActionEditor4/">Official website</a> .</p>
    <p>
    While the game name being `Game_v1020.exe` is a requirement (for now), you can use tools like Resource Hacker to change its icon to your liking. 
    Be sure to only use the `Editor_v1020.exe` and `Game_v1020.exe` to run editor and game, and not the game original engine as you want it updated to the latest version.
    </p>

</details>

## Setup

First, you need one time setup of tools from your game directory.

To install, open powershell on your `Editor_v1020.exe` / `Game_v1020.exe` / Where your aquedi4 game is folder.

You can do that with "File > Open Windows Powershell > File > Open Windows Powershell" 

Then, paste the following command :

`iwr -useb https://raw.githubusercontent.com/omoshiro-game/translate-tools/refs/heads/main/tools/_setup-tools.ps1 | iex`

If you got a security warning, run the following command : `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and try the above command again.

If it's still blocking, try downloading directly the [_setup-tools.ps1](https://raw.githubusercontent.com/omoshiro-game/translate-tools/refs/heads/main/tools/_setup-tools.ps1) into your game folder, and running it from here with `.\_setup-tools.ps1`

Wait for it to finish, then you can close the blue window.

If your game needs upgrading to 1020 (it may be), then use `upgrade_all.bat` by entering on the blue window `.\upgrade_all.bat`. Just let the window open and close  many times and wait for it to be done.

## Mod Loader

Install it using `.\tools\_setup-modloader.ps1` as it would make the english text on the game less spaced, and allow you to put your mod apart from the game file (Into the `update` folder, see [Aquedi4 Mod Loader](https://github.com/omoshiro-game/aquedi4-modoader) ).

## Translating 

The flow is fairly easy :

```bash
python\python.exe tools\stg4_tool.py export data\stg4\MyStage.stg4_1020 
python\python.exe tools\keys_extract.py data\stg4
python\python.exe tools\translate_pre.py data\stg4
```

Then, translate the _todo.json and finally apply the translation (Don't leave any TODO !!):

```bash
python\python.exe tools\translate_post.py data\stg4
python\python.exe tools\keys_apply.py data\stg4
python\python.exe tools\stg4_tool.py import data\stg4\MyStage.stg4_1020.json
```

And you can do that for every `stg4_1020` file on the 'stg4' folder you have

## Releasing a mod/translation patch

You'd need the [Aquedi4 Mod Loader](https://github.com/omoshiro-game/aquedi4-modoader) to do that. While being very flexible, it's mainly used to load mods file and patch font size on english computer. Get it from [Releases](https://github.com/omoshiro-game/aquedi4-modoader/releases/tag/0.0.1) and create an `update` folder with all your translation and modified data. They would overlay original files, like for example drop a `update/bmp/Title.bmp` with your custom 640x480 image to use as new menu background.

You should not redistribute the `tools` folder, but you are encouraged to distribute the game with the mod loader and the `scripts` and `update` folder and `d3d9*.dll` files. That would make font a bit easier to read in english computer.


You may be interested to check [English editor patches](https://github.com/omoshiro-game/English_patch/) too if you work with the editor a lot.