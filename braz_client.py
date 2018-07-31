import urllib.request
import sys
import random
import time
import copy

class Node:
    board = []
    alphabeta = 0
    parent = None
    edge = (-1,-1)
    maximizer = False
    calculated = False
    child = []

    def __init__(self, isMax):
        self.maximizer = isMax
        if self.maximizer:
            self.alphabeta = -10000
        else:
            self.alphabeta = 10000

    def expand(self, positions, player):
        for position in range(len(positions)):
            child = Node(not self.maximizer)
            child.board = copy.deepcopy(self.board)
            child.board[positions[position][0]][positions[position][1]] = player
            child.edge = copy.copy(positions[position])
            child.parent = self
            self.child.append(child)

    def updateAlpha(self,newValue):
        self.alphabeta = copy.copy(newValue)
        if self.parent is not None:                         # Se não for a raíz
            self.parent.updateAlphaBeta()                   # Checa recursivamente as mudanças
            if self.parent.alphabeta >= self.alphabeta:     # Update alpha só é chamado por maximizadores
                    self.destruction()                      # Se o pai é maximizador e maior, então poda esse nodo

    def updateBeta(self,newValue):
        self.alphabeta = copy.copy(newValue)
        if self.parent is not None:                         # Se não for a raíz
            self.parent.updateAlphaBeta()                   # Checa recursivamente as mudanças
            if self.parent.alphabeta <= self.alphabeta:     # Update beta só é chamado por minimizadores
                    self.destruction()                      # Se o pai é minimizador e menor, então poda esse nodo

    def updateAlphaBeta(self):
        childrenValue = []
        for c in range(len(self.child)):
            childrenValue.append(self.child[c].alphabeta)
        if self.maximizer:
            self.updateAlpha(max(childrenValue))
        else:
            self.updateBeta(min(childrenValue))


    def destruction(self):                          #Top-down delete
        for c in range(len(self.child)):
            self.child[c].destruction()
        del(self)


if len(sys.argv)==1:
    print("Voce deve especificar o numero do jogador (1 ou 2)\n\nExemplo:    ./random_client.py 1")
    quit()

# Alterar se utilizar outro host
host = "http://localhost:8080"

player = int(sys.argv[1])

occupiedSpaces = set
trumpSpeedUp = True

done = False
while not done:
    # Pergunta quem eh o jogador
    resp = urllib.request.urlopen("%s/jogador" % host)
    player_turn = int(resp.read())

    # Se jogador == 0, o jogo acabou e o cliente perdeu
    if player_turn==0:
        print("I lost!")
        done = True

    # Se for a vez do jogador
    if player_turn==player:
        # Pega a última jogada
        resp = urllib.request.urlopen("%s/ultima_jogada" % host)
        lastMove = eval(resp.read())

        # Se ainda não houver última jogada, você faz a jogada inicial
        if lastMove == (-1,-1):
            move = (6,5)
            occupiedSpaces.add(move)
        else:
            occupiedSpaces.add(lastMove)

            # Pega os movimentos possiveis
            resp = urllib.request.urlopen("%s/movimentos" % host)
            validMoves = eval(resp.read())

            # Pega o estado atual do tabuleiro
            resp = urllib.request.urlopen("%s/tabuleiro" % host)
            board = eval(resp.read())

            # Cria a raíz do minimax com o estado atual (é um max, pois escolhe entre as jogadas do jogador)
            root = Node(True)
            root.board = copy.deepcopy(board)

# Poda Trump
            if trumpSpeedUp:
                # Pega a vizinhança dos espaços ocupados
                allNeighborhood = []
                for i in range(len(occupiedSpaces)):
                    allNeighborhood.extend(upwardsNeighborhoodCoords(occupiedSpaces[i][0],occupiedSpaces[i][1]))
                    allNeighborhood.extend(downwardsNeighborhoodCoords(occupiedSpaces[i][0],occupiedSpaces[i][1]))
                    allNeighborhood.extend(verticalNeighborhoodCoords(occupiedSpaces[i][0],occupiedSpaces[i][1]))

                # Converte as listas em conjuntos
                movesTuple = map(tuple, validMoves)
                usefulNeighborhoodTuple = map(tuple, allNeighborhood)
                movesSet = set(movesTuple)
                usefulNeighborhoodSet = set(usefulNeighborhoodTuple)

                # Dos movimentos possíveis, considera só a vizinhança dos espaços ocupados
                usefulMovesSet = movesSet & usefulNeighborhoodSet
                usefulMoves = list(usefulMoves)
            else:
                usefulMoves = validMoves
