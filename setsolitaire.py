# TODO have option to deal more even if sets remain (maybe penalty)
import random
import ui
from scene import *
from sound import *
import console
import itertools
import json
import time
import photos

console.clear()

# Get images drawn by Iris in photo album 'SetImages'
for album in photos.get_albums():
    if album.title == 'SetImages':
        try:
            scaleFaces = .05
            imgBadChoice = album.assets[0].get_ui_image()
            imgAlreadyChosen = album.assets[1].get_ui_image()
            imgBadDealRequest = album.assets[2].get_ui_image()
            imgCorrectSet = album.assets[3].get_ui_image()
            imgOops = album.assets[1].get_ui_image()
            #            imgBadChoice = album.assets[0].get_ui_image(size=(120, 120), crop=False)
            #            imgAlreadyChosen = album.assets[1].get_ui_image(size=(120, 120), crop=False)
            #            imgBadDealRequest = album.assets[2].get_ui_image(size=(120, 120), crop=False)
            #            imgCorrectSet = album.assets[3].get_ui_image(size=(120, 120), crop=True)

            break
        except:
            pass
else:  # if no album 'SetImages' or not contains all images default to these
    scaleFaces = 1
    imgBadChoice = 'emj:Stuck-Out_Tongue_1'
    imgAlreadyChosen = 'emj:Astonished'
    imgBadDealRequest = 'emj:Flushed'
    imgCorrectSet = 'emj:Smiling_2'
    imgOops = 'emj:Relieved'

DEBUG_LEVEL = 0  # max level to show
print('DEBUG LEVEL ', DEBUG_LEVEL)


def dbPrint(*args, level=1):
    if level <= DEBUG_LEVEL:
        print(level * ' ', 'LINE:', sys._getframe().f_back.f_lineno, *args)


# Default parm if setsolitaireParm.txt not exist
parm = dict(  # of all parameters that can be specified in the gui
    SOUND_ON=True,
    FACES=True,
    DELAY=31,
    DEAL=3,
    STARTDEAL=12,
    EASY=True,
    FILL=True,
    REMOVE=False,
    PROPERTY='Random',
    PROPERTY_idx=0,
    ATTRIBUTE='Random',
    ATTRIBUTE_idx=0)

paramnames = [
    'SOUND_ON', 'FACES', 'DELAY', 'DEAL', 'STARTDEAL', 'EASY', 'FILL',
    'PROPERTY', 'ATTRIBUTE', 'REMOVE'
]

# Get parm from json file if exists
try:
    with open('setsolitaireParm.txt', 'r') as f:
        parm = json.load(f)
except:
    pass


class parmScale(dict):
    def __missing__(self, key):
        return 1


class parmShift(dict):
    def __missing__(self, key):
        return 0


sfac = parmScale()
sfac['DELAY'] = 119
sfac['DEAL'] = 6
sfac['STARTDEAL'] = 15

pshift = parmShift()
pshift['DELAY'] = 2
pshift['DEAL'] = 1
pshift['STARTDEAL'] = 3


# called from menu gui setsolitaire.pyui
def input_action(sender):
    try:
        dbPrint(
            'sender.name {} sender.value {}'.format(sender.name, sender.value))
    except:
        pass
    # get global params that are in the gui and update corresponding text if exists
    # eg if key is 'PAR_XX' the gui input slider etc must have name PAR_XX
    # a text box named par_xx_text will be populated with par_xx: nnnnn
    for pn in parm.keys():
        try:
            # get parameter scaled, ceil and shifted
            parm[pn] = int(sender.superview[pn].value * sfac[pn]) + pshift[pn]
            # update text
            sender.superview[pn.lower() + '_text'].text = '{}: {}'.format(
                pn.lower(), parm[pn])
        except:
            try:
                parm[pn] = sender.superview[pn].segments[sender.superview[pn]
                                                         .selected_index]
                parm[pn + '_idx'] = sender.superview[pn].selected_index
                # update text
                sender.superview[pn.lower() +
                                 '_text'].text = '{}: {:s}'.format(
                                     pn.lower(), parm[pn])
            except:
                pass


# Backend with 'cards' just list of the 4 atribute values


