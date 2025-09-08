import matplotlib
matplotlib.use('WebAgg')
import matplotlib.pyplot as plt

# Data
years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 
         2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

col1 = [185, 249, 268, 297, 308, 361, 455, 554, 562, 613, 825, 904, 1140, 1300, 1590, 1860, 
        2300, 2970, 4310, 6390, 8130, 11500, 14300, 15900, 17400]

col2 = [63, 71, 89, 71, 98, 149, 207, 214, 196, 167, 223, 217, 229, 245, 288, 308, 
        530, 922, 1660, 2780, 4170, 6440, 8630, 11400, 14600]

# Create the plot
plt.figure(figsize=(12, 8))
plt.plot(years, col1, marker='o', linewidth=2, markersize=6, label='seismology AND \"machine learning\"')
plt.plot(years, col2, marker='s', linewidth=2, markersize=6, label='seismology AND \"deep learning\"')

# Customize the plot
plt.xlabel('Year', fontsize=20)
plt.ylabel('Scientific works', fontsize=20)
plt.legend(fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=14)
plt.grid(True, alpha=0.25)

# Format the axes
plt.xticks(years[::2], rotation=45)  # Show every other year to avoid crowding
plt.tight_layout()

plt.savefig('papers_per_year.png')

# Display the plot
plt.show()
