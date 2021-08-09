#!/usr/local/bin/python3
# -*- coding: utf-8 -*- 
import os,re,sys,time
import subprocess,shlex
import math,random
import requests,json,lxml
import unicodedata
from datetime import datetime, timedelta
from dateutil import tz

'''
qbt server info --username admin --password <password> --url <server_url>
'''
# darwin / win32
password = 123456
server_url = "http://xx.xxx.xx:port"
qbit_path = 'qbt' # if sys.platform.startswith('darwin') else 'D:/qbit/qbt-win/qbt'
qbittorrent_path = '/Applications/qBittorrent.app/Contents/MacOS/qbittorrent' if sys.platform.startswith('darwin') else 'C:/Program Files/qBittorrent/qbittorrent.exe'
server = f' --username admin --password {password} --url {server_url}' if sys.platform.startswith('darwin') else ''
print(sys.platform, qbit_path, server)

clear = lambda: os.system('cls' if os.name=='nt' else 'clear')
#sys.stdin=open('in.txt','r')

def exec_cmd(cmd):
    # cmd = unicodedata.normalize('NFC', cmd)
    print('Running command: {}\n'.format(cmd))
    output = ' '.encode('utf-8')
    cmd = re.sub(r'( |\t)+', ' ', cmd)
    try:
        # output = subprocess.check_output(cmd.split(' '))
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        output = e.output.decode()
        # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    else:
        print('command successed.')
        output = unicodedata.normalize('NFC', output.decode('utf-8'))

    print(output)
    return output

def get_torrent_property(hsh):
    cmd = f'qbt torrent properties {hsh} --username admin --password {password} --url {server_url}'
    ret = exec_cmd(cmd)
    return ret

def utc2local(utc):
    from datetime import datetime
    from dateutil import tz

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)

    return central


def test(cmd):
    from subprocess import Popen, PIPE, STDOUT
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    p.wait()
    output = p.stdout.read()
    print(output)
    pass

def test2(cmd):
    process = subprocess.Popen(cmd, shell=True,
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE,
                     errors='ignore')
    stdout, stderr = process.communicate()
    # print('returncode:{}\nstdout:{}\nstderr:{}'.format(process.returncode, stdout, stderr))
    return process.returncode,stdout,stderr


def test3(cmd):
    import os
    stream = os.popen(cmd) # stream = os.popen(cmd, 'r')
    output = stream.read()
    # print(output)
    return output

def test4(cmd):
    import subprocess
    result = subprocess.Popen(cmd)
    text = result.communicate()[0]
    returncode = result.returncode
    return returncode, text

def extract_properties(s):
    import re
    s2 = re.sub(': +', '\n', s)
    s2 = re.sub('  +', '\n', s2)
    l = s2.split('\n')
    d = dict(zip(l[::2], l[1::2]))
    print(d)
    return d


def get_torrent_finish_time(torrent_hash, server=server):
    '''
    Addition date:                 8/31/19 7:05:40 PM
    Tile elapsed:                  01:13:11
    '''
    cmd = '{} torrent properties {} {}'.format(qbit_path, torrent_hash, server)
    d = extract_properties(test3(cmd))

    date_format = '%m/%d/%y %I:%M:%S %p' if sys.platform.startswith('darwin') else '%m/%d/%Y %I:%M:%S %p'
    torrent_finished = not (d['Seeding time'] == '00:00:00')
    # torrent_finish_utc_time = datetime.strptime('1/1/00 00:00:00 AM', '%m/%d/%y %I:%M:%S %p')
    torrent_finish_utc_time = datetime.now()
    if torrent_finished:
        addition_utc = datetime.strptime(d['Addition date'], date_format)

        days, hours, minutes, seconds = 0,0,0,0
        tmp = d['Tile elapsed']
        days = int(tmp[:tmp.find('.')]) if '.' in tmp else 0
        hours, minutes, seconds = map(int, tmp[tmp.find('.')+1:].split(':'))
        elapsed_time = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        pass

    print('Torrent_finished: {}\nAddition date: {}\nelapsed_time: {}\nFinish date: {}\n'.format(
        torrent_finished, d['Addition date'], d['Tile elapsed'], addition_utc+elapsed_time))

    return torrent_finished, torrent_finish_utc_time

