from setsolitairalt import *
import setsolitairalt
import numpy
import matplotlib.pyplot as plt

#setsolitaire.N = 81  # initial deal

#setsolitaire.Ndeal = 1 # auto and manual deal size when no sets left

# override and use numbers for the states, so can map into lattice cube
# so a card is a point in [1,2,3] x [1,2,3] x [1,2,3] x [1,2,3]
# the parity of a card is the sum of its coordinates

def makeDeck(colorSlice=(0, 3, 1),
             numberSlice=(0, 3, 1),
             shapeSlice=(0, 3, 1),
             shadeSlice=(0, 3, 1)):
    # card has 4 properties each with 3 states
    # here just use number
    # eg color (r,g,b), number (1,2,3), shape (oval, diamond, squiggles), shading (open, solid, stripe)
    deck = []
    for color in itertools.islice(range(1, 4), *colorSlice):
        for number in itertools.islice(range(1, 4), *numberSlice):
            for shape in itertools.islice(range(1, 4), *shapeSlice):
                for shade in itertools.islice(range(1, 4), *shadeSlice):
                    deck.append([color, number, shape, shade])
    return deck


def main():

    # plays nrounds rounds of find all sets in deal
    # look at histogram of total sets found
    #
    nrounds = 61
    histcnt = {}
    deck = makeDeck()
    deal20 = makeCap20Deal(deck, coorOnly=True)
    for i in range(nrounds):
        paritycnt = {}
        dimcnt = {}
        pdcnt ={}
        #deck = makeDeck()
        #deal = makeDeal(deck, N=81)
        # make backend initial deal from cap20 plus one more card from rest of deck
        deal = deal20 + [deck[i]]
        #deck = makeDeck(shadeSlice=(1, 2, 1))  # solid only
        #deal = makeDeal(deck, N=27)
        #deck = makeDeck(shadeSlice=(1, 2, 1),shapeSlice=(1, 2, 1),  )  # solid and diamond
        #print(deck)
        #deal = makeDeal(deck, N=9)
        sets = findSets(deal)
        for s in sets:
            # sets may have 0,1,2 or 3 odd parity cards (parity is sum of coordinates )
            keyp=sum(map(lambda x:sum(x)%2, map(numpy.array, s)))
            #print(s, key)
            if keyp not in paritycnt:
                paritycnt.update([(keyp, 0)])
            paritycnt[keyp] += 1

            keyd=dimSet(s)
            #print(s, key)
            if keyd not in dimcnt:
                dimcnt.update([(keyd, 0)])
            dimcnt[keyd] += 1

            key = (keyp, keyd)
            if key not in pdcnt:
                pdcnt.update([(key, 0)])
            pdcnt[key] += 1


#        print("Hist Num of odd parity cards in  Set {}".format(sorted(paritycnt.items())))
#        plt.bar(list(paritycnt.keys()), list(paritycnt.values()),color='red')
#        plt.title('num odd parity')
#        plt.show()
#
#        plt.clf()
#        print("Hist Dim Sets {}".format(sorted(dimcnt.items())))
#        plt.bar(list(dimcnt.keys()), list(dimcnt.values()))
#        plt.title('dim set')
#        plt.show()
#
#        print("Hist pd {}".format(sorted(pdcnt.items())))
#
#
        key = len(sets)
        if key==10:
            print(deal)
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
        #deck = makeDeck(shadeSlice=(1, 2, 1))  # solid only
        deal = makeCap20Deal(deck, coorOnly=True)
        deal = makeDeal(deck, N=12)
        setsFound = []
        cnt = 0
        while True:
            bestSet = findBestSet(deal, deck)
            #print(deal)
            if len(bestSet) == 3:  # a set so remove from table and continue
                setsFound.append(bestSet)
                #printDeck(deal)
                #print(len(deal), len(deck), bestSet)
                cnt = cnt + 1
                removeCardsInSet(bestSet, deal)
            else:  # no more sets on table, add 3 new cards from deck
                if len(deck) == 0:
                    if cnt < 7:
                        print(setsFound)
                    break
                deal.append(dealCard(deck))
                #deal.append(dealCard(deck))
                #deal.append(dealCard(deck))
        histcnt[cnt] += 1

    print("Hist Cnt {}".format(histcnt))
    plt.clf()
    plt.bar(range(28), histcnt)
    plt.title('total found')
    plt.show()

if __name__ == '__main__':
    main()
