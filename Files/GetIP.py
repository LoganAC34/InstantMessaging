import queue
import socket
import subprocess
import threading
import time

import kthread


def user_ip(user):
    timeout = 0.1
    q = queue.Queue()

    def getips():
        ipadressen = {}

        def ping(ipadresse):
            try:
                outputcap = subprocess.run([f'ping', ipadresse, '-n', '1'],
                                           capture_output=True)  # sends only one package, faster
                ipadressen[ipadresse] = outputcap
            except Exception as Fehler:
                print(Fehler)

        t = [kthread.KThread(target=ping, name=f"ipgetter{ipend}", args=(f'192.168.16.{ipend}',)) for ipend in
             range(255)]  # prepares threads
        [kk.start() for kk in t]  # starts 255 threads
        print('Searching network for valid IPs')
        #while len(ipadressen) < 255:
            #print('Searching network')
            # sleep(0.001)
        alldevices = []
        for key, item in ipadressen.items():
            if not 'unreachable' in item.stdout.decode('utf-8') and 'failure' not in item.stdout.decode(
                    'utf-8'):  # checks if there wasn't neither general failure nor 'unreachable host'
                alldevices.append(key)
        return alldevices

    def worker(ip):
        try:
            proc = subprocess.run(f'query user /server:{ip}', stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  shell=True, timeout=timeout)
            if user.upper() in str(proc.stdout.decode("UTF-8")).upper():
                q.put(ip)
                # print("Tyler: " + ip)
        except:
            pass

    def after_timeout():
        # print("KILL MAIN THREAD: %s" % threading.current_thread().ident)
        raise SystemExit

    def search_user(all_ips):
        n = 1
        results = ''
        print(f'Searching IPs for user "{user}"')
        for ip in all_ips:
            try:
                results = q.get(block=False, timeout=timeout)
                break
            except:
                #print(f"Starting thread {n}")
                t = threading.Thread(target=worker, args=[ip], daemon=True)
                time.sleep(timeout)
                t.start()
                threading.Timer(timeout, after_timeout).start()
                n += 1
        return results

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

    proc = subprocess.run(f'query user', stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          shell=True, timeout=timeout)
    if user.upper() in str(proc.stdout.decode("UTF-8")).upper():
        out = socket.gethostbyname(socket.gethostname())
    else:
        allIPs = getips()
        print(allIPs)
        out = search_user(allIPs)
        if type(out) is list:
            out = out[0]
        print(out)
    return out
