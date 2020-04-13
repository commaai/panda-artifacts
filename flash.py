#!/usr/bin/env python3
import time
import os
import json
import zipfile
from panda import Panda, PandaDFU


if __name__ == "__main__":
  cur_dir = os.path.dirname(os.path.realpath(__file__))

  # Open manifest
  manifest_fn = os.path.join(cur_dir, 'latest.json')
  with open(manifest_fn) as manifest:
    latest = json.load(manifest)

  # Open zip file
  zip_fn = os.path.join(cur_dir, latest['version'] + '.zip')
  with zipfile.ZipFile(zip_fn) as zip_file:
    # Check for panda in DFU mode
    if not PandaDFU.list():
      print("No panda in DFU mode found")

      while not Panda.list():
        print("Waiting for Panda")
        time.sleep(0.5)

      print("Putting panda in DFU mode")
      panda = Panda()
      panda.reset(enter_bootstub=True)
      panda.reset(enter_bootloader=True)

    # Wait for dfu
    while not PandaDFU.list():
      print("Waiting for DFU")
      time.sleep(0.5)

    # Flash bootstub
    bootstub_code = zip_file.open('bootstub.panda.bin').read()
    PandaDFU(None).program_bootstub(bootstub_code)

    # Wait for panda
    while not Panda.list():
      print("Waiting for Panda")
      time.sleep(0.5)

    # Flash firmware
    firmware_code = zip_file.open('panda.bin').read()
    Panda().flash(code=firmware_code)
