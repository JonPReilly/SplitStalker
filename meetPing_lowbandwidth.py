import sys
import os
import time
import requests
import logging
import urllib2
import difflib
import string

from bs4 import BeautifulSoup


from django.db import models
from django.core.mail import send_mail



class Meet:
    def __init__(self,name,url):
        self.name = name
        self.url = url

def openUrl(url):
    """
    Attempts to open a url and return it's html contents as a string
    On error, returns the empty string
    """
    try:
        print "Opening: " + url 
        req = urllib2.Request(url , headers={ 'User-Agent': 'Meetpingbot/1.0 (jonreilly1994@gmail.com http://splitstalker.com/botinfo)' })
        html = urllib2.urlopen(req).read()
    except Exception  as e:
        log.error("[MeetPing-openUrl] Error fetching " + url)
        return ""

    return html


def getMeetOrNone(url):
    try:
        z = LastMeet.objects.get(last_url=url)
    except ObjectDoesNotExist:
        return None
    return z


def getNewMeets(xmlsoup, MOST_RECENT_LINK):
    new_meets = []

   # table = xmlsoup.find("table")
   # for row in table.findAll("tr"):
   #     for cells in row.findAll("td"):
   #         for link in cells.find_all("a"):
   #             url = str(link.get('href'))
   #             name = link.text
                
             #   if (getMeetOrNone(url) == None):
             #       processed = LastMeet(last_url = url, meets_processed=0, name=name)
	     #       processed.save()
             #       new_meet = Meet(name,url)
             #       new_meets.append(new_meet)

  #  return new_meets
    print xmlsoup.prettify()
    for meet in xmlsoup.find_all("item"):
        name = meet.find("title").text
        url =str(meet.link.next_sibling).replace("\n","")
        if (getMeetOrNone(url) == None):
	    processed = LastMeet(last_url = url, meets_processed=0,name=name)
            processed.save()
            new_meet = Meet(name,url)
            new_meets.append(new_meet)
        

    return new_meets[::-1]

def getCompiledMeets(new_meets):
    HTTPS_PROTOCOL = "https:"
    LOW_BANDWITH_QUERY = "?printable=1&popup=1"
    compiled_meets = []
    for  meet in new_meets:
        meet_woman = Meet(meet.name, HTTPS_PROTOCOL + meet.url.replace(".html","_f.html") + LOW_BANDWITH_QUERY)
        meet_men = Meet(meet.name, HTTPS_PROTOCOL + meet.url.replace(".html","_m.html") + LOW_BANDWITH_QUERY)
        compiled_meets.append(meet_woman)
        compiled_meets.append(meet_men)
    return compiled_meets

