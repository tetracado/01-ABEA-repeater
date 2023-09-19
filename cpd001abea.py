import cpd001sel
from selenium import webdriver
import platform
#from webdriver_manager.chrome import ChromeDriverManager
#from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import re
import albertamunis

def ab_getalertlink(link):
    cpd001sel.openlink(link)

    #check if no alerts

    try:
        if cpd001sel.driver.find_element(By.CLASS_NAME, "goa-callout"): #updated to goa-callout for noalerts
            print('no alerts')
            #cpd001sel.driver.close()
            return(None)
    except NoSuchElementException:
            print('couldnt find noalerts')
            pass

    
    #check for crit and info alerts and cancelled alerts

    if cpd001sel.driver.find_element(By.CLASS_NAME, "goa-alert"):
        allalerts=cpd001sel.driver.find_elements(By.CLASS_NAME, "goa-alert")
        print ('found', (len(allalerts)), 'alerts')
        for alert in allalerts:
            #print ('finding alerts')
            try: #crit alert
                 if (alert.find_element(By.CLASS_NAME, "goa-alert--top-red")):
                        print('found crit alert')
                        linkornone=processalert(alert)
                        if linkornone!=None:
                             return linkornone
            except NoSuchElementException:
                 try: #info alert 
                     if (alert.find_element(By.CLASS_NAME, "goa-alert--top-yellow")):
                            print('found info alert')
                            linkornone=processalert(alert)
                            if linkornone!=None:
                                return linkornone
                 except NoSuchElementException:
                      try: #cancelled alert
                            if (alert.find_element(By.CLASS_NAME, "goa-alert--top-grey")):
                                print('found cancel alert')
                                linkornone=processalert(alert)
                                if linkornone!=None:
                                    return linkornone
                      except NoSuchElementException:
                        print('couldnt find link')
                        continue
                 
            # OLD VERSION:
            # print ('finding info alert')
            # try:
            #     if alert.find_element(By.CLASS_NAME, "goa-alert--top-yellow"):
            #         print('found info alert')
            #         infohtml=alert.find_element(By.TAG_NAME, "a").get_attribute("outerHTML")
            #         print('found outerhtml',infohtml)
            #         infolink=(re.findall('a href="(.*)" class="goa-alert--more-details-link"', infohtml))[0]
            #         print('got infolink',infolink)
            #         if ab_checkfordupes(infolink)==False:
            #             print('about to return critlink: ',infolink)
            #             return(infolink)
            # except NoSuchElementException:
            #      print('couldnt find infolink')
            #      pass

def processalert(alert):
    link=alert.find_element(By.TAG_NAME, "a").get_attribute("href")
    #print('found outerhtml',html)
    #link=(re.findall('a href="(.*)" class="goa-alert--more-details-link"', html))[0]
    print('got link',link)
    if ab_checkfordupes(link)==False:
        print('about to return link: ',link)
        return(link)

def reducetext(text):
     nlinks=re.findall(".*(\.com).*",text) + re.findall(".*(\.ca).*",text) + re.findall(".*(\.org).*",text)
     tlength=min(275-(25*len(nlinks)), len(text))
     if (len(nlinks)==0) and (len(text)<275):
         outtext=text
     else:
         outtext=text[:tlength]+"..."
     return outtext

def reducetextsumm(text):
     nlinks=re.findall(".*(\.com).*",text) + re.findall(".*(\.ca).*",text) + re.findall(".*(\.org).*",text)
     tlength=min(240-(25*len(nlinks)), len(text))#to account for the constant 25char imgur link
     #print('got nlinks from reducetextsumm',nlinks)
     #print('got tlength from reducetextsumm', tlength)
     if (len(nlinks)==0) and (len(text)<240):
         outtext=text
     else:
         outtext=text[:tlength]+"..."
     return outtext

