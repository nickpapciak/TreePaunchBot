import configparser
import os
import sys
import codecs


if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

    config = configparser.ConfigParser()

    config.read_file(codecs.open(
        str(application_path)+'/config.ini', "r", "utf8"))

    TOKEN = config['SECRETS']['DISCORD_TOKEN'].strip("'")
    TWITCH_CLIENT_ID = config['SECRETS']['TWITCH_CLIENT_ID'].strip("'")
    TWITCH_CLIENT_SECRET = config['SECRETS']['TWITCH_CLIENT_SECRET'].strip("'")
