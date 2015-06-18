
# coding: utf-8

# In[1]:

import os
import pycurl
from io import BytesIO 
import certifi 
import difflib
import sys, traceback
import stem.process
from stem.util import term


# In[2]:

def query(url, istor, SOCKS_PORT = 7000):
  """
  Uses pycurl to fetch a site
  """
  output = BytesIO()

  query = pycurl.Curl()
  query.setopt(pycurl.CAINFO, certifi.where())
  query.setopt(pycurl.FOLLOWLOCATION, 1)
  
  if istor:
        #setup proxy
        query.setopt(pycurl.PROXY, 'localhost')
        query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
        query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
        
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.WRITEFUNCTION, output.write)
  
  try:
    query.perform()
    return output.getvalue()
  except pycurl.error as exc:
    return "Unable to reach %s (%s)" % (url, exc)


# In[3]:

def print_bootstrap_lines(line):
  if "Bootstrapped " in line:
    print(line)


# In[5]:

#start the Tor process

SOCKS_PORT = 7000
print(term.format("Starting Tor:\n", term.Attr.BOLD))

tor_process = stem.process.launch_tor_with_config(
  config = {
    'SocksPort': str(SOCKS_PORT),
    'ExitNodes': '{se}',
  },
  init_msg_handler = print_bootstrap_lines,
)


# In[13]:

#visit urls

allurls = open('alexa100.csv','r')
try:
    #need to find a way to get the exit ip
    savefile = 'files/'
    if not os.path.exists(savefile):
        os.makedirs(savefile)
        
    
    i = 0
    for aurl in allurls:
        
        if i>20:
            break
        i+=1
        
        aurl = aurl.replace('\n','')
        print(aurl)
        page_tor = query(aurl, True)
        page_regular = query(aurl, False)

        if isinstance(page_tor, bytes):
            page_tor = page_tor.decode('ISO-8859-1')
        if isinstance(page_regular, bytes):
            page_regular = page_regular.decode('ISO-8859-1')
        
        out = open(savefile + aurl.split('.')[1]+'_tor.html','w')
        out.write(page_tor)
        out.close()
        
        out = open(savefile + aurl.split('.')[1]+'.html','w')
        out.write(page_regular)
        out.close()
        
        diff = difflib.ndiff(page_tor.splitlines(1), page_regular.splitlines(1))
        out = open(savefile + aurl.split('.')[1]+'_diff.html','w')
        out.write(''.join(diff))
        out.close()
        
        
except Exception as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exc()
    
finally:
    tor_process.kill()


# In[ ]:



