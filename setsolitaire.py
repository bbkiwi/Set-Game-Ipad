# have option find all sets in deal then replenish deal
# have option to deal more even if sets remain (maybe penalty)
import random
import ui
from scene import *
from sound import *
import console
import itertools

A = Action

DEBUG = False
Ninitial = 12 # initial deal
Ndeal = 3 # auto and manual deal size when no sets left
Nc = 3
Ns = 3
Nsh = 3

parm = dict( # of all parameters that can be specified in the gui
    #SOUND_ON = True,
    #RING_SIZE = 100, # 30
    SPEED = 0,
    EASY = True,
    MENU = "rerdogrr"
)


class scalefactor(dict):
    def __missing__(self, key):
        return 1

sfac = scalefactor()

paramnames = ['SPEED', 'EASY', 'MENU']

sfac['SPEED'] = 1


# called from menu gui setsolitaire.pyui
def input_action(sender):
    print('sender.name {} sender.value {}'.format(sender.name, sender.value))
    # get global params that are in the gui and update corresponding text if exists
    # eg if key is 'PAR_XX' the gui input slider etc must have name PAR_XX
    #.          a text box named par_xx_text will be populated with par_xx: nnnnn
    for pn in parm.keys():
        try:
            # get scaled parameter
            #parm[pn] = sender.superview[pn].value * sfac[pn]
            parm[pn] = sender.superview[pn].value
            # update text
            sender.superview[pn.lower()+'_text'].text = '{}: {:.2f}'.format(pn.lower(),parm[pn])
        except:
            try:
                parm[pn] = sender.superview[pn].segments[sender.superview[pn].selected_index]
                # update text
                sender.superview[pn.lower()+'_text'].text = '{}: {:s}'.format(pn.lower(),parm[pn])
            except:
                pass
    #print(sender.superview['MENU'].segments[sender.superview['MENU'].selected_index])


console.clear()

def makeDeck(colorSlice = (0,3,1), numberSlice = (0,3,1), shapeSlice=(0,3,1),shadeSlice=(0,3,1)):
    # card has 4 properties each with 3 states
    # eg color (r,g,b), number (1,2,3), shape (circle, square, sqiggle), shading (open, striped, solid) and
    deck = []
    for color in itertools.islice(['red', 'green', 'blue'], *colorSlice):
        for number in itertools.islice(range(1, 4), *numberSlice):
            for shape in itertools.islice(['ovals', 'diamonds', 'squiggles'], *shapeSlice):
                for shade in itertools.islice(['open', 'solid', 'stripes'], *shadeSlice):
                    deck.append([color, number, shape, shade])
    return deck


def checkDeck(deck):
    colorCnt = dict(zip(['red', 'green', 'blue'], [0, 0, 0]))
    numberCnt = dict(zip([1, 2, 3], [0, 0, 0]))
    shapeCnt = dict(zip(['ovals', 'diamonds', 'squiggles'], [0, 0, 0]))
    shadeCnt = dict(zip(['open', 'solid', 'stripes'], [0, 0, 0]))
    for card in deck:
        colorCnt[card[0]] += 1
        numberCnt[card[1]] += 1
        shapeCnt[card[2]] += 1
        shadeCnt[card[3]] += 1
    return "N= {}, Color R:{} G:{} B:{} Number 1:{} 2:{} 3:{} Shape Ov:{} Di:{} Sq:{} Shade Op:{} Fi:{} St:{}".format(len(deck),
        *colorCnt.values(), *numberCnt.values(), *shapeCnt.values(),
        *shadeCnt.values())


def removeCardsInSet(set, deck):
    #print(" set", set)
    #print(" deck", deck)
    for card in set:
        #print(" card", card)
        deck.remove(card)


def dealCard(deck):
    # chooses card and removes from deck
    card = random.choice(deck)
    deck.remove(card)
    return card


def makeDeal(deck):
    #deal = random.sample(deck, N)
    deal = []
    for i in range(Ninitial):
        deal.append(dealCard(deck))
    return deal


