import threading
import time

#current issues:
#   solo players are very likely to end up against other large groups
#   no skilled based matchmaking
#   will create small lobbies if there isn't lots of people

class MatchMaker:
    gameLobbySize = 8
    matchMakeQueue = []

    def __init__(self):
        threading.Thread(target=self.matchMakeLoop).start()

        self.enQueue(("rory", "shrey"))
        self.enQueue("dan")
        self.enQueue(("henry", "chewt", "gannon"))
        self.enQueue(("lewis", "alex", "sina"))
        self.enQueue(("george", "gordan"))
        self.enQueue("botbot")
        self.enQueue("noah")
        self.enQueue(("flo", "evie"))
        self.enQueue(("dom", "charlie", "fred", "gerald"))


        entered = ""
        while entered != "quit":
            entered = input()
            if entered != "quit":
                self.enQueue(eval(entered))
                print(self.matchMakeQueue)


    def getMatchQueue(self):
        return self.matchMakeQueue

    def getTotalQueueWeight(self):
        weight = 0
        for x in self.matchMakeQueue:
            weight += len(x)
        return weight


    #add a player or players to the queue
    #requires matchMakeQueue Array
    #takes player as string or tuple depending on if adding one or more players
    #if string passed turns into single tuple
    #if single item tuple gets append to end of matchMakeQueue
    #if tuple more than 1 item gets inserted into array before any tuples small than itself
    def enQueue(self, player):
        if type(player) == str:
            player = (player,)

        weight = len(player)
        if len(self.matchMakeQueue) == 0:
            self.matchMakeQueue.append(player)
        else:
            if weight == 1:
                self.matchMakeQueue.append(player)
            else:
                index = 0
                while len(self.matchMakeQueue[index]) >= weight:
                    index += 1
                self.matchMakeQueue.insert(index, player)

    #creates a group of players and adds them to a new game based on the size specified in matchSize
    #grabs usernames from queue starting at the beginning
    #skips an item if the item weight will make the total weight greater than 8
    #removes players from queue once the group is finalized
    def deQueue(self):
        group = []
        index = 0
        clearAmount = 0

        while len(group) != MatchMaker.gameLobbySize and index < len(self.matchMakeQueue):
            if len(group) + len(self.matchMakeQueue[index]) <= MatchMaker.gameLobbySize:
                for x in self.matchMakeQueue[index]:
                    group.append(x)
                    self.matchMakeQueue[index] = ""
                clearAmount += 1
            index = index + 1

        for x in range(clearAmount-1):
            self.matchMakeQueue.remove("")

        #todo replace with game creation
        print(group)

    def matchMakeLoop(self):
        skipped = 0
        while True:
            if (self.getTotalQueueWeight() >= MatchMaker.gameLobbySize or skipped == 10) and len(self.matchMakeQueue) > 1:
                self.deQueue()
                skipped = 0
            else:
                skipped = skipped + 1
            time.sleep(1)


test = MatchMaker()