def makeDeck(colorSlice=(0, 3, 1),
             numberSlice=(0, 3, 1),
             shapeSlice=(0, 3, 1),
             shadeSlice=(0, 3, 1)):
    # card has 4 properties each with 3 states
    # eg color (r,g,b), number (1,2,3), shape (circle, square, sqiggle), shading (open, striped, solid) and
    deck = []
    for color in itertools.islice(['red', 'green', 'blue'], *colorSlice):
        for number in itertools.islice(range(1, 4), *numberSlice):
            for shape in itertools.islice(['ovals', 'diamonds', 'squiggles'],
                                          *shapeSlice):
                for shade in itertools.islice(['open', 'solid', 'stripes'],
                                              *shadeSlice):
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
    return "N= {}, Color R:{} G:{} B:{} Number 1:{} 2:{} 3:{} Shape Ov:{} Di:{} Sq:{} Shade Op:{} Fi:{} St:{}".format(
        len(deck), *colorCnt.values(), *numberCnt.values(), *shapeCnt.values(),
        *shadeCnt.values())


def removeCardsInSet(set, deck):
    # print(" set", set)
    # print(" deck", deck)
    for card in set:
        # print(" card", card)
        deck.remove(card)


def dealCard(deck):
    # chooses card and removes from deck
    card = random.choice(deck)
    deck.remove(card)
    return card


def makeDeal(deck):
    # deal = random.sample(deck, N)
    deal = []
    for i in range(parm['STARTDEAL']):
        deal.append(dealCard(deck))
    return deal


def printDeck(deck):
    for i, card in enumerate(deck):
        print(i, card)
    print(len(deck))


def findSets(deal):
    N = len(deal)
    # cnt=0
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
                    # print(i, j, k,check,deal[i],deal[j],deal[k])
                    # cnt=cnt+1
                # print(N, cnt)
    return setsFound


def goodness(set, deck):
    deckCopy = deck.copy()
    # print(" g***1 ", deckCopy)
    removeCardsInSet(set, deckCopy)
    # print(" g***2 ", deckCopy)
    return len(findSets(deckCopy))


def findBestSet(deal, deck):
    # best when removed from deal will have max sets still left
    #    if tie will choose onewith max sets left in deck
    sets = findSets(deal)
    # print(sets)
    if len(sets) == 0:
        return []
    else:
        sbest = sets[0]
        sbestgoodness = [goodness(sbest, deal), goodness(sbest, deck + deal)]
        # print(" first set {} goodness {}".format(sbest, sbestgoodness))
        if len(sets) == 1:
            # print(" is only set")
            return sbest
        # return sbest # just use first
        for set in sets[1:]:
            setgoodness = [goodness(set, deal), goodness(set, deck + deal)]
            # print(" {} goodness {}".format(set, setgoodness))
            if setgoodness > sbestgoodness:
                # go for worst choice
                # setgoodness = [goodness(set, deck + deal), goodness(set, deal)]
                # if setgoodness < sbestgoodness:
                sbest = set
                sbestgoodness = setgoodness
        # print(" best {} goodness {}".format(sbest, sbestgoodness))
        return sbest


# functions for drawing shape paths

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

# rectPath = ui.Path.rect(30, 75, 60, 30)
# rectPath.append_path(outlinePath)
# rectPath.line_width = 4.0
# rectPath.eo_fill_rule = True


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

####################

cardShapes = {
    'diamonds': diamondPaths,
    'ovals': ovalPaths,
    'squiggles': squigglePaths
}

# print(diamondPaths, ovalPaths, squigglePaths)

# TODO how to make non global?
posPositions = [(x, y) for y in range(3)
                for x in range(4)] + [(x, y)
                                      for x in range(4, 8) for y in range(3)]
freePositions = [True] * len(posPositions)


