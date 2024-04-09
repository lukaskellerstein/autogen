# filename: plot_stock_price.py
import matplotlib.pyplot as plt
import pandas as pd

# Read the stock price data from a CSV file
df = pd.read_csv('stock_price.csv')

# Convert the 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Filter the data for the specified date range
start_date = '2020-01-01'
end_date = '2020-12-31'
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

# Plot the line chart
plt.plot(filtered_df['Date'], filtered_df['Close'])

# Set the x-axis label and rotate the tick labels
plt.xlabel('Date')
plt.xticks(rotation=45)

# Set the y-axis label
plt.ylabel('Stock Price')

# Set the title of the chart
plt.title('Stock Price of Apple Inc. (AAPL) from 2020-01-01 to 2020-12-31')

# Save the chart to a file
plt.savefig('stock_price.png')

# Show the chart
plt.show()