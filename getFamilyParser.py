#Shane Lynes, Zachary Shakked, Cassidy Donlean, and Jhustin Scarlett
#I pledge my honor that I have abided by the Stevens Honor System

import os
import datetime
import unittest
from prettytable import PrettyTable

def genFamilyParser():
    infile = open('My-Family-23-Jan-2018-602.ged', 'r')

    personDic = {}
    familyDic = {}

    firstLevelTags = ['NOTE', 'HEAD', 'TRLR']
    firstLevelExceptions = ['INDI', 'FAM']
    secondLevelTags = ['NAME', 'SEX', 'BIRT', 'DEAT', 'MARR', 'DIV', 'FAMC', 'FAMS', 'HUSB', 'WIFE', 'CHIL']
    thirdLevelTags =['DATE']
    thirdLevelTagMonths = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    individualDic = {'NAME': 'Name', 'SEX': 'Sex', 'FAMC': 'Child', 'FAMS': 'Spouse'}
    importantDateDic = {'BIRT': 'Birthday', 'DEAT': 'Death', 'MARR': 'Marriage', 'DIV': 'Divorce'}
    parentDic = {'HUSB': ['Husband ID', 'Husband Name'], 'WIFE': ['Wife ID', 'Wife Name']} #defines the parent structure
    datesDic = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT' : '10', 'NOV' : '11', 'DEC' : '12'} #can make date in proper format with #
    
    currentID = ""
    currentDic = {}
    dateType = ''
    duplicateCheck = 0
    for line in infile:
        if line[0] == '0':
            duplicateCheck = 0
            if checkIfValidTagExc(line, firstLevelExceptions) is True:
                ln = line.split()
                if ln[2] == 'INDI':
                    if checkIfKeyInDictionaryExists(ln[1].replace("@", ""),personDic): #if key already in person dictionary
                        duplicateCheck = 1
                        continue #go to next iteration and do not include
                    currentID = ln[1].replace("@", "") #this replaces the"@" that was seen in the ID's of the GEDCOM file
                    personDic[currentID] = {'Name': '', 'Sex': '', 'Birthday': '', 'Age': '', 'Death': 'N/A', 'Alive': 'True', 'Spouse': 'N/A', 'Child': 'N/A'} #initializes our dictionaries
                    currentDic = personDic #we are now editing the individual dictionary
                elif ln[2] == 'FAM':
                    if checkIfKeyInDictionaryExists(ln[1].replace("@", ""),familyDic): #if key already in family dictionary
                        duplicateCheck = 1
                        continue #go to next iteration and do not include
                    currentID = ln[1].replace("@", "")
                    familyDic[currentID] = {'Marriage': '', 'Husband ID': '', 'Husband Name': '', 'Wife ID': '', 'Wife Name': '','Children': [], 'Divorce': 'N/A'}  #initializes our dictionaries
                    currentDic = familyDic #we are now editing the family dictionary
        elif line[0] == '1' and duplicateCheck != 1:
            if checkIfValidTag(line, secondLevelTags) is True:
               ln = line.split()
               if ln[1] in importantDateDic.keys():
                   dateType = importantDateDic[ln[1]] #get date type such as marriage, death, or birth
                   if dateType == 'Death':
                       personDic[currentID]['Alive'] = 'False' #if Death than make alive false in dic
               elif ln[1] in individualDic.keys():
                   tag = individualDic[ln[1]]
                   if ln[1] == 'NAME':
                       value = ''
                       for i in ln[2:]:
                           value += i + ' '
                       personDic[currentID][tag] = value[0:] #allows us to get the full name (including the last name)
                   else:
                       value = ln[2]
                       personDic[currentID][tag] = value.replace("@", "")
               else:
                   if ln[1] in parentDic.keys():
                       tags = parentDic[ln[1]]
                       familyDic[currentID][tags[0]] = ln[2].replace("@", "")
                       familyDic[currentID][tags[1]] = personDic[ln[2].replace("@", "")]['Name'] #put parents in the family dictionary
                   else:
                       familyDic[currentID]['Children'].append(ln[2].replace("@", "")) #put children in the family dictionary
        elif line[0] == '2' and duplicateCheck != 1:
            if checkIfValidTagMonth(line, thirdLevelTags, thirdLevelTagMonths) is True:
                 ln = line.split()
                 currentDic[currentID][dateType] = ln[4] + '-' + datesDic[ln[3]] + '-' + ln[2] #make date in the proper format as shown in the example on canvas
                 if currentDic == personDic:
                     personDic[currentID]['Age'] = getIndividualAge(currentID, personDic) #if we are in the person dictionary than give that person an age
                     
    
    peopleTable = PrettyTable(["ID", 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse'])

    personDic = checkUniqueNameBirthday(personDic)
    checkMalesNamesAreSame(personDic, familyDic)
    checkForPolygamy(familyDic, personDic)

    for key,val in sorted(personDic.items()):
        row = list([key, val['Name'], val['Sex'], val['Birthday'], val['Age'], val['Alive'], val['Death'], val['Child'], val['Spouse']])
        peopleTable.add_row(row)
    print('Individuals')
    print(peopleTable)

    familyTable = PrettyTable(["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])

    for key,val in sorted(familyDic.items()):
        row = list([key, val['Marriage'], val['Divorce'], val['Husband ID'], val['Husband Name'], val['Wife ID'], val['Wife Name'], val['Children']])
        familyTable.add_row(row)
    print('Families')
    print(familyTable)

    return personDic, familyDic



def getIndividualAge(personID, dic):
    currentDate = datetime.date.today()
    birthday = list(dic[personID]['Birthday'].split('-'))
    birthdayDate = datetime.date(int(birthday[0]), int(birthday[1]), int(birthday[2]))
    days = 0
    if dic[personID]['Alive'] == 'False':
        death = list(dic[personID]['Death'].split('-'))
        deathDate = datetime.date(int(death[0]), int(death[1]), int(death[2]))

    if dic[personID]['Alive'] == 'True': 
        days = (currentDate - birthdayDate).days
        years = days/365
    else:
        days = (deathDate - birthdayDate).days
        years = days/365
    return str(int(years))

def checkIfValidTag(line, tags):
      parts = line.split()
      if parts[1] in tags:
          return True
      else:
          return False

def checkIfValidTagExc(line, tags):
    parts = line.split()
    if len(parts) == 3:
        if parts[2] in tags:
            return True
        else:
            return False

def checkIfValidTagMonth(line, tags, tags1):
    parts = line.split()
    if len(parts) == 5:
        if parts[1] in tags:
            if parts[3] in tags1:
                return True
            else:
                return False
        else:
            return False


def checkUniqueNameBirthday(personDic):
    names = []
    birthdays = []
    values = {}
    for key,value in sorted(personDic.items()):
        if value['Birthday'] not in birthdays and value['Name'] not in names:
            names.append(value['Name'])
            birthdays.append(value['Birthday'])
            values[key] = value
        if value['Name'] in names and value['Birthday'] not in birthdays:
            names.append(value['Name'])
            birthdays.append(value['Birthday'])
            values[key] = value
    return values

def checkMalesNamesAreSame(personDic, familyDic):
    for key,family in familyDic.items():
        father = getPerson(family["Husband ID"], personDic)
        fathersLastName = getLastName(father)
        children = getChildren(family, personDic)
        for child in children:
            if child["Sex"] == "M" and getLastName(child) != fathersLastName:
                raise ValueError('Male child does not have same last name as father.')


def checkForPolygamy(familyDic, personDic):
    marriages = {}
    for key,family in familyDic.items():
        husbandID = family["Husband ID"]
        wifeID = family["Wife ID"]
        if "Divorced" in family:
            continue
        if not isPersonAlive(husbandID, personDic):
            continue
        if not isPersonAlive(wifeID, personDic):
            continue
        
        
        if wifeID in marriages:
            marriages[wifeID] += 1
        else:
            marriages[wifeID] = 1

        if husbandID in marriages:
            marriages[husbandID] += 1
        else:
            marriages[husbandID] = 1
             
    for key, count in marriages.items():
      if count > 1:
        raise ValueError('Polygamy has occurred.')        

    

# better smell, instead of duplicating if code, made a function
def checkIfKeyInDictionaryExists(line, dict):
    if line in dict.keys():
        return True
    else:
        return False

def getPerson(id, personDic):
    return personDic[id]

def getLastName(person):
    return person.get("Name").split('/')[1]
    
def getChildren(family, personDic):
    childrenIDs = family.get("Children")
    children = []
    for childrenID in childrenIDs:
        children.append(getPerson(childrenID, personDic))
    return children

def isPersonAlive(personID, personDic):
  if getPerson(personID, personDic)["Alive"] == "True":
      return True
  else:
      return False


genFamilyParser()
