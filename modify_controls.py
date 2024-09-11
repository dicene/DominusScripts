import pymem

button_names = {
    0x01: "up",
    0x02: "down",
    0x04: "left",
    0x08: "right",
    0x10: "start",
    0x20: "unk-20",
    0x40: "unk-40",
    0x80: "unk-80",
    0x100: "l",
    0x200: "r",
    0x400: "unk-400",
    0x800: "unk-800",
    0x1000: "b",
    0x2000: "a",
    0x4000: "y",
    0x8000: "x",
}

key_codes = {
    "`": 0x01,
    "1": 0x02,
    "2": 0x03,
    "3": 0x04,
    "4": 0x05,
    "5": 0x06,
    "6": 0x07,
    "7": 0x08,
    "8": 0x09,
    "9": 0x0a,
    "0": 0x0b,
    "-": 0x0c,
    "=": 0x0d,
    "tab": 0x0f,
    "q": 0x10,
    "w": 0x11,
    "e": 0x12,
    "r": 0x13,
    "t": 0x14,
    "y": 0x15,
    "u": 0x16,
    "i": 0x17,
    "o": 0x18,
    "p": 0x19,
    "[": 0x1a,
    "]": 0x1b,
    "enter": 0x1c,
    "a": 0x1e,
    "s": 0x1f,
    "d": 0x20,
    "f": 0x21,
    "g": 0x22,
    "h": 0x23,
    "j": 0x24,
    "k": 0x25,
    "l": 0x26,
    ";": 0x27,
    "'": 0x28,
    "shift": 0x2a,
    "z": 0x2c,
    "x": 0x2d,
    "c": 0x2e,
    "v": 0x2f,
    "b": 0x30,
    "n": 0x31,
    "m": 0x32,
    ",": 0x33,
    ".": 0x34,
    "/": 0x35,
    "f1": 0x3b,
    "f2": 0x3c,
    "f3": 0x3d,
    "f4": 0x3e,
    "f5": 0x3f,
    "f6": 0x40,
    "f7": 0x41,
    "f8": 0x42,
    "f9": 0x43,
    "f10": 0x44,
    "f11": 0x45,
    "f12": 0x46,
    "up": 0xc8,
    "left": 0xcb,
    "right": 0xcd,
    "down": 0xd0,
}

desired_keys = {
    "up": "e",
    "down": "d",
    "left": "s",
    "right": "f",
    "start": "r",
    "y": "j",
    "x": "i",
    "b": "k",
    "a": "l",
    "l": "h",
    "r": ";"
}

def main():
    proc = pymem.Pymem("game.exe")
    game_module = None
    game_module_base = None
    dra01_module = None
    dra01_module_base = None

    print(f"Game.exe found, pid: {proc.process_id}")

    for module in proc.list_modules():
        if module.name.lower().startswith("game.exe"):
            game_module = module
            game_module_base = game_module.lpBaseOfDll
            print(f"Found {module.name} module: {hex(module.lpBaseOfDll)}")
        if module.name.lower().startswith("dra01"):
            dra01_module = module
            dra01_module_base = dra01_module.lpBaseOfDll
            print(f"Found {module.name} module: {hex(module.lpBaseOfDll)}")

    key_map_address = proc.read_ulonglong(game_module_base + 0x58EE60)
    key_map_end_address = proc.read_ulonglong(game_module_base + 0x58EE68)

    print(f"key_map: {hex(key_map_address)} ({hex(game_module_base + 0x58EE60)})")
    print(f"key_map_end: {hex(key_map_end_address)} ({hex(game_module_base + 0x58EE68)})")

    key_map_current = key_map_address

    if not key_map_end_address > key_map_current:
        return

    while key_map_current < key_map_end_address:
        key_id = proc.read_uint(key_map_current)
        button_id = proc.read_uint(key_map_current + 4)
        button_id2 = proc.read_uint(key_map_current + 8)

        new_key = None
        new_key_id = None

        button_name = button_names[button_id2] if button_id2 in button_names.keys() else f'unk-{hex(button_id2)}'

        if button_name is not None and button_name in desired_keys:
            new_key = desired_keys[button_name]
            if new_key is not None and new_key in key_codes:
                new_key_id = key_codes[new_key]
            else:
                print(f"Unknown new key code {new_key_id} for key {button_name}")

        print(f"Key: {hex(key_id)}, {button_name}, {hex(button_id)}, {hex(button_id2)}")
        if new_key_id is not None:
            print(f"    > New key {new_key} set for button {button_name}")
            proc.write_uint(key_map_current, new_key_id)

        key_map_current += 12

main()
