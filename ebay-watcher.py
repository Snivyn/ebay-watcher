import requests
from bs4 import BeautifulSoup as soup
import random
import datetime
from threading import Thread
from log import log as log

def read_from_txt(path):
    '''
    (str) -> list of str
    Loads up all sites from the sitelist.txt file in the root directory.
    Returns the sites as a list
    '''
    # Initialize variables
    raw_lines = []
    lines = []

    # Load data from the txt file
    try:
        f = open(path, "r")
        raw_lines = f.readlines()
        f.close()

    # Raise an error if the file couldn't be found
    except:
        log('e', "Couldn't locate <" + path + ">.")
        raise FileNotFound()

    # Parse the data
    for line in raw_lines:
        lines.append(line.strip("\n"))

    # Return the data
    return lines

def get_proxy(proxy_list):
    '''
    (list) -> dict
    Given a proxy list <proxy_list>, a proxy is selected and returned.
    '''
    # Choose a random proxy
    proxy = random.choice(proxy_list)

    # Split up the proxy
    proxy_parts = proxy.split(':')

    # Set up the proxy to be used
    try:
        proxies = {
            "http": "http://" + proxy_parts[2] + ":" + proxy_parts[3] + "@" +\
            proxy_parts[0] + ":" + proxy_parts[1],
            "https": "https://" + proxy_parts[2] + ":" + proxy_parts[3] + "@" +\
            proxy_parts[0] + ":" + proxy_parts[1]
        }
    except:
        proxies = {
            "http": str(proxy),
            "https": str(proxy)
            }

    # Return the proxy
    return proxies

def gen_email(domain):
    '''
    (str) -> str
    Given a domain, a random email address is generated.

    REQ: Valid <domain> is provided
    '''
    return str(random.randint(100000000, 999999999)) + "@" + domain


class eBae:
    def __init__(self, product_link, domain):
        '''
        (str, str) -> eBae
        Given a link to an eBay product <product_link> and a catch-all domain
        address <domain>, a random email address is generated and an eBae
        object is returned.
        
        REQ: domain is a catch-all domain
        REQ: product_link is a link to a product listed on eBay
        '''
        self.s = requests.session()
        self.product_link = product_link
        self.s.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
        }
        self.proxy_list = read_from_txt("proxies.txt")
        self.email = gen_email(domain)

    def register(self):
        '''
        () -> bool
        Attempts to create an eBay account. No error checking is done to ensure
        success. The assumption is that if a connection could be made through
        the proxy, no issues should occur during the registration phase.
        '''
        # Set up request to be made
        link = "https://reg.ebay.ca/reg/PartialReg"
        payload = {
            "isSug": "false",
            "countryId": "2",
            "userid": "",
            "ru": "http://www.ebay.ca",
            "firstname": "Bill",
            "lastname": "Nye",
            "email": self.email,
            "PASSWORD": "G2-kennyS",
            "promotion": "true",
            "iframeMigration1": "true",
            "mode": "1",
            "frmaction": "submit",
            "tagInfo": "ht5%3DAQAAAWYTLNkMAAUxNjYyM2QzN2E5ZC5hOTliMTliLjIzZjA2LmZmZmY1OWZiUII8pysAhR1B%252F7QeEEkR2JhM6UE*%7Cht5new%3Dfalse%26usid%3D23d486fd1660aa16b5f1511fffff63de",
            "isGuest": "0",
            "idlstate": "",
            "profilePicture": "",
            "agreement": "Terms and conditions",
            "signInUrl": "https%3A%2F%2Fsignin.ebay.ca%2Fws%2FeBayISAPI.dll%3FSignIn%26ru%3Dhttp%253A%252F%252Fwww.ebay.ca%26regUrl%3Dhttps%253A%252F%252Freg.ebay.ca%252Freg%252FPartialReg",
            "personalFlag": "true",
            "isMobilePhone": "",
            "_trksid": "p2052190",
            "ets": "AQADAAAAEEI86Oq8oYGjne4i2ZMNKME"
            }
        
        try:
            self.s.post(link, data=payload, proxies=get_proxy(self.proxy_list), verify=False)
        except:
            try:
                self.s.post(link, data=payload, proxies=get_proxy(self.proxy_list), verify=False)
            except:
                log('e', "Connection failed while creating account with email " + self.email)
                return False

        # Alert user of progress: Account creation attempted
        log('i', "Created account with email " + self.email)
        return True

    def watch(self):
        '''
        () -> None
        Attempts to watch a product on eBay.
        '''
        # Get product watch link
        try:
            r = self.s.get(self.product_link, proxies=get_proxy(self.proxy_list), verify=False)
        except:
            try:
                r = self.s.get(self.product_link, proxies=get_proxy(self.proxy_list), verify=False)
            except:
                log('e', "Connection failed while loading product on " + self.product_link)
                return

        try:
            watch_link = soup(r.text, "html.parser").find("div", {"id": "vi-atl-lnk"}).a["href"]
        except:
            log('e', "Connection failed while loading product on " + self.product_link)
            return
            
        # Watch the product (the second GET actually adds it to watch list)
        try:
            r = self.s.get(watch_link, proxies=get_proxy(self.proxy_list), verify=False)
            r = self.s.get(watch_link, proxies=get_proxy(self.proxy_list), verify=False)   
        except:
            try:
                r = self.s.get(watch_link, proxies=get_proxy(self.proxy_list), verify=False)
                r = self.s.get(watch_link, proxies=get_proxy(self.proxy_list), verify=False)   
            except:
                log('e', "Failed to add " + self.product_link + " to watch list.")
                return
                

        # Alert user of progress: Watch product success/failure
        if("saved in your" in r.text.lower()):
            log('s', "Added " + self.product_link + " to watch list.")
        else:
            log('e', "Couldn't add " + self.product_link + " to watch list.")

    def start(self):
        '''
        () -> None
        Creates an eBay account and attempts to watch a previously defined
        product.
        '''
        # Create an account
        logged_in = self.register()

        # Watch the product
        if(logged_in):
            self.watch()