def similarityRatio(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def updateRaceParse(race_parse):
    if (race_parse == 2):
        return 0
    return race_parse + 1

def getName(data_cell):
    print data_cell
    name = data_cell[2].split(",")
    name[1] = name[1].replace(" " , "")
    name[0] = name[0].replace(" " , "")
    return name[::-1]
def getSchool(data_cell):
    return data_cell[4]


def correctAthleteLikely(athletes, FIRST_NAME, LAST_NAME, SCHOOl):
    for ath in athletes:
        simval = 0
        name = ath.name.split(" ")
        school = ath.school
        simval += similarityRatio(name[0].lower(), FIRST_NAME.lower())
        simval += similarityRatio(name[1].lower(), LAST_NAME.lower())
        simval += similarityRatio(school.lower(), SCHOOl.lower())
        simval /= 3

        if (simval >= .95 ):
            return ath.id
    return -1

def isBeingFollowed(name,school):
    FIRST_NAME = str(   filter( lambda x: x in string.printable,  name[0] )    )
    LAST_NAME = str( filter ( lambda x: x in string.printable,  name[1] ) )
    followed = Athlete.objects.filter(name__icontains= LAST_NAME).filter(name__icontains = FIRST_NAME)

    pk = correctAthleteLikely(followed, FIRST_NAME, LAST_NAME, school)
    

    return pk

def parseEvent(race,Current_race):
    #print "Cirremt race: " , Current_race
    email_stubs = []
    for row in race.findAll("tr"):
        data_cell = []
        for cells in row.findAll("td"):
            data_cell.append(cells.text.replace("\n","").replace("\t",""))
        
        pk = isBeingFollowed(getName(data_cell), getSchool(data_cell))
        if (pk != -1):
            followers = Stalker.objects.filter(following_athletes__id = pk)
            
            for follower in followers:
                data_copy = data_cell[:]
                place = data_copy[0]
                data_copy[0] = follower.user.email
                data_copy[len(data_copy) - 1] = place
                data_copy[1] = Current_race
                email_stubs.append(data_copy)
    
    return email_stubs

def constructName(namelist):
    return " ".join(namelist.split(",")[::-1])


def constructHtmlFromData(data_cell):
    html = ""

    html +=  constructName(str(data_cell[2]))

    return html


def ordinal(num):
    """
    Given a int, return a string containing it's ordinal value
    1 = '1st' , 2 = '2nd', and so on
    """
    SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
    
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = SUFFIXES.get(num % 10, 'th')
    return str(num) + suffix

def sendMailIndividual(send_to, stubs, url, name):
    LOW_BANDWITH_QUERY = "?printable=1&popup=1"
    usr = User.objects.get(email = send_to)
    addressing = usr.get_username() +",\n\n"
    html = addressing + "Athlete(s) you are following have just competed at the " + name + ":\n\n"
    
    for data in stubs:
        print data
        html += "\t" + constructHtmlFromData(data)
        html += " of " + data[4]
        if (not "m" in data[5]): 
            html += " has run a time of "
            html += ' '.join(data[5].split()) 
        else:
            html += " has achieved a distance of "
            html += ' '.join(data[5].split()) + " (" + ' '.join(data[6].split()) + ")"
        
        html +=  " in the " + ' '.join(data[1].split())
        html += ", placing " + ordinal( int(data[len(data) - 1].replace(".","") ) ) 

        html += "\n\n"

    html += "\nCheck out the full results for " + name + " at:" + url.replace(LOW_BANDWITH_QUERY,"")
    subject = usr.get_username() + ' - Athlete(s) you are following have run at the ' + name


    rc = send_mail(subject, html, 'SplitStalkerBot@gmail.com',[send_to], fail_silently=True)
    
    if(rc == 0): #failed to send email
        print "[" +  str(time.ctime()) + "]: "   + "Failed to send email"
        not_sent = FailedEmail(email = send_to, subject= subject, body = html )
        not_sent.save()
        log.error("[MeetPing-sendMail] Failed to send an email to: " + usr.get_username())
    else:
        log.info("[MeetPing-sendMail] Sucesfully sent email to: " + usr.get_username())


def sendMail(emails,url,name):
    mail = {}
    for x in emails:
        mail.setdefault(x[0], []).append(x)

    for send_to in mail:
        sendMailIndividual(send_to, mail[send_to], url, name)

def parseMeet(meet):
    
    r = openUrl(meet.url)
    #r = open("C:/Users/RebelLad/Desktop/StartingBlocks/StartingBlocks/lowband.html",'r').read()
    if (r is ""):
        return False
    soup = BeautifulSoup(r, "html.parser")

    races = soup.findAll("table")
    
    race_parse = 0
    Current_race = ""
    emails = []
    for race in races:
       
        if (race_parse == 0):
	    try:
                Current_race = race.find("h2").text.replace("\n","").replace("\t","")
            except AttributeError:
                Current_race = "[Unknown Race]"
                race_parse = 1

        if (race_parse == 2 and not "Relay" in Current_race and not "Medley" in Current_race):
            email_stubs = parseEvent(race,Current_race)
            
            for email in email_stubs:
               emails.append(email)

        race_parse = updateRaceParse(race_parse)

    if (emails != []):
        log.info("[MeetPing-parseMeet] Calling sendMail for " + meet.name)
        sendMail(emails, meet.url, meet.name)
    else:
        log.warning("[MeetPing-parseMeet] No emails to send for " + meet.name)

    return True


def main(argv): 

    # log.info("[MeetPing-main] Stating Up...")
    # time.sleep(10)
    LOW_BANDWITH_QUERY = "?printable=1&popup=1"
   # r = openUrl("https://www.tfrrs.org/results_search.html" + LOW_BANDWITH_QUERY)
    r = openUrl("https://www.tfrrs.org/rss/results.rss")


    if not (r is ""):
        soup = BeautifulSoup(r, "lxml")
        LAST_MEET_OBJECT = LastMeet.objects.get(pk=1)
        MOST_RECENT_LINK = LAST_MEET_OBJECT.last_url
        
        new_meets = getNewMeets(soup,MOST_RECENT_LINK)
        if (new_meets != []):
            print "New meets to check"
            new_meets = getCompiledMeets(new_meets)
            # rc = parseMeet(new_meets[0])
            for meet in new_meets:
                time.sleep(10)
                log.info("[MeetPing-main] Checking: " + meet.name)
                rc = parseMeet(meet)
                if not (rc):
                    log.error("[MeetPing] Error checking: " + meet.name + ", check logs")
                    print "Error parsing: " + meet.name
                    error = MiscError(
                        error_type = "MeetParse Error" , 
                        error_data = meet.url + meet.name , 
                        error_explination = "Unable to process meet" )
                    error.save()
                else:
                    log.info("[MeetPing-main] Succesfully processed: " + meet.name)
                    #NEW_RECENT_LINK = meet.url.replace("_m","").replace("_f","").replace("https:","").replace(LOW_BANDWITH_QUERY,"")
                    #LAST_MEET_OBJECT.last_url = NEW_RECENT_LINK
                    #LAST_MEET_OBJECT.meets_processed = LAST_MEET_OBJECT.meets_processed + 1
                    #LAST_MEET_OBJECT.save()         


        else:
            print "No new meets to check"
            log.info("[MeetPing-main] No new meets to check")

        

    else:
        error = MiscError(
            error_type = "TFRRS connection error" , 
            error_data = MOST_RECENT_LINK , 
            error_explination = "Unable to connect" )      
        error.save()
        log.error("[MeetPing-main] TFRRS connection error")
        raise Exception("TFRRS connection error")

    

if __name__ == "__main__":
    """
    Typically imports go at the front, but to use django objects
    """
   
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StartingBlocks.settings")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

    from django.contrib.auth.models import User
    from django.conf import settings
    from django.core.exceptions import ObjectDoesNotExist
    from signups.models import Stalker
    from signups.models import LastMeet
    from signups.models import Athlete
    from errors.models import FailedEmail
    from errors.models import MiscError

    log = logging.getLogger(settings.LOG_OBJECT)
    main(sys.argv[0:])