def get_rss_date():
    if len(sys.argv) < 2:
        print('No threshold_date assigned. Please pass one parameter.')
        exit(1)
    s = sys.argv[1]
    # date_format = '%a, %b %d, %Y  %I:%M:%S %p'  # 12h format
    date_format = '%a, %b %d, %Y  %H:%M:%S'
    threshold_date = datetime.strptime(s, date_format)
    threshold_date = threshold_date.replace(tzinfo=tz.tzlocal())
    print('rss finish date: {}'.format(threshold_date))
    return threshold_date

def srepl(matchobj):
    # Remove " ' from illegal json formats, like name and paths.
    # print(f'group 0: {matchobj[0]}\n')
    # return ': "{}",\n'.format(re.sub('[^A-Za-z0-9\[\{:\]\}\.\\-/_\s]+', '', matchobj.group(0)[3:-3]))
    return ': "{}",\n'.format(re.sub(r'[\"\']', ' ', matchobj.group(0)[3:-3]))


def get_torrent_list(server=server):
    cmd = '{} torrent list --format json {}'.format(qbit_path,str(server))
    ret = test2(cmd)[1]
    ret = re.sub(': "(.+?)",\n' , srepl, ret)
    # print(type(ret))
    js = json.loads(ret, strict=False)
    # print(js)
    print('Total number of torrents: {}'.format(len(js)))
    return js


def delete_torrents_before(threshold_date, torrent_list=None, server=server):
    print('Deleting all torrents finished before {}:'.format(threshold_date))
    if torrent_list is None:
        torrent_list = get_torrent_list(server)
    hx = []
    name = []
    for torrent in torrent_list:
        if torrent['progress']!=1.0 or torrent['completion_on']<torrent['added_on']:
            continue
        completion_on = datetime.utcfromtimestamp(int(torrent['completion_on']))
        completion_on = completion_on.replace(tzinfo=tz.tzutc())
        completion_on = completion_on.astimezone(tz.tzlocal())
        print('Torrent {}\nProgress: {}\tCompletion_on:{}\tCompletion date: {}\n'.format(torrent['name'], torrent['progress'], torrent['completion_on'], completion_on))
        if completion_on < threshold_date:
            hx.append(torrent['hash'])
            name.append(torrent['name'])
    print('Total number of torrents to be deleted: {}'.format(len(hx)))
    for i,j in zip(hx,name):
        delete_torrent(i, delete_file=True)
        print('{} hash:{} deleted.'.format(j,i))
        time.sleep(15)
    print('\n{} torrents finished before {} deleted.\n'.format(len(hx), threshold_date))
    return hx

def delete_torrent(hx, delete_file=False):
    cmd = '{} torrent delete {} {} {}'.format(qbit_path,'-f' if delete_file else ' ', hx, server)
    ret = test3(cmd)
    pass


def delete_duplicate_torrents(torrent_list=None, server=server):
    if torrent_list is None:
        torrent_list = get_torrent_list(server)
    d = {}
    for t in torrent_list:
        if t['category']+' '+t['name'] not in d:
            d[t['category']+' '+t['name']] = [t]
        else:
            d[t['category']+' '+t['name']].append(t)
    to_delete = []
    print('Deleting duplicate torrents:')
    for i,j in d.items():
        if len(j)<=1:
            continue
        j.sort(key=lambda t: t['added_on'], reverse=True)
        for t in j[1:]:
            delete_torrent(t['hash'], delete_file=False)
            print('{} hash:{} deleted.'.format(t['name'], t['hash']))
            time.sleep(15)
    print('Finish.')


def check_qbt_alive():
    cmd = '{} torrent list {}'.format(qbit_path, server)
    ret,stdout,stderr = test2(cmd)
    # stderr = stderr.decode("utf-8")
    if ret!=0 and 'No connection' in stderr:
        print('qbittorrent is not running')
        os.startfile(qbittorrent_path)
        print('qBittorrent started.')
        time.sleep(300)
        return False
    else:
        print('qbittorrent is running.')
        return True
    pass
'''No connection could be made because the target machine actively refused it'''

def main():
    threshold_date = get_rss_date()

    check_qbt_alive()

    torrent_list=get_torrent_list()
    
    delete_torrents_before(threshold_date, torrent_list)

    delete_duplicate_torrents(torrent_list)

    pass

if __name__ == '__main__':
    main()
    