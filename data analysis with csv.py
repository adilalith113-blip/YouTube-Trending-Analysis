# YouTube Trending Video Analytics - Tableau-Ready Export
# Author: Lalith Basvesh
# Objective: Prepare enhanced CSVs for Tableau dashboards

import pandas as pd
import numpy as np
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (12,6)

# 1. Load Dataset
file_path = r"D:\Data Analytics project\YouTube_US_Cleaned.xlsx"
df = pd.read_excel(file_path)
print("Dataset loaded successfully!")

# 2. Data Cleaning
df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
df['trending_date'] = pd.to_datetime(df['trending_date'], errors='coerce')
df['publish_hour'] = df['publish_time'].dt.hour
df['publish_day'] = df['publish_time'].dt.day_name()

numeric_cols = ['views','likes','dislikes','comment_count']
for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].fillna(0)

# 3. Sentiment Analysis
df['title_sentiment'] = df['title'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
df['sentiment_label'] = df['title_sentiment'].apply(lambda x: 'Positive' if x>0 else 'Negative' if x<0 else 'Neutral')

# 4. Trending Duration
trending_duration = df.groupby('video_id')['trending_date'].nunique().reset_index()
trending_duration.rename(columns={'trending_date':'trending_duration_days'}, inplace=True)

# Merge trending_duration into main df
df = df.merge(trending_duration, on='video_id', how='left')

# 5. Tableau-ready Aggregations

# 5a. Category-level summary
if 'category_id' in df.columns:
    category_summary = df.groupby('category_id').agg({
        'views':'mean',
        'likes':'mean',
        'dislikes':'mean',
        'comment_count':'mean'
    }).reset_index()
    category_summary.rename(columns={
        'views':'avg_views',
        'likes':'avg_likes',
        'dislikes':'avg_dislikes',
        'comment_count':'avg_comments'
    }, inplace=True)
    category_summary_file = r"D:\Data Analytics project\Tableau_Category_Summary.csv"
    category_summary.to_csv(category_summary_file, index=False)
    print(f"Category summary saved: {category_summary_file}")

# 5b. Sentiment summary
sentiment_summary = df.groupby('sentiment_label').agg({
    'video_id':'count',
    'views':'mean'
}).reset_index().rename(columns={'video_id':'num_videos','views':'avg_views'})
sentiment_summary_file = r"D:\Data Analytics project\Tableau_Sentiment_Summary.csv"
sentiment_summary.to_csv(sentiment_summary_file, index=False)
print(f"Sentiment summary saved: {sentiment_summary_file}")

# 5c. Day-of-week summary
day_summary = df.groupby('publish_day').agg({
    'video_id':'count',
    'views':'mean',
    'likes':'mean'
}).reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']).reset_index()
day_summary.rename(columns={'video_id':'num_videos','views':'avg_views','likes':'avg_likes'}, inplace=True)
day_summary_file = r"D:\Data Analytics project\Tableau_Day_Summary.csv"
day_summary.to_csv(day_summary_file, index=False)
print(f"Day-of-week summary saved: {day_summary_file}")

# 5d. Trending duration summary
trending_summary = trending_duration.groupby('trending_duration_days').agg({'video_id':'count'}).reset_index()
trending_summary.rename(columns={'video_id':'num_videos'}, inplace=True)
trending_summary_file = r"D:\Data Analytics project\Tableau_Trending_Duration.csv"
trending_summary.to_csv(trending_summary_file, index=False)
print(f"Trending duration summary saved: {trending_summary_file}")

# 6. Optional: Visualizations
plt.figure()
sns.countplot(data=df, x='sentiment_label', palette='pastel')
plt.title('Sentiment Distribution of Video Titles')
plt.show()

plt.figure()
sns.histplot(trending_duration['trending_duration_days'], bins=20, kde=True)
plt.title('Distribution of Trending Duration (Days)')
plt.show()
