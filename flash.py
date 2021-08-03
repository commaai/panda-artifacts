#!/usr/bin/env python3
import time
import os
import json
import zipfile
from panda import Panda, PandaDFU, MCU_TYPE_H7

BOOTSTUB_H7_FN = "bootstub.panda_h7.bin"
BOOTSTUB_FX_FN = "bootstub.panda.bin"
FW_H7_FN = "panda_h7.bin"
FW_FX_FN = "panda.bin"
is_mcu_h7 = False

if __name__ == "__main__":
  cur_dir = os.path.dirname(os.path.realpath(__file__))

  # Open manifest
  manifest_fn = os.path.join(cur_dir, 'latest.json')
  with open(manifest_fn) as manifest:
    latest = json.load(manifest)

  # Open zip file
  zip_fn = os.path.join(cur_dir, latest['version'] + '.zip')
  with zipfile.ZipFile(zip_fn) as zip_file:
    # Wait for panda to connect
    while not PandaDFU.list():
      print("Waiting for panda in DFU mode")

      if Panda.list():
        print("Panda found. Putting in DFU Mode")
        panda = Panda()
        panda.reset(enter_bootstub=True)
        panda.reset(enter_bootloader=True)

      time.sleep(0.5)

    # Flash bootstub
    panda_dfu = PandaDFU(None)
    is_mcu_h7 = panda_dfu._mcu_type == MCU_TYPE_H7
    fn = BOOTSTUB_H7_FN if is_mcu_h7 else BOOTSTUB_FX_FN
    print(f"Detected MCU type {panda_dfu._mcu_type}, flashing {fn}")
    bootstub_code = zip_file.open(fn).read()
    panda_dfu.program_bootstub(bootstub_code)

    # Wait for panda to come back online
    while not Panda.list():
      print("Waiting for Panda")
      time.sleep(0.5)

    # Flash firmware
    fn = FW_H7_FN if is_mcu_h7 else FW_FX_FN
    print(f"Flashing {fn}")
    firmware_code = zip_file.open(fn).read()
    Panda().flash(code=firmware_code)
