# Importing the relevant modules
import tweepy
from textblob import TextBlob
import matplotlib.pyplot as plot
import re
from wordcloud import WordCloud, STOPWORDS
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

# Declaring relevant Variables
polarityVal = []
positive = 0
negative = 0
neutral = 0 
subjectivityVal = []
tweetsArray = []
tweetsCloud = ''

# Creating the relevant variables used to connect to the Twitter Application
consumerKey = '6fJBysY6Tuv4DDCO1YJ3ZAufn'
consumerSecret = '2L1bAfvRqH5IowcoJpHiaOBBKC8ItBquV5cAaKQL7BOm1tm9Qi'
accessToken = '842338846968692736-6WTy7DNps4nwLCGdf2u8Z1Q0ikR9Vlk'
accessTokenSecret = 'wsEPHEu1LgZpEYNloUWuEk6iF86RaUaVH2Z8ZaShU9rAr'

# Authenticating the Twitter Application and creating an object to use the Twitter API
auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(auth)

# Search Term and the number of tweets to search
searchTerm = input("Enter Keyword/Tag to search about: ")
NoOfTerms = int(input("Enter how many tweets to search: "))

# Storing the tweets
tweets = tweepy.Cursor(api.search, q=searchTerm).items(NoOfTerms)

# Creating a list of String Tweets
for tweet in tweets:
    tweetsArray.append(tweet.text)

# Cleaning a Tweet String
def cleanTweet(tweet):
    # Remove Links, Special Characters etc from tweet
    return ' '.join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",tweet).split())
   
# Performing Sentiment Analysis
for tweet in tweetsArray:
    t = cleanTweet(tweet)
    print(t)
    tweetsCloud += t
    analysis = TextBlob(t)
    polarityVal.append(analysis.sentiment.polarity)
    subjectivityVal.append(analysis.sentiment.subjectivity)
	
# Required for Pie Chart
for value in polarityVal:
    if value > 0:
        positive += 1
    elif value < 0:
        negative += 1
    else:
        neutral += 1
labels = ['Positive','Negative','Neutral']
values = [positive,negative,neutral]

# WordCloud
wordcloud = WordCloud(width = 1600, stopwords=STOPWORDS, height = 800 , max_font_size= 200).generate(tweetsCloud)
plot.imshow(wordcloud, interpolation="bilinear")
plot.axis("off")
plot.show()

# Creating the Dashboard and Plotting Graphs
app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children='Kepak Group'),

    html.Div(children='''
        Sentiment Analysis
    '''),

    dcc.Graph(
        id='line',
        figure={
            'data': [
                {'y': polarityVal, 
                 'type': 'basic-line',},    
            ],
            'layout': {
                'title': 'Polarity Trend of the Tweets'
            }
        }
    ),
    
    dcc.Graph(
        id='pie',
        figure={
            'data': [
                go.Pie(labels=labels, values=values)
            ],
            'layout': {
                'title': 'Distribution of the Tweets'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)

    
    