def printDeck(deck):
    for i, card in enumerate(deck):
        print(i, card)
    print(len(deck))


def findSets(deal):
    N = len(deal)
    #cnt=0
    setsFound = []
    for i in range(N):
        for j in range(i + 1, N):
            for k in range(j + 1, N):
                check = []
                for pr in range(4):
                    check.append(len({deal[i][pr], deal[j][pr], deal[k][pr]}))
                    if check[pr] == 2:
                        break
                else:
                    setsFound.append([deal[i], deal[j], deal[k]])
                    #print(i, j, k,check,deal[i],deal[j],deal[k])
                    #cnt=cnt+1
                #print(N, cnt)
    return setsFound


def goodness(set, deck):
    deckCopy = deck.copy()
    #print(" g***1 ", deckCopy)
    removeCardsInSet(set, deckCopy)
    #print(" g***2 ", deckCopy)
    return len(findSets(deckCopy))


def findBestSet(deal, deck):
    # best when removed from deal will have max sets still left
    #    if tie will choose onewith max sets left in deck
    sets = findSets(deal)
    #print(sets)
    if len(sets) == 0:
        return []
    else:
        sbest = sets[0]
        sbestgoodness = [goodness(sbest, deal), goodness(sbest, deck + deal)]
        #print(" first set {} goodness {}".format(sbest, sbestgoodness))
        if len(sets) == 1:
            #print(" is only set")
            return sbest
        #return sbest # just use first
        for set in sets[1:]:
            setgoodness = [goodness(set, deal), goodness(set, deck + deal)]
            #print(" {} goodness {}".format(set, setgoodness))
            if setgoodness > sbestgoodness:
                # go for worst choice
                #setgoodness = [goodness(set, deck + deal), goodness(set, deal)]
                #if setgoodness < sbestgoodness:
                sbest = set
                sbestgoodness = setgoodness
        #print(" best {} goodness {}".format(sbest, sbestgoodness))
        return sbest


width = 120
height = 180

shadingPath = ui.Path.rect(10, 10, width - 20, height - 20)
for x in range(3, 38):
    shadingPath.move_to(3 * x, 10)
    shadingPath.line_to(3 * x, height - 10)

outlinePath = ui.Path.rounded_rect(0, 0, width, height, 10)
ovalPath1 = ui.Path.oval(30, 75, 60, 30)
ovalPath1.append_path(outlinePath)

ovalPath2 = ui.Path.oval(30, 45, 60, 30)
ovalPath2.append_path(ui.Path.oval(30, 105, 60, 30))
ovalPath2.append_path(outlinePath)

ovalPath3 = ui.Path.oval(30, 75, 60, 30)
ovalPath3.append_path(ui.Path.oval(30, 30, 60, 30))
ovalPath3.append_path(ui.Path.oval(30, 120, 60, 30))
ovalPath3.append_path(outlinePath)

ovalPath1.line_width = 4.0
ovalPath1.eo_fill_rule = True
ovalPath2.line_width = 4.0
ovalPath2.eo_fill_rule = True
ovalPath3.line_width = 4.0
ovalPath3.eo_fill_rule = True

ovalPaths = [ovalPath1, ovalPath2, ovalPath3]

#rectPath = ui.Path.rect(30, 75, 60, 30)
#rectPath.append_path(outlinePath)
#rectPath.line_width = 4.0
#rectPath.eo_fill_rule = True


def makeSquigglePath(x, y, dx, dy):
    squigglePath = ui.Path()
    squigglePath.move_to(x, y)
    squigglePath.add_curve(x + dx, y, x + 20, y + 20, x + dx - 20, y - 20)
    squigglePath.line_to(x + dx, y + dy)
    squigglePath.add_curve(x, y + dy, x + dx - 20, y + dy - 20, x + 20,
                           y + dy + 20)
    squigglePath.line_to(x, y)
    squigglePath.close()
    return squigglePath