class Card(Node):
    def __init__(self, x, y, color, number, shape, shade, *args, **kwargs):
        # is next needed, doesnt seem to make difference
        Node.__init__(self, *args, **kwargs)

        if x == None:
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
        # print(x,y,color,number,shape,shade)
        shadings = {
            'solid': color,
            'stripes': (0, 0, 0, 0),
            'open': (1, 1, 1, 1)
        }
        shading = ShapeNode(path=shadingPath, *args, **kwargs)
        shading.stroke_color = color
        outline = ShapeNode(path=outlinePath, *args, **kwargs)
        # outline.z_position = 0

        outline.fill_color = shadings[shade]

        # print(outline.fill_color)
        # outline.blend_mode = BLEND_NORMAL
        outline.position = [0, 0]

        # print(cardShapes[shape][number - 1])

        self.cardShape = ShapeNode(
            path=cardShapes[shape][number - 1], *args, **kwargs)
        self.cardShape.stroke_color = color
        self.cardShape.fill_color = 'white'  #'#fbff9b'
        # cardShape.remove_from_parent()
        # outline.remove_from_parent()

        self.add_child(shading)
        self.add_child(outline)
        self.add_child(self.cardShape)


class MyScene(Scene):
    def setup(self):
        self.background_color = (0, 0, .5)
        self.v = None
        self.INPUT_ACTION_TAKEN = False
        self.nextT = 0
        # set up all permanent nodes and subnodes

        self.face = SpriteNode(
            'emj:Smiling_2', position=(500, 350), parent=self)
        self.face.alpha = 0
        self.face.z_position = 100000

        self.buttonParmPopup = ShapeNode(
            ui.Path.rounded_rect(0, 0, 60, 60, 12),
            position=(975, 30),
            fill_color='green',
            parent=self)

        self.buttonAllAuto = ShapeNode(
            ui.Path.rounded_rect(0, 0, 60, 60, 12),
            position=(875, 30),
            fill_color='white',
            parent=self)

        self.buttonAuto = ShapeNode(
            ui.Path.rounded_rect(0, 0, 60, 60, 12),
            position=(775, 30),
            fill_color='orange',
            parent=self)

        self.buttonPile = ShapeNode(
            ui.Path.rounded_rect(0, 0, 60, 60, 12),
            position=(180, 30),
            fill_color='purple',
            parent=self)

        self.buttonSet = ShapeNode(
            ui.Path.rounded_rect(0, 0, 60, 60, 12),
            position=(60, 30),
            fill_color='red',
            parent=self)

        self.messageBoard = Node(position=(50, 300), alpha=0, parent=self)
        #self.rect = SpriteNode(color='black', parent=self.messageBoard)
        self.rect = ShapeNode(
            outlinePath, color='#ff4300', parent=self.messageBoard)
        self.rect.anchor_point = (0, 0)
        self.messageBoard.z_position = 100
        self.message = LabelNode(
            '',
            position=(0, 0),
            color='#000000',
            font=('Helvetica', 100),
            parent=self.messageBoard)
        self.message.anchor_point = (0, 0)

        self.scoreBoard = Node(position=(10, 750), parent=self)
        self.score = LabelNode('', parent=self.scoreBoard)
        self.score.anchor_point = (0, 5)

        self.deckInfo = Node(position=(10, 725), parent=self)
        self.deckLabel = LabelNode('', parent=self.deckInfo)
        self.deckLabel.anchor_point = (0, 5)

        self.dealInfo = Node(position=(10, 700), parent=self)
        self.dealLabel = LabelNode('', color='yellow', parent=self.dealInfo)
        self.dealLabel.anchor_point = (0, 5)

        self.timerBar = ShapeNode(
            ui.Path.rect(0, 0, 5, 700),
            position=(1020, 0),
            anchor_point=(0, 0),
            fill_color='yellow',
            parent=self)

        ws = ui.get_window_size()
        self.setsFound = Node(position=(0, ws[1]), parent=self)

        # save number of permanent nodes
        self.numChildrenSetup = len(self.children)

        self.start()

    def stop(self):
        with open('setsolitaireParm.txt', 'w') as f:
            json.dump(parm, f)

    def start(self):
        # remove added card nodes and free their positions
        for node in self.children[self.numChildrenSetup:]:
            freePositions[node.posInd] = True
            node.remove_from_parent()

        # clear out self.setsFound   
        for child in self.setsFound.children:
            child.remove_from_parent()

        self.numCorrectSets = 0
        self.numBadSets = 0
        self.numAbortSetCall = 0
        self.numCorrectDeals = 0
        self.numBadDeals = 0
        self.numAutoSets = 0
        self.numAutoDeals = 0

        ws = ui.get_window_size()
        self.xDisp = self.xDispCol = ws[0] - 225
        self.yDisp = -150

        self.startNextTouch = False
        self.cardsOnTable = []
        self.setAutoFound = []
        self.cardsLeft = []
        self.setsDisplayed = []

        # make backend deck
        if parm['EASY']:
            attNum = parm['ATTRIBUTE_idx']
            if attNum == 0:
                attNum = random.randrange(3)
            else:
                attNum -= 1

            propertyFixed = parm['PROPERTY']
            if propertyFixed == 'Random':
                propertyFixed = random.choice(
                    ['Color', 'Number', 'Shape', 'Shade'])
            if propertyFixed == 'Color':
                self.deck = makeDeck(colorSlice=(attNum, attNum + 1, 1))
            elif propertyFixed == 'Number':
                self.deck = makeDeck(numberSlice=(attNum, attNum + 1, 1))
            elif propertyFixed == 'Shape':
                self.deck = makeDeck(shapeSlice=(attNum, attNum + 1, 1))
            elif propertyFixed == 'Shade':
                self.deck = makeDeck(shadeSlice=(attNum, attNum + 1, 1))
        else:
            self.deck = makeDeck()

        # make backend initial deal   
        self.deal = makeDeal(self.deck)
        # print(self.deal)
        self.deckLabel.text = checkDeck(self.deck)
        self.dealLabel.text = checkDeck(self.deal)

        # create and draw card nodes of deal in grid
        for cardData in self.deal:
            ctmp = Card(None, None, *cardData)
            # print(ctmp.position)
            self.add_child(ctmp)
            self.cardsOnTable.append(ctmp)

        # FIX only for the initial deal!
        for i, subnode in enumerate(self.children[self.numChildrenSetup:]):
            subnode.z_position = -i

        self.cardTouched = None
        self.buttonTouchId = None
        self.userCalledSet = False
        self.userCardsSelected = []
        self.showAllThenAbort = False
        self.message.text = ''
        self.messageBoard.alpha = 0
        self.nextT = self.t + parm['DELAY']
        self.startTime = self.t
        self.lastScoreShowTime = self.t

