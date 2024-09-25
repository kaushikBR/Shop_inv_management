import os
import datetime
import hashlib


def check_trial():
    if os.path.exists('license_key'):
        valid_key = hashlib.sha256("king-god-bira-jack-old-monk-moment-91010".encode()).hexdigest()
        with open('license_key', 'r') as file:
            content = file.read()
            if valid_key in content:
                return True
            else:
                print("License Error")
    file = 'acdate'
    if not os.path.exists(file):
        with open(file, 'w') as f:
            f.write(str(datetime.date.today()))
        return True
    with open(file, 'r') as f:
        install_date = datetime.datetime.strptime(f.read(), '%Y-%m-%d').date()
    return (datetime.date.today() - install_date).days <= 7

def validate_license(key):
    valid_key = hashlib.sha256("king-god-bira-jack-old-monk-moment-91010".encode()).hexdigest()
    return hashlib.sha256(key.encode()).hexdigest() == valid_key

def save_license(key):
    with open('license_key', 'w') as f:
        f.write(key)