# Poda Trump

            # Expande um ply
            root.expand(usefulMoves,player)
            for c in range(len(root.child)):
                depthExpansion()
                validChildMoves = copy.copy(usefulMoves)
                validChildMoves.remove(root.child[c].edge)
                if trumpSpeedUp:    #Se tivermos cortado vizinhos distantes, considera novos vizinhos à partir da jogada
                    validChildMoves.extend(upwardsNeighborhoodCoords(root.child[c].edge[0],root.child[c].edge[1]))
                    validChildMoves.extend(downwardsNeighborhoodCoords(root.child[c].edge[0],root.child[c].edge[1]))
                    validChildMoves.extend(verticalNeighborhoodCoords(root.child[c].edge[0],root.child[c].edge[1]))
                    # Remove as duplicatas transformando em conjunto e voltando para lista
                    validChildMoves = list(set(validChildMoves))
                root.child[c].expand(validChildMoves,adversary(player))

            # Escolhe um movimento aleatoriamente
            move = (movimentos)

        # Executa o movimento
        resp = urllib.request.urlopen("%s/move?player=%d&coluna=%d&linha=%d" % (host,player,move[0],move[1]))
        msg = eval(resp.read())

        # Se com o movimento o jogo acabou, o cliente venceu
        if msg[0]==0:
            print("I won!")
            done = True
        if msg[0]<0:
            raise Exception(msg[1])
            invalidMove = copy.move

        # Verifica se ainda está fazendo muita diferença no tamanho de movimentos considerados
        if (len(usefulMoves) - len(validMoves)) < 20:
            trumpSpeedUp = False
            print("Fall of the Wall!")

def depthExpansion(node, moves, depth, player):
    if depth < 10:
        node.expand(moves, player)
        uncalculated = [child for child in node.child if child.calculated == False]
        while len(uncalculated) > 0:
            validChildMoves = copy.copy(moves)
            validChildMoves.remove(uncalculated[0].edge)
            if trumpSpeedUp:  # Se tivermos cortado vizinhos distantes, considera novos vizinhos à partir da jogada
                validChildMoves.extend(upwardsNeighborhoodCoords(uncalculated[0].edge[0], uncalculated[0].edge[1]))
                validChildMoves.extend(downwardsNeighborhoodCoords(uncalculated[0].edge[0], uncalculated[0].edge[1]))
                validChildMoves.extend(verticalNeighborhoodCoords(uncalculated[0].edge[0], uncalculated[0].edge[1]))
                # Remove as duplicatas transformando em conjunto e voltando para lista
                validChildMoves = list(set(validChildMoves))
            depthExpansion(uncalculated[0],validChildMoves, depth-1, adversary(player))
            # Se o nodo foi podado dentro da recursão, quebra o laço
            if node is None:
                break
            # Senão, atualiza a lista de não calculados
            uncalculated = [child for child in node.child if child.calculated == False]
    else:
        evaluateNode(node, adversary(player))

def evaluateNode(node, player):
    h = neighborhoodValue(node.edge[0],node.edge[1],player)
    if node.maximizer:
        node.updateAlpha(h)
    else:
        node.updateBeta(h)
    if node is not None:            # Se o nodo não foi podado
        node.calculated = True      # Então marca como calculado

validMoves = []     #all moves, in the application, it comes from the API
currentState = []   #all spaces empty, in the application, it comes from the API

for i in range(11):
    if i > 5:
        limit = 15-i
    else:
        limit = 5+i
    for j in range(limit):
        validMoves.append((i,j))
    currentState.append([0] * limit)

state = ((1,1),(2,2),(5,8),(4,7),(20,20))
print(state)
validTuple = map(tuple,validMoves)
setState = set(state)
setValid = set(validTuple)
intersecSet = setState & setValid
print(intersecSet)
intersec = list(intersecSet)
for j in range(len(intersec)):
    for i in range(len(intersec[j])):
        print(f'{intersec[j][i]}')

fullOfDuplicatesList = [1,1,1,1,1,1, 3, 5,5,5,5,5,5,5, 6]
print(fullOfDuplicatesList)
fullOfDuplicatesList = list(set(fullOfDuplicatesList))
print(fullOfDuplicatesList)

def topNeighbor(column, line):
    if line > 1:
        return (column, line - 1)
    else:
        return None

def upperRightNeighbor(column, line):
    if (column < 6 or line > 1) and (column < len(state)):
        if column >= 6:
            return (column + 1, line - 1)
        else:
            return (column + 1, line)
    else:
        return None

def upperLeftNeighbor(column, line):
    if (column > 6 or line > 1) and (column > 1):
        if column > 6:
            return (column - 1, line)
        else:
            return (column - 1, line - 1)
    else:
        return None

def bottomNeighbor(column, line):
    if line < len(currentState[column - 1]):
        return (column, line + 1)
    else:
        return None

def lowerRightNeighbor(column, line):
    if (column < 6 or line < len(currentState[column - 1])) and column < 11:
        if column < 6:
            return (column + 1, line + 1)
        else:
            return (column + 1, line)
    else:
        return None