#    def dispFoundAction(self, node, progress):
#        return
#        if progress > 0.9:
#            node.x_scale = 1

    def changeParmPopup(self, touch):
        if self.v is None:
            self.v = ui.load_view(
                'setsolitaire.pyui')  # needed name here explicitly. Why?
            # repopulate param values and menus in gui
            for pn in paramnames:
                dbPrint(parm[pn], sfac[pn], pshift[pn], level=1)
                try:
                    self.v[pn].value = (parm[pn] - pshift[pn]) / sfac[pn]
                    # self.v[pn].value = parm[pn]
                except:
                    dbPrint(pn, 'value exception')
                    pass
                try:
                    self.v[pn].selected_index = parm[pn + '_idx']
                except:
                    dbPrint(pn, 'selected_index exception')
                    pass
                dbPrint(pn, parm[pn])

            self.v.background_color = '#5564ff'
            self.v.tint_color = '#12ff26'

            # popover will close when touch outside it
            input_action(self.v['DELAY'])  # force update of parameters

            # TODO attempt to immediately adjust count down
            self.nextT = self.t + parm['DELAY']

            self.v.present(
                'popover',
                popover_location=(touch.location[0], 768 - touch.location[1]),
                hide_title_bar=True)
            self.v.wait_modal()
            self.INPUT_ACTION_TAKEN = True
            self.v = None

    def newDeal(self):
        if parm['FILL']:
            NdealNow = min(
                len(self.deck),
                max(parm['DEAL'], parm['STARTDEAL'] - len(self.deal)))
        else:
            NdealNow = min(len(self.deck), parm['DEAL'])

        for i in range(NdealNow):
            newCard = dealCard(self.deck)
            self.deal.append(newCard)
            ctmp = Card(None, None, *newCard)
            self.add_child(ctmp)
            self.cardsOnTable.append(ctmp)
            self.deckLabel.text = checkDeck(self.deck)
            self.dealLabel.text = checkDeck(self.deal)
            self.updateScore()

    def activateAutoPlay(self):
        self.autoPlay()
        self.dealLabel.text = checkDeck(self.deal)
        self.deckLabel.text = checkDeck(self.deck)
        if (len(self.deck) == 0) & (len(findSets(self.deal)) == 0):
            # deck empty end game but cards left in deal
            self.message.text = ' Game Over \n Auto Play '
            bb = self.message.bbox
            self.rect.size = (bb[2], bb[3])
            self.messageBoard.alpha = 1
            self.updateScore()
            self.startNextTouch = True

    def autoPlay(self):
        if parm['REMOVE']:
            bestSetData = findBestSet(self.deal, self.deck)
        else:
            allSets = findSets(self.deal)
            dbPrint(allSets, level=3)
            dbPrint('sd ', self.setsDisplayed, level=2)
            dbPrint('cardsOnTable ', self.cardsOnTable, level=3)
            for bestSetData in allSets:
                dbPrint(bestSetData, level=3)
                setSelected = {
                    card
                    for card in self.cardsOnTable
                    if [card.color, card.number, card.shape, card.shade] in
                    bestSetData
                }
                dbPrint('setsel ', setSelected, level=2)
                if setSelected not in self.setsDisplayed:
                    break
            else:
                self.message.text = ' All Sets Found '
                bb = self.message.bbox
                self.rect.size = (bb[2], bb[3])
                self.messageBoard.alpha = 1
                self.startNextTouch = True
                return
                bestSetData = []

        self.setAutoFound = []
        self.cardsLeft = []
        if len(bestSetData) == 3:
            # a set so add its card nodes to setAutoFound
            # remove the backend card data from deal if remove option
            # print(bestSetData)
            for node in self.children[self.numChildrenSetup:]:
                if [node.color, node.number, node.shape,
                        node.shade] in bestSetData:
                    # node.x_scale = 1.2
                    # node.y_scale = 1.2
                    # node.z_position = 10
                    self.setAutoFound.append(node)
                else:
                    # node.alpha = .6
                    node.remove_all_actions()
                    node.x_scale = .5
                    node.y_scale = .5
                    self.cardsLeft.append(node)
            # print([[[node.color, node.number, node.shape,
            # node.shade] for node in self.setAutoFound]])
            self.numAutoSets += 1
            if parm['REMOVE']:
                removeCardsInSet(bestSetData, self.deal)

        else:  # no more sets on table, add new cards from deck
            if len(self.deck) != 0:
                self.newDeal()
                self.numAutoDeals += 1

    def moveAutoFoundToDisplay(self, actionTime=3):
        if len(self.setAutoFound) > 0:  # in autoplay
            self.dispFound(self.setAutoFound, auto=True, actionTime=actionTime)
            # for node in self.cardsOnTable:
            for node in self.cardsLeft:
                # restore cards made smaller during auto play
                node.remove_all_actions()
                node.run_action(Action.scale_to(1, actionTime))

            for node in self.setAutoFound:
                # print(node.position, self.setsFound.point_from_scene(node.position))
                if parm['REMOVE']:
                    self.cardsOnTable.remove(node)
                freePositions[node.posInd] = True
                # node.remove_from_parent()

        self.setAutoFound = []

    def dispFound(self, allSetsCards, auto=False, actionTime=3):
        # dbPrint(allSetsCards)
        self.setsDisplayed.append(set(allSetsCards))
        # print(self.setsDisplayed)
        for card in allSetsCards:
            if parm['REMOVE']:
                card.remove_from_parent()
            # print(*card.position)
            ctmp = Card(*self.setsFound.point_from_scene(card.position),
                        card.color, card.number, card.shape, card.shade)
            if auto:
                ctmp.cardShape.fill_color = '#000000'
            self.setsFound.add_child(ctmp)
            ctmp.run_action(
                Action.sequence(
                    Action.group(
                        Action.scale_to(0.2, actionTime),
                        Action.move_to(self.xDisp, self.yDisp, actionTime,
                                       TIMING_EASE_IN))))
            self.xDisp += .2 * width
        self.yDisp -= 0.2 * height + 2
        if self.yDisp <= -3 * (height + 2) - 150:
            self.xDispCol += 5 + 3 * 0.2 * width
            self.yDisp = -150
        self.xDisp = self.xDispCol

    def flashFace(self, img='emj:Smiling_2', dur=1):
        self.face.texture = Texture(img)
        sc = scaleFaces
        self.face.run_action(
            Action.sequence(
                Action.group(
                    Action.fade_to(0, 0),
                    Action.scale_x_to(sc * 1, 0), Action.scale_y_to(sc * 1,
                                                                    0)),
                Action.group(
                    Action.fade_to(1, dur / 2),
                    Action.scale_x_to(sc * 5, dur),
                    Action.scale_y_to(sc * 5, dur)),
                Action.group(
                    Action.fade_to(0, dur),
                    Action.scale_x_to(sc * 1, dur),
                    Action.scale_y_to(sc * 1, dur))))

    def processCorrectSet(self):
        self.nextT = self.t + parm['DELAY']  # reset auto timer
        # make nice sound
        if parm['SOUND_ON']:
            play_effect('digital:PowerUp1')
        if parm['FACES']:
            self.flashFace(imgCorrectSet)

        self.numCorrectSets += 1
        self.buttonSet.fill_color = 'red'
        self.dispFound(self.userCardsSelected)
        self.dealLabel.text = checkDeck(self.deal)

    def updateScore(self):
        ts = time.gmtime(int(self.t - self.startTime))
        if ts.tm_hour == 0:
            tstr = time.strftime("%M:%S", ts)
        else:
            tstr = time.strftime("%H:%M:%S", ts)
        self.score.text = "Set Calls: {} Correct, {} Incorrect, {} Aborted, Deals: {} Good, {} Premature, Auto: {} Sets, {} Deals, Time {}".format(
            self.numCorrectSets, self.numBadSets, self.numAbortSetCall,
            self.numCorrectDeals, self.numBadDeals, self.numAutoSets,
            self.numAutoDeals, tstr)

    def update(self):
        if self.t > self.lastScoreShowTime and not self.startNextTouch:
            self.updateScore()
            self.lastScoreShowTime += 1

        if self.startNextTouch:
            self.timerBar.alpha = 0
            return

        if self.showAllThenAbort:
            self.activateAutoPlay()
            self.moveAutoFoundToDisplay(actionTime=0)
            self.updateScore()
            return

        if parm['DELAY'] >= 121 or self.startNextTouch:
            self.timerBar.alpha = 0
            return

        self.timerBar.alpha = 1
        self.timerBar.y_scale = (self.nextT - self.t) / parm['DELAY']
        if self.t > self.nextT:
            self.activateAutoPlay()
            self.moveAutoFoundToDisplay()
            self.nextT = self.t + parm['DELAY']

    def touch_began(self, touch):

        if self.startNextTouch:
            self.start()
            return

        self.moveAutoFoundToDisplay()

        # Assertion check
        # this should never be true so raise exception if occurrs
        if [[c.color, c.number, c.shape, c.shade]
                for c in self.cardsOnTable] != self.deal:
            print('*', len(self.deal), len(self.cardsOnTable))
            print(self.deal)
            print([[c.color, c.number, c.shape, c.shade]
                   for c in self.cardsOnTable])
            raise AssertionError

        # touched found set button
        if touch.location in self.buttonSet.frame:
            if not self.userCalledSet:  # player signals found set 
                self.buttonSet.fill_color = 'yellow'
                self.userCalledSet = True
            else:  # player oops and aborts selecting cards
                if parm['SOUND_ON']:
                    play_effect('arcade:Jump_5')
                if parm['FACES']:
                    self.flashFace(imgOops)
                self.buttonSet.fill_color = 'red'
                self.numAbortSetCall += 1
                for c in self.userCardsSelected:
                    c.run_action(Action.scale_x_to(1))
                self.userCardsSelected = []
                self.userCalledSet = False
                self.buttonSet.fill_color = 'red'

        # touched change settings button
        if touch.location in self.buttonParmPopup.frame:
            self.changeParmPopup(touch)

        if touch.location in self.buttonPile.frame:
            if not parm['REMOVE']:
                return
            # if sets still exist penalty and bad noise
            # otherwise draw card
            bestSet = findBestSet(self.deal, self.deck)
            if len(bestSet) == 3:
                if parm['SOUND_ON']:
                    play_effect('game:Spaceship')
                if parm['FACES']:
                    self.flashFace(imgBadDealRequest)
                self.numBadDeals += 1
            else:
                # correct request
                self.nextT = self.t + parm['DELAY']  # reset auto timer
                if len(self.deck) == 0:
                    # deck empty end game
                    self.message.text = ' Game Over '
                    bb = self.message.bbox
                    self.rect.size = (bb[2], bb[3])
                    self.messageBoard.alpha = 1
                    self.startNextTouch = True
                    return
                self.newDeal()
                self.numCorrectDeals += 1

            # self.buttonPile.fill_color = 'yellow'
            # self.userCalledSet = True
            return

        if touch.location in self.buttonAllAuto.bbox:
            self.showAllThenAbort = True
            return

        if touch.location in self.buttonAuto.bbox:
            self.activateAutoPlay()
            self.moveAutoFoundToDisplay()

        for node in self.children[self.numChildrenSetup:]:
            # print(node.z_position)
            # node.remove_all_actions()
            if touch.location in node.bbox:
                self.cardTouched = node
                self.cardTouched.x_scale = 1.4
                if self.userCalledSet:
                    if ((len(self.userCardsSelected) < 3) and
                        (self.cardTouched not in self.userCardsSelected)):
                        self.userCardsSelected.append(self.cardTouched)
                        # print(self.userCardsSelected)
                    if (len(self.userCardsSelected) == 3):
                        if len(
                                findSets([[
                                    c.color, c.number, c.shape, c.shade
                                ] for c in self.userCardsSelected])) == 0:
                            # not a set, make noise subtract penalty etc
                            if parm['SOUND_ON']:
                                play_effect('game:Error')
                            if parm['FACES']:
                                self.flashFace(imgBadChoice)
                            self.buttonSet.fill_color = 'red'
                            # self.userCalledSet = False
                            for c in self.userCardsSelected:
                                c.remove_all_actions()
                                c.run_action(
                                    Action.sequence(
                                        Action.scale_x_to(1.4),
                                        Action.wait(1),
                                        Action.scale_x_to(1),
                                        # Action.remove()
                                    ))
                                # c.x_scale = 1
                            # self.userCardsSelected = []
                            self.numBadSets += 1
                        elif parm['REMOVE']:
                            # found set, remove cards from deck
                            removeCardsInSet(
                                [[c.color, c.number, c.shape, c.shade]
                                 for c in self.userCardsSelected], self.deal)
                            for c in self.userCardsSelected:
                                freePositions[c.posInd] = True
                                self.cardsOnTable.remove(c)
                                c.remove_from_parent()
                            self.processCorrectSet()
                        else:
                            if set(self.userCardsSelected
                                   ) not in self.setsDisplayed:
                                # found new set but dont remove
                                self.processCorrectSet()
                            else:
                                if parm['SOUND_ON']:
                                    play_effect('arcade:Jump_4')
                                if parm['FACES']:
                                    self.flashFace(imgAlreadyChosen)
                                self.buttonSet.fill_color = 'red'
                            for c in self.userCardsSelected:
                                # c.remove_all_actions()
                                c.run_action(Action.scale_x_to(1))

                        self.userCardsSelected = []
                        self.userCalledSet = False
                break
        self.updateScore()

    def touch_moved(self, touch):
        # immediate move to touch location
        if self.cardTouched != None:
            self.cardTouched.position = (touch.location[0], touch.location[1])

    def touch_ended(self, touch):
        # self.cardTouched.run_action(
        #    Action.move_to(touch.location[0], touch.location[1], 1,
        #           TIMING_SINODIAL), 'move_action_key')

        # self.cardTouched.remove_action('move_action_key')
        # print(self.userCalledSet)
        if (self.cardTouched != None) & (not self.userCalledSet):
            self.cardTouched.x_scale = 1
        self.cardTouched = None

if __name__ == '__main__':
    run(MyScene(), LANDSCAPE, show_fps=False)

