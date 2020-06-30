import TweetSentiment as ts
import AvocadoPrice as ap
from datetime import datetime, timedelta
from shared import SharedUtils
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == '__main__':

    # Tweets of Donald Trump
    tweet_sentiment = ts.TweetSentiment()
    # http: // www.trumptwitterarchive.com / archive
    tweets, retweet_values, sentiment_values = tweet_sentiment.load_clean_data('tweets.csv')

    # Date Range of Tweets
    earliest_tweet = tweets['created_at'].min(skipna=True)
    latest_tweet = tweets['created_at'].max(skipna=True)

    # Total Tweets
    total_tweets = retweet_values[False] + retweet_values[True]

    # Plot Retweet Percentage
    tweet_sentiment.plot_pct(retweet_values,
                             "Tweets sind Retweet\n{} - {}".format(earliest_tweet.date(), latest_tweet.date()))

    # Plot Sentiment Percentage
    tweet_sentiment.plot_pct(sentiment_values,
                             "Verteilung der Sentiments\n{} - {}".format(earliest_tweet.date(), latest_tweet.date()))

    # Get Best and worse Tweets
    tweet_happiest, tweet_grumpiest, tweet_median, tweet_mean, tweet_std = tweet_sentiment.get_stats(tweets)

    # Print TRUMP for Präsi
    print('TRUMP | Zeitraum {} - {}'.format(earliest_tweet, latest_tweet))
    print('TRUMP | Total Tweets {}'.format(total_tweets))
    print('TRUMP | Ohne ReTweets {}'.format(retweet_values[False]))
    print('TRUMP | Positivster Tweet: {}'.format(tweet_happiest))
    print('TRUMP | Negativster Tweet: {}'.format(tweet_grumpiest))
    print('TRUMP | Median Score: {}'.format(tweet_median))
    print('TRUMP | Mean Score: {}'.format(tweet_mean))
    print('TRUMP | Std Score: {}'.format(tweet_std))
    print('--------------------')

    # Weekly prices of Avocados, every sunday
    avocado_price = ap.AvocadoPrice()

    # Source: http://www.hassavocadoboard.com/retail/volume-and-price-data
    prices = avocado_price.load_data('avocado.csv')

    earliest_price = datetime.strptime(prices['Date'].min(skipna=True), "%Y-%m-%d")
    latest_price = datetime.strptime(prices['Date'].max(skipna=True), "%Y-%m-%d")

    # Print AVOCADO for Präsi
    print('AVOCADO | Zeitraum {} - {}'.format(earliest_price, latest_price))
    print('AVOCADO | Total Data {}'.format(len(prices)))

    current_sunday = earliest_price.date()
    last_sunday = latest_price.date()

    avocado_price_list = []
    trump_avocado_list = []

    while current_sunday <= last_sunday:
        price_day = current_sunday
        last_week_day = price_day - timedelta(days=7)

        # Compare Avocado Prices to Last Week
        last, this, pct, absolute = avocado_price.compare_prices(prices, price_day, last_week_day)

        avocado_price_list.append({
            'week': 'KW{}/{}'.format(current_sunday.isocalendar()[1], current_sunday.year),
            'price': round(this, 2)
        })

        # Standard Deviation = confusing week? Volatile Prices for avocados?
        sentiment, avg_score, std_score, max_score, min_score, peak_sentiment, amount = tweet_sentiment.filter_sentiment_score_by_date(
            tweets, price_day,
            last_week_day)

        trump_avocado_list.append({
            'price': this,
            'std_score': std_score,
            'max_score': max_score,
            'min_score': min_score,
            'avg_score': avg_score,
            'count': amount
        })

        print(
            '{} - {} | Last: {:0.2f} | This: {:0.2f} | Pct: {} | Abs: {} | {} | Score {} | Std: {} | Max: {} | Min: {} | Peak: {}'.format(
                last_week_day, price_day, last, this, SharedUtils.prefix(pct), SharedUtils.prefix(absolute), sentiment,
                SharedUtils.prefix(avg_score), SharedUtils.prefix(std_score), SharedUtils.prefix(max_score),
                SharedUtils.prefix(min_score), peak_sentiment))

        # Next week
        current_sunday = current_sunday + timedelta(days=7)

    avocado_price.save_price_week_csv(avocado_price_list)

    # Get some stats for the "Statistical View"
    avocados, price_min, date_min, price_max, date_max, price_std, price_median, price_mean, highest_gain, highest_gain_date, highest_loss, highest_loss_date = avocado_price.get_stats_week()

    print('AVOCADO | Preisspanne: {} ({}) - {} ({})'.format(price_min, date_min, price_max, date_max))
    print('AVOCADO | Standardabweichung: {}'.format(price_std))
    print('AVOCADO | Median: {}'.format(price_median))
    print('AVOCADO | Mittelwert: {}'.format(price_mean))
    print('AVOCADO | Höchster Anstieg: {} ({})'.format(highest_gain, highest_gain_date))
    print('AVOCADO | Tiefster Fall: {} ({})'.format(highest_loss, highest_loss_date))

    # Pearson Correlation
    df_analyze = pd.DataFrame(trump_avocado_list,
                              columns=['price', 'std_score', 'max_score', 'min_score', 'avg_score', 'count']).fillna(0)
    corr_p = stats.pearsonr(df_analyze['price'],df_analyze['avg_score'])
    print('STATS | PEARSON R')
    print(corr_p)

    corr_s = stats.spearmanr(df_analyze['price'],df_analyze['avg_score'])
    print('STATS | SPEARMAN')
    print(corr_s)

    df_analyze = SharedUtils.normalize(df_analyze)

    sns.distplot(df_analyze['avg_score'], hist=True, kde=True, color='blue', hist_kws={'edgecolor': 'black'})
    # Add labels
    plt.title('Histogram Sentiment Score (n=169)')
    plt.xlabel('Score')
    plt.ylabel('No. Weeks')
    plt.show()

    sns.distplot(df_analyze['price'], hist=True, kde=True, color='blue', hist_kws={'edgecolor': 'black'})
    # Add labels
    plt.title('Histogram Price (n=169)')
    plt.xlabel('Price')
    plt.ylabel('No. Weeks')
    plt.show()

    # Scatter
    plt.scatter(x=df_analyze['price'], y=df_analyze['avg_score'])
    plt.xlabel('Price')
    plt.ylabel('Avg. Score')
    plt.show()

    # Covarianz
    covariance_avg = np.cov(df_analyze['price'], df_analyze['avg_score'])
    print('STATS | COVARIANZ')
    print(covariance_avg)



    exit()
