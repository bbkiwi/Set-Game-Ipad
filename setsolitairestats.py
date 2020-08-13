from setsolitaire import *
import setsolitaire

setsolitaire.N = 12 # initial deal
#setsolitaire.Ndeal = 1 # auto and manual deal size when no sets left

def main():
    
    # plays nrounds rounds of find all sets in deal
    # look at histogram of total sets found 
    # 
    nrounds = 1000
    histcnt = {}
    for i in range(nrounds):
        deck = makeDeck()
        deal = makeDeal(deck)
        sets = findSets(deal)
        key = len(sets)
        if key not in histcnt:
            histcnt.update([(key, 0)])
        histcnt[key] += 1
            
    print("Hist Num Sets {}".format(sorted(histcnt.items())))
    
    return
    # plays 100 rounds of find and deal more only if none
    # look at histogram of total sets removed ( max 27)
    # Hist Cnt [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 39, 48, 0, 1]
    histcnt = [0] * 28
    for i in range(100):
        deck = makeDeck()
        deal = makeDeal(deck)
        cnt = 0
        while True:
            bestSet = findBestSet(deal, deck)
            #print(deal)
            if len(bestSet) == 3:  # a set so remove from table and continue
                #printDeck(deal)
                #print(len(deal), len(deck), bestSet)
                cnt = cnt + 1
                removeCardsInSet(bestSet, deal)
            else:  # no more sets on table, add new card from deck
                if len(deck) == 0:
                    break
                deal.append(dealCard(deck))
        histcnt[cnt] += 1
            
    print("Hist Cnt {}".format(histcnt))
        
if __name__ == '__main__':
    main()