def ab_savedetails(link):

    cpd001sel.openlink(link)
    details={}
    details['link']="For more information, see the alert on the Alberta Emergency Alert webpage: "+link
    
    #alert_title=cpd001sel.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[1]/table/tbody/tr/td[1]/span").text
    #details['alert_title']=alert_title
    #print('added alert_title: ',alert_title)

    #get alert title
    try:
        if cpd001sel.driver.find_element(By.XPATH, "/html/body/main/div[1]/div[2]/div/div[1]/div[1]/h2"):
            alert_title=cpd001sel.driver.find_element(By.XPATH, "/html/body/main/div[1]/div[2]/div/div[1]/div[1]/h2").text
            details['alert_title']=alert_title
            print('added alert_title: ',alert_title)
    except NoSuchElementException:
            print('couldnt find alert title, subbing blank')
            details['alert_title']=''
            pass

    #get from town
    try:
        if cpd001sel.driver.find_element(By.XPATH, "/html/body/main/div[1]/div[2]/div/div[2]/div[1]/p[1]"):
            from_town=cpd001sel.driver.find_element(By.XPATH, "/html/body/main/div[1]/div[2]/div/div[2]/div[1]/p[1]").text
            if "Source: " == from_town[:8]: 
                from_town=from_town[8:] #remove "Source"
            hash=albertamunis.allmunis.get(from_town)
            if hash != None:
                 hash=" " + hash
                 details['from_town']=from_town + hash
            else:   
                details['from_town']=from_town
            print('added from_town: ',from_town)
            
    except NoSuchElementException:
            print('couldnt get from town, subbing blank')
            details['from_town']=''
            pass

    #get issued
    try:
        if cpd001sel.driver.find_element(By.XPATH, "/html/body/main/div[1]/div[2]/div/div[2]/div[1]/p[2]"):
            issued=cpd001sel.driver.find_element(By.XPATH, "/html/body/main/div[1]/div[2]/div/div[2]/div[1]/p[2]").text
            details['issued']=issued
            print('added issued: ',issued)
    except NoSuchElementException:
            print('coudlnt get issued date, subbing blank')
            details['issued']=''
            pass

    #alertsumm=alert_title+from_town+issued
    #print('concated alertsumm: ',alertsumm)

    try:
        alertsumm="#ABemerg | "+alert_title+" | "+from_town+" | "+issued
        print('concated alertsumm: ',alertsumm)
        details['alertsumm']=reducetextsumm(alertsumm)
    except:
        details['alertsumm']=""

    #get descriptrion from two paragraphs, combine to one then reduce if possible

    #paragraph 1
    try:
        if cpd001sel.driver.find_element(By.XPATH, '/html/body/main/div[1]/div[2]/div/div[2]/p[1]'):
            description1=cpd001sel.driver.find_element(By.XPATH, '/html/body/main/div[1]/div[2]/div/div[2]/p[1]').text
    except NoSuchElementException:
            print('coudlnt find description1, subbing blank')
            description1=''
            pass
    
    #paragraph 2
    try:
        if cpd001sel.driver.find_element(By.XPATH, '/html/body/main/div[1]/div[2]/div/div[2]/p[2]'):
            description2=cpd001sel.driver.find_element(By.XPATH, '/html/body/main/div[1]/div[2]/div/div[2]/p[2]').text
    except NoSuchElementException:
            print('couldnt find description2, subbing for blank')
            description2=""
            pass
    
    #combine descriptions, apparently multiline strings work??
    try:
         description=description1+"""

"""+description2
         details['description']=reducetextsumm(description) #use summ for this to prepare for imgurlink
         print('added description: ',description)
    except:
         print('couldnt combine descriptions, subbing blank')
         details['description']=''
         pass

    #get evac map, 
    try:
        if cpd001sel.driver.find_element(By.XPATH, '/html/body/main/div[1]/div[2]/div/div[2]/ul[3]'):
            for i in range(10):
                istr=str(i)
                xpath="/html/body/main/div[1]/div[2]/div/div[2]/ul[3]/li["+istr+"]/a"
                print('trying xpath:',xpath)
                try:
                    reslink=cpd001sel.driver.find_element(By.XPATH, xpath).get_attribute("href")
                    #imglink=(re.findall('a href="(.*)" ',reslink))[0]
                    print('testing imglink',reslink)
                    #print(imglink)
                    if any([x in reslink for x in [".jpg", ".jpeg", ".png", ".gif"]]):
                        print('got resource link:',reslink)
                        details['rsclink']=reslink
                        break
                except NoSuchElementException:
                    print('not in this bullet')
                    continue
    except NoSuchElementException:
            print('couldnt find resource list, subbing blank')
            details['rsclink']=''
            pass
    
    #get instructions
    try:
        if cpd001sel.driver.find_element(By.XPATH, '/html/body/main/div[1]/div[2]/div/div[2]/ul[2]'):
            instructions=cpd001sel.driver.find_element(By.XPATH, '/html/body/main/div[1]/div[2]/div/div[2]/ul[2]').text
            instructions=re.sub('\n',' | ', instructions)
            details['instructions']=reducetext(instructions)
            print('added instructions: ',instructions)
    except NoSuchElementException:
            print('couldnt find instructions, subbing blank')
            details['instructions']=''
            pass
    print(details)
    return(details)

def ab_checkfordupes(link):
    #testlink=str(ab_getalertlink(link))
    #testlink='https://stackoverflow.com/questions/5226893/understanding-a-chain-of-imports-in-python'
    #abealink='http://www.emergencyalert.alberta.ca/alerts/2022/06/10027.html'
    try:
        fhand=open('usedlinks.txt','r+')
        print('opened usedlinks.txt')
        found=False
        for line in fhand:
            #print('checking',line.rstrip())
            if link in line:
                print('EXITING!! found testlink:',link)
                found=True
                fhand.close()
                print('retained and closed usedlinks.txt')
                return(True)
                break
        if found==False:
            print('adding new link:',link)
            #cpd001sel.openlink(link)
            fhand.write(link+'\n')
            fhand.close()
            print('wrote and closed usedlinks.txt')
            return(False)
    except:
        print('couldnt find link')
        found=False

#ab_checkfordupes('https://stackoverflow.com/questions/5226893/understanding-a-chain-of-imports-in-python')

#if ab_checkfordupes('f')==False:
#    cpd001sel.savescnclose()

# teststring="Instruction: The risk of wildfire remains due to continuing isolated ground fires. Be aware of possible flare-ups as temperatures and winds continue to pose a risk. If the situation changes, another Alberta Emergency Alert will be issued. Gather pets, important documents and medication, and enough food, water, and supplies for at least 3 days."
# print(len(reducetext(teststring)))

#testruns
#ab_savedetails("https://www.alberta.ca/aea/cap/2023/06/11/2023-06-11T18_12_39-06_00=YellowheadCounty=04C9D750-5538-4585-B681-4EB2A7F457AA.htm")
#ab_savedetails("https://www.alberta.ca/aea/cap/2023/06/23/2023-06-23T15_17_13-06_00%3DBrazeauCounty%3DBB234E65-BC1C-48A3-8078-75A22F5D1CE9.htm")
#ab_savedetails("https://www.alberta.ca/aea/cap/2023/06/23/2023-06-23T16_40_54-06_00%3DWoodlandsCounty%3DE8A86B06-01B8-4F6D-8396-49ABB9D19FEA.htm")