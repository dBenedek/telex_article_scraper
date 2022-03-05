# Telex website article scraper

Python script for Telex website article scraping and analysis.

## Description

In its current form, the `telex_scraper.py` script scrapes all the articles on the [Telex main page](https://telex.hu/), and stores the absolute frequency of all the words across the 65 articles. The script also creates a word cloud with the most frequent words. 

Example:

![wordcloud_2022_03_05_15_57_41](https://user-images.githubusercontent.com/47271010/156892022-bd9ff8ae-bfb8-4797-9d6a-45c9b136b0dc.png)

***

The script `plot_wordfreq.py` creates an interactive lineplot (using [Plotly](https://plotly.com/)) to visualize the absolute word requencies at the different time points, when the `telex_scraper.py` script was run. The top 10 most frequent words at the point 0 are plotted.

Example:

![newplot (1)](https://user-images.githubusercontent.com/47271010/156891973-76a1b14f-da2a-411e-9d39-44121544e9f1.png)
