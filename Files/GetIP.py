import pickle
import queue
import socket
import subprocess
import threading
import time
from os.path import exists


def user_ip(user, pkl_ip):
    timeout = 0.3
    q = queue.Queue()
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    def check_ip(user):
        # Tests to see if user is in ip dictionary and if the IP associated with the username is still the current IP
        try:
            # Get IP dictionary
            with open(pkl_ip, 'rb') as f:
                ip_dict = pickle.load(f)
            user_ip = ip_dict[user]

            proc = subprocess.run(f'query user /server:{user_ip}', startupinfo=startupinfo, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, shell=True, timeout=timeout)

            if user.upper() in str(proc.stdout.decode("UTF-8")).upper():
                set_ip(user, user_ip)
                return user_ip
        except:
            return False

    def set_ip(user, ip):
        if exists(pkl_ip):
            # Get IP dictionary
            with open(pkl_ip, 'rb') as f:
                ip_dict = pickle.load(f)
        else:
            ip_dict = {}

        ip_dict[user] = ip

        # Set IP dictionary
        with open(pkl_ip, 'wb') as f:
            pickle.dump(ip_dict, f)

    """
    def getips():
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        ipadressen = {}

        def ping(ipadresse, q):
            try:
                # sends only one package, faster
                outputcap = subprocess.run([f'ping', ipadresse, '-n', '1'], capture_output=True,
                                           startupinfo=startupinfo, timeout=0.001)
                ipadressen[ipadresse] = outputcap
                q.put(ipadressen)
            except Exception as e:
                print(e)

        # prepares threads
        q = queue.Queue()
        threads = []
        for ipend in range(255):
            t = threading.Thread(target=ping, args=(f'192.168.16.{ipend}', q))
            threads.append(t)
            t.start()

        # Wait for all of them to finish
        for x in threads:
            x.join()
        ipadressen = q.get(block=False)

        alldevices = []
        for key, item in ipadressen.items():
            # checks if there wasn't neither general failure nor 'unreachable host'
            if 'unreachable' not in item.stdout.decode('utf-8') and 'failure' not in item.stdout.decode('utf-8'):
                alldevices.append(key)
        alldevices.sort()
        return alldevices
    """

    def worker(ip):
        try:
            proc = subprocess.run(f'query user /server:{ip}', startupinfo=startupinfo, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, shell=True, timeout=timeout)

            if user.upper() in str(proc.stdout.decode("UTF-8")).upper():
                q.put(ip)
        except:
            pass

    def after_timeout():
        # print("KILL MAIN THREAD: %s" % threading.current_thread().ident)
        raise SystemExit

    def search_user(all_ips):
        # Search for user in discovered IPs
        n = 1
        results = ''
        print(f'Searching IPs for user "{user}"')
        for ip in all_ips:
            start = time.time()
            #print(f"Starting thread ip:{ip}")
            try:
                results = q.get(block=False, timeout=timeout)
                break
            except:
                t = threading.Thread(target=worker, args=[ip], daemon=True)
                t.start()
                time.sleep(0.1)
                #threading.Timer(timeout, after_timeout).start()
                n += 1
            lap = time.time() - start
            print(f'{ip} took {lap}')
            if lap > 0.3:
                print(f'{ip} took {lap}')
        return results

    def main(user):
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
        user_ip = check_ip(user)
        if user_ip:
            return user_ip
        else:
            # Test to see if queried user is current PC
            proc = subprocess.run(f'query user', stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  shell=True, startupinfo=startupinfo)
            if user.upper() in str(proc.stdout.decode("UTF-8")).upper():
                out = socket.gethostbyname(socket.gethostname())
            else:  # If not, search IPs on network for user
                allIPs = []
                for ipend in range(255):
                    allIPs.append(f'192.168.16.{ipend}')
                print(allIPs)

                out = search_user(allIPs)
                if type(out) is list:
                    out = out[0]
                print(out)

        set_ip(user, out)
        return out

    return main(user)
