# Auction Task scoring
This script has two requirements: all raw auction data in one data folder with two files per subject, and a .csv with subject bidding data. It outputs a scored folder with the first auction file labeled 'run1' and the second labeled 'run2.'

There are two scoring scripts. 'auction_scoring.py' includes 5 parametric modulators for the auction task: estimated calories, actual energy density, liking, estimated price, and bid value. 'auction_scoring_no_est_price.py' omits estimated price as a parametric modulator.