squigglePath1 = makeSquigglePath(30, 75, 60, 30)
squigglePath1.append_path(outlinePath)
squigglePath1.line_width = 4.0
squigglePath1.eo_fill_rule = True

squigglePath2 = makeSquigglePath(30, 45, 60, 30)
squigglePath2.append_path(makeSquigglePath(30, 105, 60, 30))
squigglePath2.append_path(outlinePath)
squigglePath2.line_width = 4.0
squigglePath2.eo_fill_rule = True

squigglePath3 = makeSquigglePath(30, 30, 60, 30)
squigglePath3.append_path(makeSquigglePath(30, 75, 60, 30))
squigglePath3.append_path(makeSquigglePath(30, 120, 60, 30))
squigglePath3.append_path(outlinePath)
squigglePath3.line_width = 4.0
squigglePath3.eo_fill_rule = True

squigglePaths = [squigglePath1, squigglePath2, squigglePath3]


def makeDiamondPath(x, y):
    diamondPath = ui.Path()
    diamondPath.move_to(x - 35, y)
    diamondPath.line_to(x, y + 15)
    diamondPath.line_to(x + 35, y)
    diamondPath.line_to(x, y - 15)
    diamondPath.line_to(x - 35, y)
    diamondPath.close()
    return diamondPath


# Draw path from centre point to touched point
diamondPath1 = makeDiamondPath(60, 90)

diamondPath2 = makeDiamondPath(60, 120)
diamondPath2.append_path(makeDiamondPath(60, 60))

diamondPath3 = makeDiamondPath(60, 90)
diamondPath3.append_path(makeDiamondPath(60, 135))
diamondPath3.append_path(makeDiamondPath(60, 45))

diamondPath1.append_path(outlinePath)
diamondPath1.line_width = 4.0
diamondPath1.eo_fill_rule = True

diamondPath2.append_path(outlinePath)
diamondPath2.line_width = 4.0
diamondPath2.eo_fill_rule = True

diamondPath3.append_path(outlinePath)
diamondPath3.line_width = 4.0
diamondPath3.eo_fill_rule = True

diamondPaths = [diamondPath1, diamondPath2, diamondPath3]

cardShapes = {
    'diamonds': diamondPaths,
    'ovals': ovalPaths,
    'squiggles': squigglePaths
}

#print(diamondPaths, ovalPaths, squigglePaths)

#TODO how to make non global?
posPositions = [(x, y) for y in range(3)
                for x in range(4)] + [(x, y)
                                      for x in range(4, 8) for y in range(3)]
freePositions = [True] * len(posPositions)


class Card(Node):
    def __init__(self, x, y, color, number, shape, shade, *args, **kwargs):
        # is next needed, doesnt seem to make difference
        Node.__init__(self, *args, **kwargs)



        if x==None:
            for posInd, fp in enumerate(freePositions):
                if fp:
                    freePositions[posInd] = False
                    break
            x, y = posPositions[posInd]
            x *= width + 5
            x += width / 2
            y *= height + 5
            y += height / 2
            y = 650 - y
            self.posInd = posInd

        self.position = (x, y)

        self.x = x
        self.y = y

        self.color = color
        self.number = number
        self.shape = shape
        self.shade = shade
        #print(x,y,color,number,shape,shade)
        shadings = {
            'solid': color,
            'stripes': (0, 0, 0, 0),
            'open': (1, 1, 1, 1)
        }
        shading = ShapeNode(path=shadingPath, *args, **kwargs)
        shading.stroke_color = color
        outline = ShapeNode(path=outlinePath, *args, **kwargs)
        #outline.z_position = 0

        outline.fill_color = shadings[shade]

        #print(outline.fill_color)
        #outline.blend_mode = BLEND_NORMAL
        outline.position = [0, 0]

        #print(cardShapes[shape][number - 1])

        cardShape = ShapeNode(
            path=cardShapes[shape][number - 1], *args, **kwargs)
        cardShape.stroke_color = color
        #cardShape.remove_from_parent()
        #outline.remove_from_parent()

        self.add_child(shading)
        self.add_child(outline)
        self.add_child(cardShape)

    #    update(self), run_action(self, A, key), remove_action(self, key) all builtin methods
    #    no need to over ride