def intro():
    '''
    () -> None
    Short intro text outlining what the project does, requirements, usage, and
    a short disclaimer at the end.
    '''
    print(
        '''
        \t\t\t\teBae v1.0
        \tMade for Sneaker Hackathon by snivyn#0416/@snivynGOD

        Cool likkle thing to try and help with finessing eBay's algorithm to
        get your listing to the top when someone searches for a product. Useful
        to sell shoes/Funkos where there are a lot of sellers and you need
        your listing to be seen first by potential buyers. The password to all
        created accounts is <G2-kennyS> (excluding < and >). If you don't care
        for the accounts that are made, you can put a random domain as your
        catch-all domain and it should still work fine. 

        Requirements:
        \tPython dependencies: requests, bs4
        \tCatch-All Domain
        \tProxies (more/rotating == better)

        Usage:
        What link do you want to watch: https://www.ebay.ca/itm/283116687683
        What is your catch-all domain (ex. ebae.com): ebae.com
        How many accounts do you want to watch the page: 5
        \n\n\n\n\n\n\n\n
        Disclaimer: This project was made for educational purposes only. 
        Please use responsibly.
        '''
        )

if(__name__ == "__main__"):
    # Ignore insecure messages
    requests.packages.urllib3.disable_warnings()

    # Display intro text
    intro()

    # Get the link to watch
    in_link = ""
    while(not in_link.startswith("http")):
        in_link = input("What link do you want to watch: ").strip()
        if(not in_link.startswith("http")):
            print("Hold up, that doesn't make sense. Let's try again.")

    # Get the user's catch-all domain
    in_domain = ""
    while(in_domain == ""):
        in_domain = input("What is your catch-all domain (ex. ebae.com): ").strip()

        # Do some basic error checking on the domain
        if(in_domain.startswith('@')):
            in_domain = in_domain[1:]

        if(in_domain.count('.') == 0):
            print("Hold up, that doesn't make sense. Let's try again.")
            in_domain = ""

    # Get number of tasks to start
    watches = 0
    while(watches == 0):
        in_watches = input("How many accounts do you want to watch the page: ")
        try:
            watches = int(in_watches)
        except:
            print("That's not a number! Try again.")

    # Ensure proxies are loaded properly
    proxy_check = False
    print("Please ensure your proxies in a file named proxies.txt in the same folder as this script.")
    while(not proxy_check):
        raw_proxy = input("Type the name of the proxy file to continue: ")
        if(raw_proxy == "proxies.txt"):
            proxy_check = True
        else:
            print("Please ensure your proxy file is named proxies.txt and try again.")

    # Load proxies
    proxy_list = read_from_txt("proxies.txt")

    # Start tasks
    tasks = []
    for i in range(0, watches):
        log('i', "Starting task " + str(i + 1) + "...")
        eInstance = eBae(in_link, in_domain)
        t = Thread(target=eInstance.start)
        t.start()
        tasks.append(t)

    # Finish all the tasks
    for t in tasks:
        t.join()

    input("Done all tasks. Press any key to exit.")
