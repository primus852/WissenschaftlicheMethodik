import TweetSentiment as ts
import AvocadoPrice as ap
from datetime import datetime, timedelta
from shared import SharedUtils

if __name__ == '__main__':

    tweet_sentiment = ts.TweetSentiment()
    avocado_price = ap.AvocadoPrice()

    # Tweets of Donald Trump
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

    # Print TRUMP for Präsi
    print('TRUMP | Zeitraum {} - {}'.format(earliest_tweet, latest_tweet))
    print('TRUMP | Total Tweets {}'.format(total_tweets))
    print('TRUMP | Ohne ReTweets {}'.format(retweet_values[False]))
    print('--------------------')

    # Weekly prices of Avocados, every sunday
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

    while current_sunday <= last_sunday:
        price_day = current_sunday
        last_week_day = price_day - timedelta(days=7)

        # Compare Avocado Prices to Last Week
        last, this, pct, absolute = avocado_price.compare_prices(prices, price_day, last_week_day)

        avocado_price_list.append({
            'week': 'KW{}/{}'.format(current_sunday.isocalendar()[1], current_sunday.year),
            'price': str(round(this, 2)).replace('.', ',')
        })

        # Standard Deviation = confusing week? Volatile Prices for avocados?
        sentiment, avg_score, std_score, max_score, min_score, peak_sentiment = tweet_sentiment.filter_sentiment_score_by_date(
            tweets, price_day,
            last_week_day)

        print(
            '{} - {} | Last: {:0.2f} | This: {:0.2f} | Pct: {} | Abs: {} | {} | Score {} | Std: {} | Max: {} | Min: {} | Peak: {}'.format(
                last_week_day, price_day, last, this, SharedUtils.prefix(pct), SharedUtils.prefix(absolute), sentiment,
                SharedUtils.prefix(avg_score), SharedUtils.prefix(std_score), SharedUtils.prefix(max_score),
                SharedUtils.prefix(min_score), peak_sentiment))

        # Next week
        current_sunday = current_sunday + timedelta(days=7)

    avocado_price.save_price_week_csv(avocado_price_list)
    exit()