def lowerLeftNeighbor(column, line):
    if (column > 6 or line < len(currentState[column - 1])) and column > 1:
        if column > 6:
            return (column - 1, line + 1)
        else:
            return (column - 1, line)
    else:
        return None

def verticalNeighborhoodCoords(column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = topNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(nextNeighbor)
    for distance in range(4):
        nextNeighbor = bottomNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(nextNeighbor)
    return neighborhood

def downwardsNeighborhoodCoords(column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = upperLeftNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(nextNeighbor)
    for distance in range(4):
        nextNeighbor = lowerRightNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(nextNeighbor)
    return neighborhood

def upwardsNeighborhoodCoords(column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = lowerLeftNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(nextNeighbor)
    for distance in range(4):
        nextNeighbor = upperRightNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(nextNeighbor)
    return neighborhood

def verticalNeighborhood(state, column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = topNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]][nextNeighbor[1]])
    beforeSize = len(neighborhood)
    neighborhood.reverse()
    nextNeighbor = (column,line)
    neighborhood.append(state[nextNeighbor[0]][nextNeighbor[1]])
    for distance in range(4):
        nextNeighbor = bottomNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]][nextNeighbor[1]])
    return (neighborhood, beforeSize)

def downwardsNeighborhood(state, column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = upperLeftNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]][nextNeighbor[1]])
    beforeSize = len(neighborhood)
    neighborhood.reverse()
    nextNeighbor = (column,line)
    neighborhood.append(state[nextNeighbor[0]][nextNeighbor[1]])
    for distance in range(4):
        nextNeighbor = lowerRightNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]][nextNeighbor[1]])
    return (neighborhood, beforeSize)

def upwardsNeighborhood(state, column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = lowerLeftNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]][nextNeighbor[1]])
    beforeSize = len(neighborhood)
    neighborhood.reverse()
    nextNeighbor = (column,line)
    neighborhood.append(state[nextNeighbor[0]][nextNeighbor[1]])
    for distance in range(4):
        nextNeighbor = upperRightNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]][nextNeighbor[1]])
    return (neighborhood, beforeSize)

def adversary(player):
    return player + 1 - 2*(player-1)

def sandwitchValue(window, player, before, direction, column, line): #direction = 0 vert, -1 down, 1 up
    if(before>2):
        for cell in range(4):
            s += str(window[cell+before-3])
        if ("1221" in s and player == 1) or ("2112" in s and player == 2):
            return 1.1
    if(len(window)-before-1>2):
        for cell in range(4):
            s += str(window[cell+before+1])
        if ("1221" in s and player == 1) or ("2112" in s and player == 2):
            return 1.1
    return 1

def neighborhoodValue(column,line,player):
    up = upwardsNeighborhood(state,column,line)
    down = downwardsNeighborhood(state,column,line)
    vert = verticalNeighborhood(state,column,line)
    windowValues = [windowValue(up[0],player),windowValue(down[0],player),windowValue(vert[0],player)]
    for w in range(3):
        if windowValues[w] > 74:
            total = 1000
    if total < 1000:
        total = windowValue(up[0],player) + windowValue(down[0],player) + windowValue(vert[0],player)
        total *= max(sandwitchValue(up[0],player,up[1],1,column,line),sandwitchValue(down[0],player,down[1],-1,column,line),sandwitchValue(vert[0],player,vert[1],0,column,line))


def windowValue(window, player):
    gap = [[],[],[]]
    currentGapStart
    currentGapType  # 0 neutral 1 player 2 adversary
    currentGapSize
    for i in range(len(window)):
        if window[i] == 0:
            if playerSequence>0:
                currentGapStart = 1
            elif adversarySequence>0:
                currentGapStart = 2
            elif currentGapSize==0:
                currentGapStart = 0
            playerSequence = 0
            adversarySequence = 0
            playerPotential += 1
            currentGapSize += 1
        elif window[i] == player:
            playerPieces += 1
            playerSequence += 1
            playerPotential += 1
            adversarySequence = 0
            if currentGapSize>0:
                if currentGapStart < 2: currentGapType = 1
                else: currentGapType = 0
                gap[currentGapType].append(currentGapSize)
        else:
            adversarySequence += 1
            playerSequence = 0
            playerPotential = 0
            if currentGapSize>0:
                if currentGapStart != 1: currentGapType = 2
                else: currentGapType = 0
                gap[currentGapType].append(currentGapSize)
        playerTopRow = max(playerTopRow,playerSequence)
        playerTopPotential = max(playerTopPotential,playerPotential)
    if playerTopPotential >= 5:
        return playerTopRow**2.5 + 2*playerPieces + (2/((1+min(gap[0],gap[1]))*2))*(gaps**2.1) + ((len(gap[0])+len(gap[1])+len(gap[2]))/8) + 1.75*playerTopPotential
    else:
        return 0
