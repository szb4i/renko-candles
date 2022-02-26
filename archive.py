#NEM ROSSZ SZTEM, belépő kérdés kilépőnél fix SL van TP viszont nem igazi tp, hanem egy bizonyos nyereség után elkezdi sma hoz hasonlítani
            #OPEN LONG
'''
            if not in_long_position and not in_short_position and self.bricks[i][5]==1 and self.bricks[i][3]>self.sma10[i]:
                in_long_position = True
                buy_price = self.bricks[i][3]
                write_log(self.bricks[i][1], 'long_op', ['brick_cl'], [buy_price])
            #CLOSE LONG
            elif in_long_position and self.bricks[i][3]<buy_price*(1-SL):
                sell_price=self.bricks[i][3]
                fee=FEE*TRADE_QUANTITY*LEVERAGE*sell_price*2
                profit*=1+((sell_price-buy_price)*TRADE_QUANTITY*LEVERAGE-fee)/(buy_price*TRADE_QUANTITY*LEVERAGE)
                loss_counter += 1
                write_log(self.bricks[i][1], 'long_ls', ['brick_cl', 'profit'], [sell_price, profit])
                in_long_position = False
            elif in_long_position and self.bricks[i][3]>buy_price*(1+TP) and self.bricks[i][3]<self.sma10[i]:
                sell_price=self.bricks[i][3]
                fee=FEE*TRADE_QUANTITY*LEVERAGE*sell_price*2
                profit*=1+((sell_price-buy_price)*TRADE_QUANTITY*LEVERAGE-fee)/(buy_price*TRADE_QUANTITY*LEVERAGE)
                win_counter += 1
                write_log(self.bricks[i][1], 'long_wn', ['brick_cl', 'profit'], [sell_price, profit])
                in_long_position = False
            #OPEN SHORT
            if not in_long_position and not in_short_position and self.bricks[i][5]==0 and self.bricks[i][3]<self.sma10[i]:
                in_short_position = True
                sell_price = self.bricks[i][3]
                write_log(self.bricks[i][1], 'shrt_op', ['brick_cl'], [sell_price])
            #CLOSE SHORT
            elif in_short_position and self.bricks[i][3]>buy_price*(1+SL):
                buy_price=self.bricks[i][3]
                fee=FEE*TRADE_QUANTITY*LEVERAGE*buy_price*2
                profit*=1+((sell_price-buy_price)*TRADE_QUANTITY*LEVERAGE-fee)/(buy_price*TRADE_QUANTITY*LEVERAGE)
                loss_counter += 1
                write_log(self.bricks[i][1], 'shrt_ls', ['brick_cl', 'profit'], [buy_price, profit])
                in_short_position = False
            elif in_short_position and self.bricks[i][3]<buy_price*(1-TP) and self.bricks[i][3]>self.sma10[i]:
                buy_price=self.bricks[i][3]
                fee=FEE*TRADE_QUANTITY*LEVERAGE*buy_price*2
                profit*=1+((sell_price-buy_price)*TRADE_QUANTITY*LEVERAGE-fee)/(buy_price*TRADE_QUANTITY*LEVERAGE)
                win_counter += 1
                write_log(self.bricks[i][1], 'shrt_wn', ['brick_cl', 'profit'], [buy_price, profit])
                in_short_position = False
        print('profit: ' + str(profit))
        print('win_counter: ' + str(win_counter))
        print('loss_counter: ' + str(loss_counter))
        if win_counter+loss_counter!=0: print("win rate {}".format(win_counter/(win_counter+loss_counter)))
        print('total number of positions : {}'.format(win_counter+loss_counter))
'''