import pandas as pd
import streamlit as st
import numpy as np
from ast import literal_eval
from googlesearch import search
from bs4 import BeautifulSoup
import requests

st.title("   \t\tMOVIES RECOMENDER")
st.markdown("created by Kavishankar K S"
#st.write("DATA SET")
#df=pd.read_csv('movies_metadata.csv')

#Only keep those features that we require 
#df = df[['title','genres', 'release_date', 'runtime', 'vote_average', 'vote_count']]

#st.write(df.head())

#st.write('COLUMNS IN DATA SET')
#st.write(df.describe())

# #Convert release_date into pandas datetime format
# df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

# #Extract year from the datetime
# df['year'] = df['release_date'].apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan)

# #Helper function to convert NaT to 0 and all other years to integers.
# def convert_int(x):
#     try:
#         return int(x)
#     except:
#         return 0
# #Apply convert_int to the year feature
# df['year'] = df['year'].apply(convert_int)

# df = df.drop('release_date', axis=1)

# #Convert all NaN into stringified empty lists
# df['genres'] = df['genres'].fillna('[]')

# #Apply literal_eval to convert stringified empty lists to the list object
# df['genres'] = df['genres'].apply(literal_eval)

# #Convert list of dictionaries to a list of strings
# df['genres'] = df['genres'].apply(lambda x: [i['name'].lower() for i in x] if isinstance(x, list) else [])

# #Create a new feature by exploding genres
# s = df.apply(lambda x: pd.Series(x['genres']),axis=1).stack().reset_index(level=1, drop=True)

# #Name the new feature as 'genre'
# s.name = 'genre'

# #Create a new dataframe gen_df which by dropping the old 'genres' feature and adding the new 'genre'.
# gen_df = df.drop('genres', axis=1).join(s)
#--------------------------------------------------------------------------------------
#saving processed and using this for next time
#gen_df.to_csv('Movies_processed.csv',index=False)
@st.cache
def load_date():
	pgen=pd.read_csv('Movies_processed.csv')
	return pgen
	#pgen.head()

pgen=load_date()
year=[]
for i in range(1990,2021):
   	year.append(i)


time=[]
for t in range(30,300,30):
    time.append(t)
time2=time[2:]
year2=year[10:]
genres=['action','drama','romance','animation','comedy','family','adventure']
@st.cache
def build_chart(pgen,genre,low_time,high_time,low_year,high_year, percentile=0.8):
    #Define a new movies variable to store the preferred movies. Copy the contents of gen_df to movies
    movies = pgen.copy()
    
    #Filter based on the condition
    movies = movies[(movies['genre'] == genre) & 
                    (movies['runtime'] >= low_time) & 
                    (movies['runtime'] <= high_time) & 
                    (movies['year'] >= low_year) & 
                    (movies['year'] <= high_year)]
    
    #Compute the values of C and m for the filtered movies
    C = movies['vote_average'].mean()
    m = movies['vote_count'].quantile(percentile)
    
    #Only consider movies that have higher than m votes. Save this in a new dataframe q_movies
    q_movies = movies.copy().loc[movies['vote_count'] >= m]
    
    #Calculate score using the IMDB formula
    q_movies['score'] = q_movies.apply(lambda x: (x['vote_count']/(x['vote_count']+m) * x['vote_average']) 
                                       + (m/(m+x['vote_count']) * C)
                                       ,axis=1)

    #Sort movies in descending order of their scores
    q_movies = q_movies.sort_values('score', ascending=False)
    
    return q_movies

#Generate the chart for top animation movies and display top 5.

#Ask for preferred genres
genre = st.selectbox("Select preferred genre",genres)
    
#Ask for lower limit of duration
#print("Input shortest duration")
low_time = st.selectbox("Input shortest duration",time)
    
#Ask for upper limit of duration
#print("Input longest duration")
high_time = st.selectbox("Input longest duration",time2)

error=0
if(high_time<=low_time):
	error=1
	st.error("High year should be more")
#Ask for lower limit of timeline
#print("Input earliest year")
low_year = st.selectbox('Input earliest year',year)
    
#Ask for upper limit of timeline
#print("Input latest year")
high_year = st.selectbox('Input latest year',year2)

@st.cache
def find(details):
	    for d in search(details, tld='co.in',lang='en',start=0,stop=1):
	        
	        site=d
	        req=requests.get(site)
	        
	        if req.status_code !=200 :
	            print("Error in getting information about date")
	            return 
	        soup=BeautifulSoup(req.content, 'html.parser')
	        data=' '
	        i=0
	        for l in soup.find_all('p'):
	            data+=l.text
	            data+='\n'
	        return data

if(high_year<=low_year):
	error=1
	st.error("High year should be more")
if(error==0):
	gen=build_chart(pgen,genre,low_time,high_time,low_year,high_year,)

	gen=gen.drop('genre',axis=1)
	gen.reset_index(drop=True, inplace=True)
	# In[24]:
	st.write("RECOMENDED MOVIES")

	st.write(gen.head(10))
	movies=st.selectbox("MOVIES",gen.head(10))

	if(st.button("Get details",help="Click to get full information about movie from internet")):
		d='wiki'+movies

		st.write(find(d))

# In[15]:


#Convert the cleaned (non-exploded) dataframe df into a CSV file and save it in the data folder
#Set parameter index to False as the index of the DataFrame has no inherent meaning.
#df.to_csv('metadata_clean.csv', index=False)

