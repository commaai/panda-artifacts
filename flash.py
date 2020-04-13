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
    bootstub_code = zip_file.open('bootstub.panda.bin').read()
    PandaDFU(None).program_bootstub(bootstub_code)

    # Wait for panda to come back online
    while not Panda.list():
      print("Waiting for Panda")
      time.sleep(0.5)

    # Flash firmware
    firmware_code = zip_file.open('panda.bin').read()
    Panda().flash(code=firmware_code)
