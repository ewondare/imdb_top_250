
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re # for gross
import csv

try:

    url = "https://www.imdb.com/chart/top/?ref_=nv_mv_250"
    Headers = {  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" ,
                'Accept-Language': 'en-US,en;q=0.5'}
    response = requests.get(url , headers=Headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    movie_links = soup.find("ul" , class_="ipc-metadata-list ipc-metadata-list--dividers-between sc-3f13560f-0 sTTRj compact-list-view ipc-metadata-list--base").find_all("a", class_="ipc-title-link-wrapper")
    print(len(movie_links)) #to be sure there's actually 250 tags found
    urls = []
    titles = []
    moviesoups = []

    years = []
    parental_guides = []
    runtimes = []
    
    genres_list = []
    directors_list = []
    writers_list = []
    stars_list = []

    gross_us_canada_list = []

    movie_ids = {}
    movie_id_list = []
    person_ids = {}
    j = 1
    for link in movie_links:
        print(j)

        # Extract the movie title
        movie_name = link.h3.text
        titles.append(movie_name)
        # to get rid of the ranks before the movies:
        titles = [tag.split('. ', 1)[-1] for tag in titles]

        # Extract the movie URL
        movie_url = "https://www.imdb.com" + link["href"]
        urls.append(link["href"])

        # Extract the movie id
        href = link["href"]
        movie_id = ''.join(filter(str.isdigit, href.split('/')[-2])) #/title/tt0111161/ to '0111161'
        movie_id_list.append(movie_id)
        movie_ids[movie_name] = movie_id
  


            
        
        movie_response = requests.get(movie_url , headers=Headers )
        # Extract the movie soup
        movie_soup = BeautifulSoup(movie_response.text, "html.parser")
        moviesoups.append(movie_soup)

        # a variable just to help to find next wanted values
        #print("findhelp")
        findhelp = movie_soup.find("ul" , class_ ="ipc-inline-list ipc-inline-list--show-dividers sc-afe43def-4 kdXikI baseAlt").find_all("li" , class_="ipc-inline-list__item")
        if (len(findhelp) > 2):
            # Extract year
            year = findhelp[0].text
            print(year)
            years.append(year)
            # Extract  panrental_guide 
            pguide = findhelp[1].text
            parental_guides.append(pguide)
            # Extract the runtime
            runtime = findhelp[2].text
            runtimes.append(runtime)
        else:
            # Extract year
            year = 'NaN'
            years.append(year)
            # Extract  panrental_guide 
            pguide = 'Nan'
            parental_guides.append(pguide)
            # Extract the runtime
            runtime = 'NaN'
            runtimes.append(runtime)

        
        # Extract the genre(s)
        print("genre")
        findgenre = movie_soup.find("div" , class_="ipc-chip-list__scroller").find_all("a" , class_="ipc-chip ipc-chip--on-baseAlt")
        genrelist = []
        for g in findgenre:
            genrelist.append(g.text)
        genres_list.append(genrelist)

        # directors and writers 
        print("findhelp2")
        findhelp2 = movie_soup.find("div" , class_="sc-410d722f-1 cdbSXZ").find_all("li" , class_="ipc-metadata-list__item")
        
        # Extract the director(s) , person id
        print("director")
        if (len(findhelp2) > 0):

            finddirector = findhelp2[0].find_all("a" , class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
            
            direclist = []
            for d in finddirector:
                direclist.append(d.text)
                L = d['href']
                person_id = ''.join(filter(str.isdigit, L.split('/')[-2]))
                #turn the /name/nm0001104/?ref_=tt_ov_dr to nm0001104 and then to 0001104
                person_ids[d.text ] = person_id
            directors_list.append(direclist)
        else:
            direclist=['NaN']
            directors_list.append(direclist)

        # Extract the writer(s) , person id
        print("writer")
        if (len(findhelp2) > 0):
            writerfind = findhelp2[1].find_all("a" , class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
            writerlist = []
            for w in writerfind:
                writerlist.append(w.text)
                L = w['href']
                person_id = ''.join(filter(str.isdigit, L.split('/')[-2]))
                #turn the /name/nm0001104/?ref_=tt_ov_dr to nm0001104 and then to 0001104
                person_ids[w.text ] = person_id
            writers_list.append(writerlist)
        else:
            writerlist = ['NaN']
            writers_list.append(writerlist)


        # Extract the Stars , person id
        print("star")
        starfind = movie_soup.find("li" , class_="ipc-metadata-list__item ipc-metadata-list-item--link").find_all("a" , class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
        starlist = []

        for s in starfind:
            starlist.append(s.text)
            L = s['href']
            person_id = ''.join(filter(str.isdigit, L.split('/')[-2]))
            #turn the /name/nm0001104/?ref_=tt_ov_dr to nm0001104 and then to 0001104
            person_ids[s.text ] = person_id
        stars_list.append(starlist)

        # Extract the gross
        if (j == 110 or j == 219): #exception for hamilton which was in theather and therefore has no box office section
            grossfind = []
        else:
            print("gross")
            grossfind = movie_soup.find("ul" , class_="ipc-metadata-list ipc-metadata-list--dividers-none ipc-metadata-list--compact sc-6d4f3f8c-0 VdkJY ipc-metadata-list--base").find_all("li" , class_="ipc-metadata-list__item sc-6d4f3f8c-2 byhjlB")
        if (len(grossfind) > 1):   
            grosstext = grossfind[1].text
            gross =  int(re.sub("[^0-9]", "", grosstext)) #['Gross US & Canada$28,767,189'] => 28767189
        else:
            gross = 'NaN'
        gross_us_canada_list.append( gross )
        j+=1



    df = pd.DataFrame({
    'ID' : movie_id_list,
    'Title': titles,
    'Year': years,
    'Parental Guidelines': parental_guides,
    'Runtime': runtimes,
    'Genres': genres_list,
    'Directors': directors_list,
    'Writers' : writers_list,
    'Stars': stars_list,
    'Gross Us and Canada' : gross_us_canada_list
    })
    df.to_csv('250_top_movies_imdb.csv', index=False)
    print("done")

    field_names = ['Name', 'ID']
    rows = [{'Name': name, 'ID': id} for name, id in person_ids.items()]
    with open('person_ids.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)

    field_names = ['Name', 'ID']
    rows = [{'Name': name, 'ID': id} for name, id in movie_ids.items()]
    with open('movie_ids.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)


except Exception as e:
    print(e)


