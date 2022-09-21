This is a personal project to build an automated system for exploring options trading opportunities from S&P 500 stocks.

The first goal is, for the top N number of companies in the S&P 500 index measured by by market cap,  to compare the implied volatilies in options prices
using the Black-Scholes formula versus the recent realized volatilies in the underlyings to find any major discrepencies. Based on any major discrepencies,
we can build potential options positions (e.g. straddles, strangles, call spreads, put spreads, directional bets, etc).

Once the framework is built, I'd like to start building in an ARCH model on the underlying stocks to try and forecast volatility. This will help form a 
statistical basis for options positioning.

Then I'd like to start storing the data that this program computes to build distributions for further statistical modeling.

This project is very much a work in progress, and anything is subject to change/ improvement/ adjustment. 
