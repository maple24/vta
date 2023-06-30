# General tools to help Jenkins
import shutil 
import os
import sys
import yaml
import win32api
import win32con
import win32file
import serial
import time
import re
import sys
import tarfile
import zipfile
from tqdm import tqdm
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def load_config(config: str):
    try:
        with open(config, 'r') as f:
            try:
                conf = yaml.safe_load(f)
            except yaml.scanner.ScannerError:
                print(f"Invalid yaml file '{config}'!!")
                sys.exit(1)
            except TypeError:
                print(f"Unsupported config type '{config}'!!")
                sys.exit(1)
    except FileNotFoundError:
        print(f"File not found '{config}'!!")
        sys.exit(1)
    return conf

def get_removable_drives():
    drives = [i for i in win32api.GetLogicalDriveStrings().split('\x00') if i]
    rdrives = [d for d in drives if win32file.GetDriveType(d) == win32con.DRIVE_REMOVABLE]
    if len(rdrives) == 0:
        print("No removable drives found!")
    return rdrives[0]

def remove_directory(path, recursive=True):
    path = _absnorm(path)
    if not os.path.exists(path):
        print("Directory '%s' does not exist." % path)
    elif not os.path.isdir(path):
        print("Path '%s' is not a directory." % path)
    else:
        if recursive:
            shutil.rmtree(path)
            print("Directory '%s' is removed." % path)
        
def copy_directory(source, destination):
    source, destination \
        = _prepare_copy_and_move_directory(source, destination)
    try:
        shutil.copytree(source, destination)
    except shutil.Error as e:
        print(f"{e}")
    except:
        raise
    print(f"Copied directory from {source} to {destination}.")
    
def copy_file(source, destination):
    try:
        print("Start copying, Please wait...")
        shutil.copyfile(source, destination)
    except shutil.Error as e:
        print(f"{e}")
    except:
        raise
    print(f"Copied file from {source} to {destination}.")

def move_directory(source, destination):
    source, destination \
        = _prepare_copy_and_move_directory(source, destination)
    try:
        shutil.move(source, destination)
    except shutil.Error as e:
        print(f"{e}")
    except:
        raise
    print(f"Moved directory from {source} to {destination}.")    
    
def _prepare_copy_and_move_directory(source, destination):
    source = _absnorm(source)
    destination = _absnorm(destination)
    if not os.path.exists(source):
        print("Source '%s' does not exist." % source)
    if not os.path.isdir(source):
        print("Source '%s' is not a directory." % source)
    if os.path.exists(destination) and not os.path.isdir(destination):
        print("Destination '%s' is not a directory." % destination)
    if os.path.exists(destination):
        base = os.path.basename(source)
        destination = os.path.join(destination, base)
    else:
        parent = os.path.dirname(destination)
        if not os.path.exists(parent):
            os.makedirs(parent)
    return source, destination

def _absnorm(path):
    path = _normalize_path(path)
    try:
        return _abspath(path)
    except ValueError:
        return path
    
def _normalize_path(path, case_normalize=False):
    path = os.path.normpath(os.path.expanduser(path.replace('/', os.sep)))
    if case_normalize:
        path = os.path.normcase(path)
    return path or '.'

def _abspath(path, case_normalize=False):
    path = _normpath(path, case_normalize)
    return path

def _normpath(path, case_normalize=False):
    path = os.path.normpath(path)
    if case_normalize:
        path = path.lower()
    if len(path) == 2 and path[1] == ':':
        return path + '\\'
    return path

def decompress(dsfile, dcfolder=None, members=None):
    '''
    Extracts `tar_file` and puts the `members` to `path`.
    If members is None, all members on `tar_file` will be extracted.
    '''
    if dcfolder is None:
        dcfolder = "\\".join(os.path.abspath(__file__).split("\\")[:-1])

    if not os.path.exists(dsfile):
        print("Decompress Error!! File is not existed!")
        sys.exit(1)
    if dsfile.split('.')[-1] == 'tgz':
        tar = tarfile.open(dsfile, mode="r:gz")
        print(f"**********Start uncompressing {dsfile}**********")
        if members is None:
            members = tar.getmembers()
        progress = tqdm(members)
        for member in progress:
            tar.extract(member, path=dcfolder)
            progress.set_description(f"Extracting {member.name}")
        tar.close()
        print(f"++++++++++Done uncompressing++++++++++")
    elif dsfile.split('.')[-1] == 'zip':
        zip = zipfile.ZipFile(dsfile, 'r')
        print(f"**********Start uncompressing {dsfile}**********")
        if members is None:
            members = zip.namelist()
        print(members)
        progress = tqdm(members)
        for member in progress:
            zip.extract(member, path=dcfolder)
            progress.set_description(f"Extracting {member}")
        zip.close()
        print(f"++++++++++Done uncompressing++++++++++")
    else:
        print('File type is not supported to decompress.')
    return dcfolder

def write_command(cmd, comport, username='root', password='root', timeout=2):
    with serial.Serial(comport, baudrate=115200, timeout=2) as ser:
        print(f"Opening port {comport}...")
        ser.write("\n".encode())
        if ser.readlines()[-1].decode() == 'login: ':
            ser.write((username + '\n').encode())
        if ser.readlines()[-1].decode() == 'Password: ':
            ser.write((password + '\n').encode())
        print(f"Sending cmd {cmd}")
        if isinstance(cmd, list):
            for i in cmd:
                ser.write((i + '\n').encode())
                time.sleep(3)
        else:
            ser.write((cmd + '\n').encode())
        time.sleep(timeout)
        data = ser.readlines()
        return data

def match_string(pattern, data):
    for string in data:
        match = re.search(pattern, string.decode())
        if match:
            match_data = match.group()
            print("regex matches: ", match_data)
            return True

def list_string(data):
    for string in data:
        print(string.decode(), end='')

def close_puttywindow():
    os.system("taskkill /im PUTTY.EXE /f 2>nul >nul")
    os.system("taskkill /im putty.exe /f 2>nul >nul")
    time.sleep(1)
    print("Putty window is shut down.")


class EmailClient:
  def __init__(self, sender, username="ets1szh", password="estbangbangde5"):
    self._mail_server = 'rb-smtp-int.bosch.com'
    self._mail_server_port = 25
    self._sender = sender
    self._credentials = {
      "username": username,
      "password": password
    }

  def send_mail(self, recipients: list, subject, email_body):    
    msg = MIMEMultipart()
    # body = MIMEText(email_body, 'html')
    body = MIMEText(email_body)
    msg['Subject'] = subject
    msg.attach(body)
    msg['From'] = self._sender
    msg['To'] = ", ".join(recipients)

    with SMTP(self._mail_server,port=self._mail_server_port) as conn:
        try:
            conn.login(self._credentials['username'], self._credentials['password'])
            print("Login successfully!")
            conn.sendmail(self._sender, recipients, msg.as_string())
            print("Mail sent successfully!")
        except:
            raise