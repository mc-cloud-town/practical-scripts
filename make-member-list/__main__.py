import shutil
from pathlib import Path
from typing import Union

import requests
from PIL import Image, ImageDraw, ImageFont

ROW_LEN = 2
COLUMN_LEN = 8
ALL_IN_ONE = False
AVATAR_SIZE = 64
FONT_SIZE = 20
RIGHT_PADDING = 188
BOTTOM_PADDING = 20

FORCE_DOWNLOAD = False

MEMBERS_TABLE = [
    "-Zonzer",
    "-Fallen_Monkey",
    "-stevened7246",
    "-The0ldSteve",
    "-Poltergeist824",
    "-BragMatthew",
    "-Eveeeandpokemon",
    "-Kahyxen",
    "-Dr_Poti",
    "-BragMatthew",
    "-CoolNot",
    "+sbans",
    "+GriRet",
]

MEMBERS_MAP = {
    "member": {
        "-": {m[1:].strip() for m in MEMBERS_TABLE if m.startswith("-")},
        "+": {m[1:].strip() for m in MEMBERS_TABLE if m.startswith("+")},
    }
}


def summon_member_list(images: list[Path], output_path: Union[str, Path] = "out"):
    i = 0
    path = Path(output_path)
    while images:
        background = Image.new(
            "RGBA",
            (
                ROW_LEN * (AVATAR_SIZE + RIGHT_PADDING),
                COLUMN_LEN * (AVATAR_SIZE + BOTTOM_PADDING) - BOTTOM_PADDING,
            ),
            0,
        )
        for row in range(ROW_LEN):
            row_width = row * (AVATAR_SIZE + RIGHT_PADDING)
            for column in range(COLUMN_LEN):
                column_height = column * (AVATAR_SIZE + BOTTOM_PADDING)
                try:
                    file = images.pop()
                except IndexError:
                    break

                avatar = Image.open(file).resize((AVATAR_SIZE, AVATAR_SIZE))
                background.paste(avatar, (row_width, column_height))

                imd = ImageDraw.Draw(background)
                imd.text(
                    (
                        row_width + AVATAR_SIZE + 12,
                        column_height + AVATAR_SIZE / 2 - FONT_SIZE / 2,
                    ),
                    file.stem,
                    fill=(255, 255, 255),
                    font=ImageFont.truetype("arial.ttf", FONT_SIZE),
                )

                print(f"{row:02}-{column:02}: {file.stem}")
        i += 1

        path.mkdir(parents=True, exist_ok=True)
        background.save(path / f"{i}.png")


if __name__ == "__main__":
    data = requests.get("https://mc-ctec.org/static-data/member.json").json()

    if FORCE_DOWNLOAD:
        shutil.rmtree("avatars", ignore_errors=True)

    for type, members in data.items():
        members = [m["name"] for m in members]
        if type in MEMBERS_MAP:
            members_map = MEMBERS_MAP[type]

            print(f"取得 {type} 成員名單")
            members = list(filter(lambda x: x not in members_map["-"], members))
            members.extend(list(members_map["+"]))

        members.sort()
        members = set[str](members)
        data[type] = list(members)
        for name in members:
            file = Path(f"avatars/{type}/{name}.png")
            if not file.is_file():
                r = requests.get(f"https://mineskin.eu/helm/{name}")
                if r.status_code == 200:
                    file.parent.mkdir(parents=True, exist_ok=True)
                    file.write_bytes(r.content)
                    print(f"取得 {type} {name} 頭像")
                else:
                    print(f"無法取該 {name} 頭像: {r.status_code}")

    for dir in Path("avatars").glob("*"):
        print(dir)
        images = list(dir.glob("*.png"))
        if dir.name not in data:
            continue

        remote_names = data[dir.name]
        for image in images:
            if image.stem not in remote_names:
                image.unlink()
                images.remove(image)

        if ALL_IN_ONE:
            COLUMN_LEN = round(len(images) / ROW_LEN)

        summon_member_list(images, Path("out") / dir.name)
