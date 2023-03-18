import pickle
import queue
import socket
import subprocess
import threading
import time
from os.path import exists


def user_ip(_user, pkl_ip):
    _user = _user.upper()
    q = queue.Queue()
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    def query_user(ip=""):
        proc = subprocess.run(f'query user /server:{ip}', startupinfo=startupinfo, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, shell=True, timeout=0.3)
        output = str(proc.stdout.decode("UTF-8")).upper()
        return output

    def check_ip(_user):
        # Tests to see if _user is in ip dictionary and if the IP associated with the username is still the current IP
        try:
            # Get IP dictionary
            with open(pkl_ip, 'rb') as f:
                ip_dict = pickle.load(f)
            _user_ip = ip_dict[_user]

            if _user in query_user(_user_ip):
                set_ip(_user, _user_ip)
                return _user_ip
        except Exception as e:
            print(e)
            return False

    def set_ip(_user, ip):
        if exists(pkl_ip):
            # Get IP dictionary
            with open(pkl_ip, 'rb') as f:
                ip_dict = pickle.load(f)
        else:
            ip_dict = {}

        ip_dict[_user] = ip

        # Set IP dictionary
        with open(pkl_ip, 'wb') as f:
            pickle.dump(ip_dict, f)

    def worker(ip):
        try:
            if _user in query_user(ip):
                q.put(ip)
        except Exception as e:
            print(e)
            pass

    def search_user(all_ips):
        # Search for _user in discovered IPs
        n = 1
        results = ''
        print(f'Searching IPs for user "{_user}"')
        for ip in all_ips:
            start = time.time()
            try:
                results = q.get(block=False, timeout=0.1)
                break
            except queue.Empty:
                t = threading.Thread(target=worker, args=[ip], daemon=True)
                t.start()
                time.sleep(0.1)
                n += 1
            lap = time.time() - start
            print(f'{ip} took {lap}')
        return results

    def main(_user):
        """
        Testing allIPs = ['192.168.16.1', '192.168.16.5', '192.168.16.19', '192.168.16.6', '192.168.16.3',
        '192.168.16.29', '192.168.16.27', '192.168.16.24', '192.168.16.32', '192.168.16.38', '192.168.16.35',
        '192.168.16.40', '192.168.16.58', '192.168.16.55', '192.168.16.62', '192.168.16.70', '192.168.16.66',
        '192.168.16.65', '192.168.16.80', '192.168.16.42', '192.168.16.83', '192.168.16.41', '192.168.16.49',
        '192.168.16.89', '192.168.16.88', '192.168.16.86', '192.168.16.93', '192.168.16.100', '192.168.16.63',
        '192.168.16.106', '192.168.16.47', '192.168.16.103', '192.168.16.105', '192.168.16.112', '192.168.16.114',
        '192.168.16.111', '192.168.16.122', '192.168.16.109', '192.168.16.120', '192.168.16.116', '192.168.16.121',
        '192.168.16.126', '192.168.16.125', '192.168.16.119', '192.168.16.124', '192.168.16.131', '192.168.16.130',
        '192.168.16.132', '192.168.16.71', '192.168.16.134', '192.168.16.77', '192.168.16.133', '192.168.16.136',
        '192.168.16.46', '192.168.16.94', '192.168.16.91', '192.168.16.90', '192.168.16.200', '192.168.16.240',
        '192.168.16.75', '192.168.16.21', '192.168.16.44', '192.168.16.57', '192.168.16.64', '192.168.16.72',
        '192.168.16.61', '192.168.16.96', '192.168.16.69', '192.168.16.54', '192.168.16.73', '192.168.16.82',
        '192.168.16.118']
        """
        _user_ip = check_ip(_user)
        if _user_ip:
            return _user_ip
        else:
            if _user in query_user():  # Test to see if queried _user is current PC
                out = socket.gethostbyname(socket.gethostname())
            else:  # If not, search IPs on network for _user
                all_ips = []
                for ip_end in range(255):
                    all_ips.append(f'192.168.16.{ip_end}')
                print(all_ips)

                out = search_user(all_ips)
                if type(out) is list:
                    out = out[0]
                print(out)

        set_ip(_user, out)
        return out

    return main(_user)