class MyScene(Scene):
    def setup(self):
        self.background_color = (0, 0, .5)
        self.v = None
        self.INPUT_ACTION_TAKEN = False
        self.buttonParmPopup = ShapeNode(
            ui.Path.rect(0, 0, 50, 50),
            position=(625, 25),
            fill_color='green',
            parent=self)
        self.add_child(self.buttonParmPopup)

        self.buttonAllAuto = ShapeNode(
            ui.Path.rect(0, 0, 50, 50),
            position=(325, 25),
            fill_color='white',
            parent=self)
        self.add_child(self.buttonAllAuto)

        self.buttonAuto = ShapeNode(
            ui.Path.rect(0, 0, 50, 50),
            position=(225, 25),
            fill_color='orange',
            parent=self)
        self.add_child(self.buttonAuto)

        self.buttonPile = ShapeNode(
            ui.Path.rect(0, 0, 50, 50),
            position=(125, 25),
            fill_color='purple',
            parent=self)
        self.add_child(self.buttonPile)

        self.buttonSet = ShapeNode(
            ui.Path.rect(0, 0, 50, 50),
            position=(25, 25),
            fill_color='red',
            parent=self)
        self.add_child(self.buttonSet)

        self.message = LabelNode('', position=(800, 225), font=('Helvetica', 50), parent=self)

        self.scoreBoard = Node(position=(10, 750), parent=self)
        self.score = LabelNode('', parent=self.scoreBoard)
        self.score.anchor_point = (0, 5)

        self.deckInfo = Node(position=(10, 725), parent=self)
        self.deckLabel = LabelNode('', parent=self.deckInfo)
        self.deckLabel.anchor_point = (0, 5)

        self.dealInfo = Node(position=(10, 700), parent=self)
        self.dealLabel = LabelNode('', color='yellow', parent=self.dealInfo)
        self.dealLabel.anchor_point = (0, 5)

