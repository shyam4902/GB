# GB

This repository contains R Markdown files for analyzing fantasy football contests in the app GameBlazers. The main components of this project include:

## 1. Player Projections (`Projections/`)
- Takes an exported CSV file from the game.
- Cleans and processes the data.
- Outputs a new CSV with weekly projections for each player on the roster.
- Some manual adjustments were made for bye weeks and other updates.
- We are using week 17 data as a showcase since the schedule had games in 5 out of 6 straight days.
- Sadly there are no bye teams, however, it is just a matter of editing teams around just like you would while making the schedule.
- I think the simple fix for next season is to input the entire schedule when released and create a slider widget to select the week for the website. 


## 2. Contest Analyzer (`Contest_Analyzer/`)
- Analyzes historical contest results.
- Estimates how many points were needed to reach different payout tiers.
- Currently includes past data and a small sample set but was still extremely accurate in making predictions.
