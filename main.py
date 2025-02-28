import tomllib
from pathlib import Path
import json
import shutil
import requests
import os

cfg = {}

def main():
    with open("config.toml", "rb") as cfg_file:
        global cfg
        cfg = tomllib.load(cfg_file)
    check_config()
    print_logo()
    prompt_user()

def check_config():
    if not cfg["script"]["upload_url"]:
        print("No upload URL specified in config.toml - you must specify a URL for uploading to / downloading from to sync saves!")
        exit()
    if not cfg["script"]["shared_name"]:
        print("No shared name in config.toml - you must have a shared name to sync files with friends!")
        exit()
    if not cfg["pacha"]["path"]:
        print("No Roots of Pacha save path found - Pacha uploads/downloads will not work!")
    if not cfg["stardew"]["path"]:
        print("No Stardew Valley save path found - Stardew uploads/downloads will not work!")

def print_logo():
    print(" ================================== ")
    print("|                                  |")
    print("|    CCCC       GGGG       SSSS    |")
    print("|   C    C     G    g     s    s   |")
    print("|  C          G            SS      |")
    print("|  C          G    gGg       SS    |")
    print("|   C    C     G    G     s    s   |")
    print("|    CCCC       GGGG       SSSS    |")
    print("|                                  |")
    print("|  + COZY  +-+  GAME  +-+  SYNC +  |")
    print("|                                  |")
    print(" ================================== ")

def prompt_user():
    print("Your Share Code: " + cfg["script"]["shared_name"])
    print("")
    print(" ================================== ")
    print("OPTIONS: ")
    print("1) Manage Stardew")
    print("2) Manage Pacha")
    print("0) Exit")
    print("")
    manage_choice = input("Choice? > ")
    match manage_choice:
        case "1":
            clear()
            manage_stardew()
        case "2":
            clear()
            manage_pacha()
        case "0":
            exit()
        case _:
            clear()
            print("Invalid option, try again (1-3)")
            prompt_user()

def manage_stardew():
    i = 2
    print("")
    print("Stardew Cloud Save - Last Updated " + get_cloud_date("stardew"))
    print("")
    print(" ================================== ")
    print("OPTIONS: ")
    print("1) Download Cloud Save")
    for s in list_stardew_saves():
        print(str(i) + ") Upload " + s[0])
        i = i + 1
    print("0) Go Back")
    print("")
    stardew_choice = input("Choice? > ")
    match stardew_choice:
        case "1":
            download_and_unzip("stardew")
        case "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
            zip_and_upload(list_stardew_saves()[int(stardew_choice) - i][1], "stardew")
        case "0":
            clear()
            prompt_user()
        case _:
            clear()
            print("Invalid Option, try again")
            manage_stardew()

def manage_pacha():
    i = 2
    print("")
    print("Pacha Cloud Save - Last Updated " + get_cloud_date("pacha"))
    print("")
    print(" ================================== ")
    print("OPTIONS: ")
    print("1) Download Cloud Save")
    for s in list_pacha_saves():
        print(str(i) + ") Upload " + s[0])
        i = i + 1
    print("0) Go Back")
    print("")
    pacha_choice = input("Choice? > ")
    match pacha_choice:
        case "1":
            download_and_unzip("pacha")
        case "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
            zip_and_upload(list_pacha_saves()[int(pacha_choice) - i][1], "pacha")
        case "0":
            clear()
            prompt_user()
        case _:
            clear()
            print("Invalid Option, try again")
            manage_pacha()

def list_stardew_saves() -> list[tuple[str, str]]:
    rv = []

    folder = Path(cfg["stardew"]["path"])
    saves = [d for d in folder.iterdir() if d.is_dir()]
    for save in saves:
        rv.append([save.name, str(save)])
    return rv

def list_pacha_saves() -> list[tuple[str, str]]:
    rv = []

    folder = Path(cfg["pacha"]["path"])
    subdirs = [d for d in folder.iterdir() if d.is_dir()]
    folder = folder / subdirs[0]
    saves = [d for d in folder.iterdir() if d.is_dir()]
    for save in saves:
        with open(save / "header.json", "rb") as savedata:
            saveinfo = json.load(savedata)
            rv.append([saveinfo["Players"][0]["Name"], str(save)])
    return rv

def get_cloud_date(game_name):
    response = requests.head(cfg["script"]["upload_url"] + cfg["script"]["shared_name"] + "_" + game_name + ".zip", auth=(cfg["script"]["url_username"], cfg["script"]["url_password"]))
    return response.headers["Last-Modified"] if "Last-Modified" in response.headers else "??"

def zip_and_upload(folder_path, game):
    upload_name = cfg["script"]["shared_name"] + "_" + game
    parent = Path(folder_path).parent
    base = Path(folder_path).name
    shutil.make_archive(upload_name, "zip", root_dir=parent, base_dir=base)

    with open(upload_name + ".zip", "rb") as zip:
        response = requests.put(
            cfg["script"]["upload_url"] + upload_name + ".zip",
            data=zip,
            auth=(cfg["script"]["url_username"], cfg["script"]["url_password"])
        )
    os.remove(upload_name + ".zip")
    clear()
    print("=== ++ FILE UPLOADED! ++ ===")
    prompt_user()
        

def download_and_unzip(game):
    dest = Path(cfg[game]["path"])
    if game == "pacha":
        dest = dest / [d for d in dest.iterdir() if d.is_dir()][0]
    filename =  cfg["script"]["shared_name"] + "_" + game + ".zip"
    url = cfg["script"]["upload_url"] + filename

    response = requests.get(url, auth=(cfg["script"]["url_username"], cfg["script"]["url_password"]), stream=True)
    response.raise_for_status()

    with open(dest / filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    shutil.unpack_archive(dest / filename, dest)
    os.remove(dest / filename)

    clear()
    print("=== ++ SAVE UPDATED! ++ ===")
    prompt_user()


    

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# def download_save_and_unzip(game):
    

main()