#        self.setsFound = Node(position=(800, 650), parent=self)
#        self.setsFound.x_scale = .2
#        self.setsFound.y_scale = .2

        ws = ui.get_window_size()
        self.setsFound = Node(position=(0, ws[1]), parent=self)
        #self.setsFound.x_scale = .2
        #self.setsFound.y_scale = .2

        self.cardsOnTable = []
        self.numChildrenSetup = len(self.children)

        self.start()

    def start(self):
        # clean up all added card nodes and free their positions
        for node in self.children[self.numChildrenSetup:]:
            freePositions[node.posInd] = True
            node.remove_from_parent()

        self.numCorrectSets = 0
        self.numBadSets = 0
        self.numCorrectDeals = Ninitial
        self.numBadDeals = 0
        self.numAuto = 0

        for c in self.setsFound.children:
            c.remove_from_parent()

        ws = ui.get_window_size()
        self.xDisp = self.xDispCol =  ws[0] - 225
        self.yDisp = -150

        self.startNextTouch = False
        self.cardsOnTable = []
        self.setAutoFound = []
        self.cardsLeft = []


        if parm['EASY']:
            self.deck = makeDeck(shadeSlice=(2,3,1))
        else:
            self.deck = makeDeck()

        self.deal = makeDeal(self.deck)
        #print(self.deal)
        self.deckLabel.text = checkDeck(self.deck)
        self.dealLabel.text = checkDeck(self.deal)

        # draw card nodes of deal in grid
        for cardData in self.deal:
            ctmp = Card(None, None, *cardData)
            #print(ctmp.position)
            self.add_child(ctmp)
            self.cardsOnTable.append(ctmp)

        # FIX only for the initial deal!
        for i, subnode in enumerate(self.children):
            subnode.z_position = -i

        self.cardTouched = None
        self.buttonTouchId = None
        self.userCalledSet = False
        self.userCardsSelected = []
        self.message.text = ''
        self.score.text = "{} Correct Set Calls, {} Incorrect, {} Good Deals, {} Premature, {} Auto".format(
            self.numCorrectSets, self.numBadSets, self.numCorrectDeals,
            self.numBadDeals, self.numAuto)

    def dispFoundAction(self, node, progress):
        return
        if progress > 0.9:
            #print(bestSet)
            node.x_scale = 1


    def autoPlay(self):
        bestSetData = findBestSet(self.deal, self.deck)
        self.setAutoFound = []
        self.cardsLeft = []
        if len(bestSetData) == 3:  # a set so remove from table and continue
            print(bestSetData)
            for node in self.children[self.numChildrenSetup:]:
                if [node.color, node.number, node.shape,
                        node.shade] in bestSetData:
                    #node.x_scale = 1.2
                    #node.y_scale = 1.2
                    #node.z_position = 10
                    self.setAutoFound.append(node)
                else:
                    #pass
                    #node.alpha = .6
                    node.remove_all_actions()
                    node.x_scale = .5
                    node.y_scale = .5
                    self.cardsLeft.append(node)

            self.dispFound([bestSetData])
            removeCardsInSet(bestSetData, self.deal)
        else:  # no more sets on table, add new cards from deck
            if len(self.deck) != 0:
                #NdealNow = Ndeal):
                NdealNow = min(len(self.deck), max(Ndeal, Ninitial - len(self.deal)))
                for i in range(NdealNow):
                    newCardData = dealCard(self.deck)
                    self.deal.append(newCardData)
                    ctmp = Card(None, None, *newCardData)
                    self.add_child(ctmp)
                    self.cardsOnTable.append(ctmp)

    def dispFound(self, allSets):
        for setData in allSets:
            #print(set)
            for cardData in setData:
                ctmp = Card(self.xDisp, self.yDisp, *cardData)
                ctmp.x_scale = .2
                ctmp.y_scale = .2
                self.setsFound.add_child(ctmp)
                self.xDisp += .2*width
            self.yDisp -= 0.2*height+2
            if self.yDisp <= -3*(height+2) - 150:
                self.xDispCol += 5+3*0.2*width
                self.yDisp = -150
            self.xDisp = self.xDispCol

    def update(self):
        pass

    def touch_began(self, touch):

        #TODO BUG if touch while cards are moving to display they stop and never get removed

        # remove actions from all cards
        #for node in self.children[self.numChildrenSetup:]:
            #node.remove_all_actions()

        #print(self.t)




        if self.startNextTouch:
            self.start()
            return

        if len(self.setAutoFound) > 0: # in autoplay
            for node in self.cardsOnTable:
                # restore cards made smaller during auto play
                #node.alpha = 1
                #node.x_scale = 1
                #node.y_scale = 1
                node.remove_all_actions()
                node.run_action(A.scale_to(1, 3))
                pass


        for node in self.setAutoFound:
            print(node.position, self.setsFound.point_from_scene(node.position))
            self.cardsOnTable.remove(node)
            freePositions[node.posInd] = True
            #node.remove_from_parent()
            node.remove_all_actions()
            node.run_action(A.sequence(
                                    A.group(
                                    A.scale_to(0.2, 3),
                                    A.move_to(*self.setsFound.point_to_scene((self.xDisp, self.yDisp)), 3,                 TIMING_EASE_IN),
                                    A.call(self.dispFoundAction,3)),
                                    A.remove() # seems to remove  from parent
                                    ))

        self.setAutoFound = []

        # this should never be true so raise exception if occurrs
        if [[c.color, c.number, c.shape, c.shade] for c in self.cardsOnTable] != self.deal:
            print('*', len(self.deal), len(self.cardsOnTable))
            print(self.deal)
            print([[c.color, c.number, c.shape, c.shade] for c in self.cardsOnTable])
            raise Exception



        # touched found set button
        if touch.location in self.buttonSet.frame:
            self.buttonSet.fill_color = 'yellow'
            self.userCalledSet = True
            return

        # touched change settings button
        if touch.location in self.buttonParmPopup.frame:
            if self.v is None:
                self.v = ui.load_view('setsolitaire.pyui') # needed name here explicitly. Why?
                # repopulate param values in gui
                for pn in paramnames:
                    #self.v[pn].value = parm[pn] / sfac[pn]
                    self.v[pn].value = parm[pn]
                    print(pn, parm[pn])
                self.v.background_color = '#5564ff'
                self.v.tint_color = '#12ff26'

                # popover will close when touch outside it
                input_action(self.v['SPEED']) # force update of parameters
                self.v.present('popover', popover_location=(touch.location[0], 768 - touch.location[1]), hide_title_bar=True)
                #input_action(self.v['SPEED']) # force update of parameters
                self.v.wait_modal()
