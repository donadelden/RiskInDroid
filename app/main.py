import hashlib
import os
import subprocess
import time
import pprint
import argparse
import os
import sys
import datetime
import json

from RiskInDroid import RiskInDroid
from model import db, Apk
import argparse
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-f", "--file", help="apk file name")
group.add_argument("-d", "--dir", help="apk directory path")
args = parser.parse_args()
ALLOWED_EXTENSIONS = {"apk", "zip"}

pp = pprint.PrettyPrinter(indent=2)
rid = RiskInDroid()

def check_if_valid_file_name(file_name):
    return (
        "." in file_name and file_name.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

def get_risk(file_path):
    permissions = rid.get_permission_json(file_path)
    risk = rid.calculate_risk(rid.get_feature_vector_from_json(permissions))
    permissions["risk_factor"] = risk
    return permissions

def run():
    if args.file:
        apk_file_path = args.file
        if not os.path.isfile(apk_file_path):
            print("File not found", apk_file_path)
            return
        
        if not check_if_valid_file_name(apk_file_path):
            print(apk_file_path, ": Not and apk")
            return

        print(apk_file_path)
        file = os.path.basename(apk_file_path)
        if(not os.path.exists("results")):
            os.mkdir("results")

        result_path = os.path.join("results", datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S"))
        os.mkdir(result_path)

        print("\nAnazying " + file)
        permission_dict = get_risk(apk_file_path)
        permission_dict = {**{"apk": file}, **permission_dict}
        permission_json = json.dumps(permission_dict, indent=4)
        result_file = file.replace(" ", "_").removesuffix(".apk").removesuffix(".zip")+".json"
        with open(os.path.join(result_path, result_file), "w") as f:
            f.write(permission_json)
        print("Result Written for: " + file)

    elif args.dir:
        apk_dir_path = args.dir
        if(not os.path.exists(apk_dir_path)):
            print("The Directory path does not exists..", file=sys.stderr)
            return
        file_list = [f for f in os.listdir(apk_dir_path)
                     if os.path.isfile(os.path.join(apk_dir_path, f))]

        if(not os.path.exists("results")):
            os.mkdir("results")

        result_path = os.path.join("results", datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S"))
        os.mkdir(result_path)
        
        for file in file_list:
            file_path = os.path.join(apk_dir_path ,file)
            if not check_if_valid_file_name(file_path):
                print(file, ": Not and apk, skipping...")
                continue

            print("\nAnazying " + file)
            permission_dict = get_risk(file_path)
            permission_dict = {**{"apk": file}, **permission_dict}
            permission_json = json.dumps(permission_dict, indent=4)
            result_file = file.replace(" ", "_").removesuffix(".apk").removesuffix(".zip")+".json"
            with open(os.path.join(result_path, result_file), "w") as f:
                f.write(permission_json)
            print("Result Written for: " + file)

run()
