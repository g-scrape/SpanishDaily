# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 16:01:09 2022

@author: glens
"""
#news API Key: 1410e45925c849f48b78138091c1635a
import requests
from bs4 import BeautifulSoup
import textstat
import os
import mysql.connector
#set library lang to espanol
textstat.set_lang('es')
from mailApp import sendEmail

def getNewsUrls(subject):
    from datetime import date
    date = date.today()
    date = date.strftime("%Y-%m-%d")

    url = ('https://newsapi.org/v2/everything?'
           'q='+subject+'&'
           'language=es&'
           'from='+date+'&'
           'sortBy=popularity&'
           'apiKey=1410e45925c849f48b78138091c1635a')

    response = requests.get(url)
    print('response: ' + str(response))
    articles = response.json()['articles']
    articleUrls = []

    for x in range(len(articles)):
        articleUrls.append(articles[x]['url'])

    return(articleUrls)


def evaluateDifficulty(urls):
    difficulty = []
    for url in urls:
        try:
            res = requests.get(url)
            if str(res) == '<Response [200]>':
                soup = BeautifulSoup(res.text, 'html.parser')
                text = soup.find('body').text
                rating = textstat.fernandez_huerta(text)
                entry = [url, rating]
                difficulty.append(entry)
                print('ranking successful')
            else:
                continue
        except:
            print('error occured')
            continue
    print(difficulty)
    return difficulty


#function to assign human readable difficulty level and obtain the 'easiest' mesaured article.
#collecting easiest article in case no easy or very easy articles returned
#probably should do the same for difficulty...
def sortUrlsByDiff(articles):
    count = 0
    urlDict = {'Very Confusing': [], 'Difficult': [], 'Fairly Difficult': [],'Standard': [],'Fairly Easy':[], 'Easy': [],'Very Easy':[]}
    difficulty = []
    while count < (len(articles) - 1) and any(n == [] for n in urlDict.values()):

        #print('Count: ' + str(count))
        url = articles[count]
        #print('URL: ' + url)
        try:
                res = requests.get(url)
                if str(res) == '<Response [200]>':
                    soup = BeautifulSoup(res.text, 'html.parser')
                    text = soup.find('body').text
                    rating = textstat.fernandez_huerta(text)
                    urlRank = [url, rating]
                    difficulty.append(urlRank)
                    if rating < 30:
                        urlDict['Very Confusing'].append(url)
                    elif rating < 50:
                        urlDict['Difficult'].append(url)
                    elif rating < 60:
                        urlDict['Fairly Difficult'].append(url)
                    elif rating < 70:
                        urlDict['Standard'].append(url)
                    elif rating < 80:
                        urlDict['Fairly Easy'].append(url)
                    elif rating <= 90:
                        urlDict['Easy'].append(url)
                    elif rating > 90:
                        urlDict['Very Easy'].append(url)
                    print('Assigned: ' + str(rating))
                    count += 1
                else:
                    print('Unexpected Response: ' + str(res))
                    count += 1
                    continue
        except:
                print('error occured')
                count += 1
                continue
    difficulty.sort(key = lambda x: x[1])
    hardestArticle = difficulty[0]
    easiestArticle = difficulty[len(difficulty)-1]
    return urlDict, easiestArticle, hardestArticle

#assigns only 1 article per difficulty and hydrates missing difficulties
def trimUrlList(results):
    #parse out variables from list
    urlDict = results[0]
    easiestArticle = results[1]
    easiestArticleUrl = easiestArticle[0]
    easiestArticleRating = easiestArticle[1]

    hardestArticle = results[2]
    hardestArticleUrl = hardestArticle[0]
    hardestArticleRating = hardestArticle[1]

    #assign difficulty rating
    if easiestArticleRating > 90:
        easiestArticleRating = 'Very Easy'
    elif easiestArticleRating > 80:
        easiestArticleRating = 'Easy'
    elif easiestArticleRating > 70:
        easiestArticleRating = 'Fairly Easy'
    elif easiestArticleRating > 60:
        easiestArticleRating = 'Standard'
    elif easiestArticleRating > 50:
        easiestArticleRating = 'Fairly Difficult'
    elif easiestArticleRating > 30:
        easiestArticleRating = 'Difficult'
    elif easiestArticleRating <= 30:
        easiestArticleRating = 'Very Confusing'

    #assign only a single URL per diff rating. Also assigns closest URL for unmatched hard or easy ratings
    for key, value in urlDict.items():
        if len(value) > 0:
            urlDict[key] = value[0]
        elif len(value) == 0:
            if key == 'Very Easy' or key == 'Easy' or key == 'Fairly Easy' or key == 'Standard':
                urlDict[key] = [easiestArticleUrl, easiestArticleRating] #need to account for this len == 2 situation if no article found
            elif key == 'Fairly Difficult' or key == 'Difficult' or key == 'Very Confusing':
                urlDict[key] = [hardestArticleUrl, hardestArticleRating] #need to account for this len == 2 situation if no article found
    return urlDict


#master function to combine all above based on just a topic search
def evalTopic(topic):
    urls = getNewsUrls(topic)
    urlDict = sortUrlsByDiff(urls)
    urlDict = trimUrlList(urlDict)
    return urlDict


def sendEmails(urlDict, topic):
    #connect to db
    exec(open('/home/gharold/utils/env_vars.py').read())
    connection = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        database=os.environ.get('DB_NAME')
    )

    topicTranslator = {
    'deportes': 'Sports',
    'noticias': 'News',
    'política': 'Politics',
    'viaje': 'Travel',
    'tecnología': 'Tech',
    'finanzas': 'Finance'
    }

    topic = topicTranslator[topic]

    #set cursor
    cur = connection.cursor(dictionary=True)
     #query db to pull all emails that have 'topic' as a preference
     ##SELECT email, spanishLevel, preference FROM users INNER JOIN preferences ON users.userId=preferences.preference WHERE preferences.preference = %s

     #topics = ['Sports', 'News', 'Politics', 'Travel', 'Tech', 'Finance']
    diffs = ['Very Easy', 'Easy', 'Fairly Easy', 'Standard', 'Fairly Difficult', 'Difficult', 'Very Confusing']

    print('urlDict: ')
    print(urlDict)
    #for every topic, loop through all spanish levels
    for diff in diffs:
        url = urlDict[diff]
        print('url: ')
        print(url)
        cur.execute("SELECT email, spanishLevel, preference FROM users INNER JOIN preferences ON users.userId=preferences.userId WHERE preferences.preference = %s AND users.spanishLevel = %s", (topic, diff))
        bcc = []
        results = cur.fetchall()
        for sDict in results:
            bcc.append(sDict['email'])
        print(bcc)
        sendEmail(url, diff, topic, bcc)

    cur.close()
    connection.close()
    return 'success'





topics = ['deportes', 'noticias', 'política', 'viaje', 'tecnología', 'finanzas']

for topic in topics:
    urlDict = evalTopic(topic)
    sendEmails(urlDict, topic)
#bug - articles being sent to non-subbed users, see politics and >1 news

print('Program Complete')