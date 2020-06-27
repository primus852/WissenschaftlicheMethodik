import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
import nltk
from nltk.corpus import stopwords
from shared import SharedUtils


class TweetSentiment:

    def __init__(self, folder='./data'):

        self.folder = folder
        self.stop_words = stopwords.words("english")

        self.negative_words_list = []
        self.positive_words_list = []

        # Download Stopwords
        nltk.download('stopwords')

        # Load the Word Lists
        self._load_words()

    def load_clean_data(self, filename):
        data = SharedUtils.load_csv(self.folder, filename, 0)
        data = data[['text', 'is_retweet', 'created_at']]

        # Split the dates
        date_format = "%m-%d-%Y %H:%M:%S"
        data["created_at"] = pd.to_datetime(data["created_at"], format=date_format)
        data["hour"] = pd.DatetimeIndex(data["created_at"]).hour
        data["month"] = pd.DatetimeIndex(data["created_at"]).month
        data["day"] = pd.DatetimeIndex(data["created_at"]).day
        data["date"] = pd.DatetimeIndex(data["created_at"]).date
        data["month_f"] = data["month"].map(
            {1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 9: "SEP"})

        # Clean the Data
        data = self._string_manipulation(data, "text")

        # Count the Data
        retweet_values = data["is_retweet"].value_counts()

        # Extract retweets
        data = data[data["is_retweet"] == False].reset_index().drop(columns=["index"], axis=1)

        # Score the tweets
        data = self._scoring_tweets(data, "text")

        # Count the Sentiments
        sentiment_values = data["sentiment"].value_counts()

        return data, retweet_values, sentiment_values

    def plot_pct(self, values, title):
        plt.style.use('ggplot')

        plt.figure(figsize=(7, 6))
        values.plot.pie(autopct=lambda pct: self.format_plot_labels(pct, values), wedgeprops={"linewidth": 1, "edgecolor": "k"}, shadow=False, fontsize=15,
                        startangle=170, colors=["#689F38", "#BDBDBD", "#ff1744"])
        plt.ylabel("")
        plt.title(title)

        plt.show()

    @staticmethod
    def format_plot_labels(pct, allvals):
        absolute = int(pct / 100. * np.sum(allvals))
        return "{:.1f}%\n({:d})".format(pct, absolute)

    @staticmethod
    def filter_sentiment_score_by_date(df, week_end, week_start):
        data = df[(df['date'] <= week_end) & (df['date'] > week_start)]

        positive = data[data["sentiment"] == "positive"]
        negative = data[data["sentiment"] == "negative"]
        neutral = data[data["sentiment"] == "neutral"]

        score_max_week = data["score"].max()
        score_min_week = data["score"].min()

        if score_max_week < 0 and score_min_week < 0:
            peak_sentiment_week = "negative"
        elif score_max_week > 0 > score_min_week:
            if abs(score_max_week) > abs(score_min_week):
                peak_sentiment_week = "positive"
            elif abs(score_max_week) < abs(score_min_week):
                peak_sentiment_week = "negative"
            else:
                peak_sentiment_week = "neutral"
        elif score_max_week > 0 and score_min_week > 0:
            peak_sentiment_week = "positive"
        else:
            peak_sentiment_week = "neutral"

        if max(len(positive), len(negative), len(neutral)) == len(positive):
            sentiment = "positive"
        elif max(len(positive), len(negative), len(neutral)) == len(negative):
            sentiment = "negative"
        else:
            sentiment = "neutral"

        mean = data["score"].mean()
        std = data["score"].std()

        return sentiment, mean, std, score_max_week, score_min_week, peak_sentiment_week

    def _load_words(self):
        # Load positive Word List
        positive_words = SharedUtils.load_csv(self.folder, 'positive-words.txt')
        pre_positive_words_list = self._convert_words_list(positive_words)

        # Remove Trump from positive
        self.positive_words_list = [i for i in pre_positive_words_list if i not in "trump"]

        # Load negative Word List
        negative_words = SharedUtils.load_csv(self.folder, 'negative-words.txt')
        self.negative_words_list = self._convert_words_list(negative_words)

    # function to score tweets based on positive and negative words present
    def _scoring_tweets(self, df, text_column):
        # identifying +ve and -ve words in tweets
        df["positive"] = df[text_column].apply(
            lambda x: " ".join([i for i in x.split() if i in self.positive_words_list]))
        df["negative"] = df[text_column].apply(
            lambda x: " ".join([i for i in x.split() if i in self.negative_words_list]))
        # scoring
        df["positive_count"] = df["positive"].str.split().str.len()
        df["negative_count"] = df["negative"].str.split().str.len()
        df["score"] = (df["positive_count"] - df["negative_count"])

        df["sentiment"] = df.apply(lambda x: self.labeling(x), axis=1)

        return df

    # create new feature sentiment :
    # +ve if score is +ve , #-ve if score is -ve , # neutral if score is 0
    @staticmethod
    def labeling(df):
        if df["score"] > 0:
            return "positive"
        elif df["score"] < 0:
            return "negative"
        elif df["score"] == 0:
            return "neutral"

    def _convert_words_list(self, df):
        words = self._string_manipulation(df, 0)
        words_list = words[words[0] != ""][0].tolist()
        return words_list

    # function to remove special characters , punctions ,stop words ,
    # digits ,hyperlinks and case conversion
    def _string_manipulation(self, df, column):
        # extract hashtags
        df["hashtag"] = df[column].str.findall(r'#.*?(?=\s|$)')
        # extract twitter account references
        df["accounts"] = df[column].str.findall(r'@.*?(?=\s|$)')

        # remove hashtags and accounts from tweets
        df[column] = df[column].str.replace(r'@.*?(?=\s|$)', " ")
        df[column] = df[column].str.replace(r'#.*?(?=\s|$)', " ")

        # convert to lower case
        df[column] = df[column].str.lower()
        # remove hyperlinks
        df[column] = df[column].apply(lambda x: re.split('https:\/\/.*', str(x))[0])
        # remove punctuations
        df[column] = df[column].str.replace('[^\w\s]', " ")
        # remove special characters
        df[column] = df[column].str.replace("\W", " ")
        # remove digits
        df[column] = df[column].str.replace("\d+", " ")
        # remove under scores
        df[column] = df[column].str.replace("_", " ")
        # remove stopwords
        df[column] = df[column].apply(lambda x: " ".join([i for i in x.split() if i not in self.stop_words]))
        return df
