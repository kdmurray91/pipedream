def get_ip(iface='eth0', localhost=False, use_netifaces=True, use_ioctl=True):
    """get_ip gets the current external (or LAN) IP of any machine.

    :param localhost: On *NIX, allows the return of 127.0.0.1, which is
            normally unhelpful.
    :type localhost: bool
    :param iface: The *NIX interface whose IP is used in place of localhost.
    :type iface: str
    :returns: str -- The current machine's external/LAN IP, or None.
    """
    try:
        # It's python, someone's already written an awesome module to do this.
        # netifaces should always import, as we've got it in setup.py. But
        # just in case...
        import netifaces
        if not use_netifaces:
            # Don't use netifaces by pretending it doesn't exist
            raise ImportError
        # get a dictionary for the specified interface
        iface_dict = netifaces.ifaddresses(iface)[netifaces.AF_INET]
        # extract the IP and return it
        return iface_dict[0]["addr"]
    except ImportError:
        import socket
        try:
            # check if we want to use ioctl
            if not use_ioctl:
                raise ImportError
            import struct
            # linux only
            import fcntl
            # This is Black Magic, see http://stackoverflow.com/q/166506/
            ifreq = struct.pack('16sH14s', iface, socket.AF_INET, '\x00'*14)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockfd = sock.fileno()
            SIOCGIFADDR = 0x8915
            res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
            ip = struct.unpack('16sH2x4s8x', res)[2]
            return socket.inet_ntoa(ip)
        except (ImportError, IOError):
            # The fall-back-fall-back. This works (gets the LAN IP) on windows,
            # but on linux it (normally) returns localhost
            # We get the IP associated with the FQDN of this machine
            fallback = socket.gethostbyname(socket.getfqdn())
            if localhost and fallback.startswith("127.0"):
                return fallback
            elif fallback.startswith("127.0"):
                return None
            else:
                return fallback

def has_internet(url="http://74.125.237.177"):
    """has_internet checks if we have internet

    :param url: The URL used to check connectivity. Must contain protocol.
    :param type: str
    :returns: bool -- True if we have internet else False
    """
    try:
        # Python 3 compatible way of doing things
        from urllib.request import urlopen
        from urllib.error import URLError
    except ImportError:
        # py2.x
        from urllib2 import URLError, urlopen
    try:
        # Try to open url. Raises URLError if we can't.
        response = urlopen(url, timeout=1)
        return True
    except URLError:
        return False