#                self.swadgeSelected.topspeed = parm['SPEED']
#                self.swadgeSelected.v = Vector2(0,self.swadgeSelected.topspeed)
                self.INPUT_ACTION_TAKEN = True
                self.v = None

        if touch.location in self.buttonPile.frame:
            # if sets still exist penalty and bad noise
            # otherwise draw card
            bestSet = findBestSet(self.deal, self.deck)
            if len(bestSet) == 3:
                play_effect('game:Spaceship')
                self.numBadDeals += 1
            else:
                if len(self.deck) == 0:
                    # deck empty end game
                    self.message.text = 'Game Over \nafter request new card'
                    self.startNextTouch = True
                    return
                #NdealNow = Ndeal):
                NdealNow = min(len(self.deck), max(Ndeal, Ninitial - len(self.deal)))
                for i in range(NdealNow):
                    newCard = dealCard(self.deck)
                    self.deal.append(newCard)
                    ctmp = Card(None, None, *newCard)
                    self.add_child(ctmp)
                    self.cardsOnTable.append(ctmp)
                    self.deckLabel.text = checkDeck(self.deck)
                    self.dealLabel.text = checkDeck(self.deal)
                    self.numCorrectDeals += 1
            self.score.text = "{} Correct Set Calls, {} Incorrect, {} Good Deals, {} Premature, {} Auto".format(
                self.numCorrectSets, self.numBadSets, self.numCorrectDeals,
                self.numBadDeals, self.numAuto)

            #self.buttonPile.fill_color = 'yellow'
            #self.userCalledSet = True
            return

        if touch.location in self.buttonAllAuto.bbox:
            self.numAuto += 1
            self.dispFound(findSets(self.deal))
            self.dealLabel.text = checkDeck(self.deal)
            self.deckLabel.text = checkDeck(self.deck)
            self.message.text = 'Game Over \nAuto Find All'
            self.startNextTouch = True

        if touch.location in self.buttonAuto.bbox:
            self.numAuto += 1
            self.autoPlay()
            self.dealLabel.text = checkDeck(self.deal)
            self.deckLabel.text = checkDeck(self.deck)
            if (len(self.deck) == 0) & (len(findSets(self.deal)) == 0):
            #if len(self.deck) == 0:
                # deck empty end game but cards left in deal
                self.message.text = 'Game Over\n Auto Play'
                self.startNextTouch = True

        for node in self.children[self.numChildrenSetup:]:
            #print(node.z_position)
            #node.remove_all_actions()
            if touch.location in node.bbox:
                self.cardTouched = node
                self.cardTouched.x_scale = 1.4
                if self.userCalledSet:
                    if ((len(self.userCardsSelected) < 3) and
                        (self.cardTouched not in self.userCardsSelected)):
                        self.userCardsSelected.append(self.cardTouched)
                        #print(self.userCardsSelected)
                    if len(self.userCardsSelected) == 3:
                        if len(
                                findSets([[
                                    c.color, c.number, c.shape, c.shade
                                ] for c in self.userCardsSelected])) == 0:
                            # not a set, make noise subtract penalty etc
                            play_effect('game:Error')
                            self.buttonSet.fill_color = 'red'
                            self.userCalledSet = False
                            for c in self.userCardsSelected:
                                c.remove_all_actions()
                                c.run_action(A.sequence(
                                    A.scale_x_to(1.4),
                                    #A.move_to(letter_pos.x, letter_pos.y, 1.2, TIMING_ELASTIC_OUT),
                                    A.wait(1),
                                    A.scale_x_to(1),
                                    #A.remove()
                                    ))
                                #c.x_scale = 1
                            self.userCardsSelected = []
                            self.numBadSets += 1
                        elif True:
                            # found set, remove cards from deck
                            # make nice sound
                            play_effect('digital:PowerUp1')
                            self.numCorrectSets += 1
                            self.buttonSet.fill_color = 'green'
                            self.userCalledSet = False

                            self.dispFound([[[c.color, c.number, c.shape, c.shade]
                                 for c in self.userCardsSelected]])
                            removeCardsInSet(
                                [[c.color, c.number, c.shape, c.shade]
                                 for c in self.userCardsSelected], self.deal)
                            self.dealLabel.text = checkDeck(self.deal)
                            for c in self.userCardsSelected:
                                freePositions[c.posInd] = True
                                #c.remove_from_parent()
                                self.cardsOnTable.remove(c)
                                c.remove_all_actions()
                                c.run_action(A.sequence(
                                    A.group(
                                    A.scale_to(0.2, 3),
                                    A.move_to(*self.setsFound.point_to_scene((self.xDisp, self.yDisp)), 3,                 TIMING_EASE_IN)),
                                    A.remove() # seems to remove c from parent
                                    ))
                            self.userCardsSelected = []
                        else:
                            # found set but dont remove
                            # make nice sound
                            play_effect('digital:PowerUp1')
                            self.numCorrectSets += 1
                            self.buttonSet.fill_color = 'green'
                            self.userCalledSet = False

                            self.dispFound([[[c.color, c.number, c.shape, c.shade]
                                 for c in self.userCardsSelected]])

                            self.dealLabel.text = checkDeck(self.deal)
                            for c in self.userCardsSelected:
                                #freePositions[c.posInd] = True
                                #c.remove_from_parent()
                                #self.cardsOnTable.remove(c)
                                c.remove_all_actions()
                                c.run_action(A.sequence(
                                    A.group(
                                    A.scale_to(0.2, 3),
                                    A.move_to(*self.setsFound.point_to_scene((self.xDisp, self.yDisp)), 3,                 TIMING_EASE_IN)),
                                    ))
                            self.userCardsSelected = []
                            #print(len(findSets(self.deal)))
                            #if (len(self.deck) == 0) & (len(findSets(self.deal)) == 0):
                                ## deck empty end game but cards left in deal
                                #self.message.text = 'Game Over\n after found last set'
                                #self.startNextTouch = True
                                ##return
                break
        self.score.text = "{} Correct Set Calls, {} Incorrect, {} Good Deals, {} Premature {} Auto".format(
            self.numCorrectSets, self.numBadSets, self.numCorrectDeals,
            self.numBadDeals, self.numAuto)

    def touch_moved(self, touch):
        # immediate move to touch location
        if self.cardTouched != None:
            self.cardTouched.position = (touch.location[0], touch.location[1])

    def touch_ended(self, touch):
        #        self.cardTouched.run_action(
        #            Action.move_to(touch.location[0], touch.location[1], 1,
        #                               TIMING_SINODIAL), 'move_action_key')

        #self.cardTouched.remove_action('move_action_key')
        print(self.userCalledSet)
        if (self.cardTouched != None) & (not self.userCalledSet):
            #pass
            self.cardTouched.x_scale = 1
        self.cardTouched = None


if __name__ == '__main__':
    run(MyScene(), LANDSCAPE, show_fps=True)

