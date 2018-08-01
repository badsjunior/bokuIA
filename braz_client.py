import urllib.request
import sys
import random
import time
import copy
from typing import List

bokuBoard = []

for column in range(11):
    if column <= 5:
        height = 5 + column
    else:
        height = 15 - column
    bokuBoard.append([0] * height)

class Node:
    board = []
    alpha = -10000  # O nodo tem este valor ou um valor menor que este (limite superior, máximo)
    beta = 10000    # O nodo tem este valor ou um valor maior que este (limite inferior, mínimo)
    f, g, h = 0, 0, 0
    parent: 'Node' = None
    edge = (-1,-1)
    maximizer = False
    calculated = False
    children: List['Node'] = []

    def __init__(self, isMax, parent, board, edge, player):
        self.maximizer = isMax
        self.board = copy.deepcopy(board)
        self.parent = parent
        if self.parent is not None:
            self.board[edge[0]-1][edge[1]-1] = copy.copy(player)
            self.edge = copy.copy(edge)
            self.g = copy.copy(self.parent.f)
            self.h = neighborhoodValue(self.board,self.edge[0],self.edge[1],player)
            if self.maximizer:
                self.h *= -1
        else:
            self.edge = (-1,-1)
            self.g, self.h = 0, 0
        self.f = self.g + self.h
    def __repr__(self):
        return '-' + str(self.edge) + '-> [' + str(self.beta) + ';' + str(self.alpha) + ']' + '<' + str(self.f) + '=' + str(self.g) + '+' + str(self.h) + '>'# = ' + str(self.board)

    def expand(self, positions, player):
        for position in range(len(positions)):
            child = Node(not self.maximizer,self,self.board,positions[position],player)
            child.children: List['Node'] = []
            #print(f'[B] grandchildren aux = {child.children} from {child}')
            self.children.append(copy.copy(child))
            #print(f'[A] children = {self.children}')
            #print(f'[A] grandchildren aux = {child.children} from {child}')
            #print(f'[A] grandchildren = {self.children[position].children} from {self.children[position]}')

    def updateAlpha(self):
        oldAlpha = copy.copy(self.alpha)
        if self.maximizer:
            calculated = [child.beta for child in self.children if child.calculated == True]
        else:
            calculated = [child.alpha for child in self.children if child.calculated == True]
        # print(calculated)
        if len(calculated) > 0:
            self.alpha = max(calculated)
        if self.alpha != oldAlpha and self.maximizer and self.parent is not None:
            self.parent.updateAlpha()
            self.parent.updateBeta()
            if self.alpha > self.parent.beta:
                self.destruction()
        # self.alpha = copy.copy(newValue)
        # if self.parent is not None:
        #     if self.maximizer:
        #         if self.alpha > self.parent.alpha:
        #             self.parent.updateAlpha(self.alpha)
        #         if self.alpha < self.parent.beta:
        #             self.parent.updateBeta(self.alpha)
        #         else:
        #             self.destruction()
        #     else:
        #         if self.alpha >= self.beta > self.parent.alpha:
        #             self.parent.updateAlpha(self.beta)


    def updateBeta(self):
        oldBeta = copy.copy(self.beta)
        if self.maximizer:
            calculated = [child.beta for child in self.children if child.calculated == True]
        else:
            calculated = [child.alpha for child in self.children if child.calculated == True]
        # print(calculated)
        if len(calculated) > 0:
            self.beta = max(calculated)
        if self.beta != oldBeta and not self.maximizer and self.parent is not None:
            self.parent.updateAlpha()
            self.parent.updateBeta()
            if self.beta < self.parent.alpha:
                self.destruction()

        # self.beta = copy.copy(newValue)
        # if self.parent is not None:
        #     if not self.maximizer:
        #         if self.beta < self.parent.beta:
        #             self.parent.updateBeta(self.beta)
        #         if self.beta > self.parent.alpha:
        #             self.parent.updateAlpha(self.beta)
        #         else:
        #             self.destruction()
        #     else:
        #         if self.beta <= self.alpha < self.parent.beta:
        #             self.parent.updateBeta(self.alpha)


    def evaluate(self):
        self.alpha = copy.copy(self.f)
        self.beta = copy.copy(self.f)
        self.calculated = True
        self.parent.updateAlpha()
        self.parent.updateBeta()


    def destruction(self):                          #Top-down delete
        for c in range(len(self.children)):
            self.children[c].destruction()
        self.children.clear()
        del self

    def tree(self,s,depth):
        for d in range(depth):
            s += '    '
        s += str(self) + "\n"
        for c in range(len(self.children)):
            s += self.children[c].tree(s,depth+1)
        return s

def depthExpansion(node, moves, depth, player):
    if depth < 2:
    #if len(moves) > 0:
        #print(f'{depth}{node} : {len(moves)}')
        node.expand(moves, player)
        uncalculatedChildren = copy.copy(node.children)
        uncalculated = [child for child in uncalculatedChildren if child.calculated == False]
        while len(uncalculated) > 0:
            validChildMoves = copy.copy(moves)
            #print(f'uncalculatedEdge = {uncalculated[0].edge}; moves = {moves}\nchild moves = {validChildMoves}')
            if trumpSpeedUp:  # Se tivermos cortado vizinhos distantes, considera novos vizinhos à partir da jogada
                validChildMoves.extend(upwardsNeighborhoodCoords(uncalculated[0].board,uncalculated[0].edge[0], uncalculated[0].edge[1]))
                validChildMoves.extend(downwardsNeighborhoodCoords(uncalculated[0].board,uncalculated[0].edge[0], uncalculated[0].edge[1]))
                validChildMoves.extend(verticalNeighborhoodCoords(uncalculated[0].board,uncalculated[0].edge[0], uncalculated[0].edge[1]))
                # Remove as duplicatas transformando em conjunto e retornando para lista
                validChildMoves = list(set(validChildMoves))
            validChildMoves.remove(uncalculated[0].edge)
            #print(f'[{depth}] moves: {len(moves)} childMoves: {len(validChildMoves)}')
            depthExpansion(uncalculated[0],validChildMoves, depth+1, adversary(player))
            # Se o nodo foi podado dentro da recursão, quebra o laço
            if node is None:
                break
            # Senão, atualiza a lista de não calculados
            uncalculatedChildren = copy.copy(node.children)
            uncalculated = [child for child in uncalculatedChildren if child.calculated == False]
    else:
        #print(f'{depth}{node} : {len(moves)}')
        node.evaluate()

def topNeighbor(column, line):
    if line > 1:
        return (column, line - 1)
    else:
        return None

def upperRightNeighbor(column, line):
    if (column < 6 or line > 1) and (column < len(bokuBoard)):
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
    if line < len(bokuBoard[column - 1]):
        return (column, line + 1)
    else:
        return None

def lowerRightNeighbor(column, line):
    if (column < 6 or line < len(bokuBoard[column - 1])) and column < 11:
        if column < 6:
            return (column + 1, line + 1)
        else:
            return (column + 1, line)
    else:
        return None

def lowerLeftNeighbor(column, line):
    if (column > 6 or line < len(bokuBoard[column - 1])) and column > 1:
        if column > 6:
            return (column - 1, line + 1)
        else:
            return (column - 1, line)
    else:
        return None

def verticalNeighborhoodCoords(state, column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = topNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        elif state[nextNeighbor[0]-1][nextNeighbor[1]-1] == 0:
            neighborhood.append(nextNeighbor)
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = bottomNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        elif state[nextNeighbor[0]-1][nextNeighbor[1]-1] == 0:
            neighborhood.append(nextNeighbor)
    return neighborhood

def downwardsNeighborhoodCoords(state, column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = upperLeftNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        elif state[nextNeighbor[0]-1][nextNeighbor[1]-1] == 0:
            neighborhood.append(nextNeighbor)
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = lowerRightNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        elif state[nextNeighbor[0]-1][nextNeighbor[1]-1] == 0:
            neighborhood.append(nextNeighbor)
    return neighborhood

def upwardsNeighborhoodCoords(state, column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = lowerLeftNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        elif state[nextNeighbor[0]-1][nextNeighbor[1]-1] == 0:
            neighborhood.append(nextNeighbor)
    nextNeighbor = (column, line)
    for distance in range(4):
        nextNeighbor = upperRightNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        elif state[nextNeighbor[0]-1][nextNeighbor[1]-1] == 0:
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
            neighborhood.append(state[nextNeighbor[0]-1][nextNeighbor[1]-1])
    beforeSize = len(neighborhood)
    neighborhood.reverse()
    nextNeighbor = (column,line)
    neighborhood.append(state[nextNeighbor[0]-1][nextNeighbor[1]-1])
    for distance in range(4):
        nextNeighbor = bottomNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]-1][nextNeighbor[1]-1])
    return (neighborhood, beforeSize)

def downwardsNeighborhood(state, column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = upperLeftNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]-1][nextNeighbor[1]-1])
    beforeSize = len(neighborhood)
    neighborhood.reverse()
    nextNeighbor = (column,line)
    neighborhood.append(state[nextNeighbor[0]-1][nextNeighbor[1]-1])
    for distance in range(4):
        nextNeighbor = lowerRightNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]-1][nextNeighbor[1]-1])
    return (neighborhood, beforeSize)

def upwardsNeighborhood(state, column, line):
    neighborhood = []
    nextNeighbor = (column,line)
    for distance in range(4):
        nextNeighbor = lowerLeftNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]-1][nextNeighbor[1]-1])
    beforeSize = len(neighborhood)
    neighborhood.reverse()
    nextNeighbor = (column,line)
    neighborhood.append(state[nextNeighbor[0]-1][nextNeighbor[1]-1])
    for distance in range(4):
        nextNeighbor = upperRightNeighbor(nextNeighbor[0], nextNeighbor[1])
        if nextNeighbor is None:
            break
        else:
            neighborhood.append(state[nextNeighbor[0]-1][nextNeighbor[1]-1])
    return (neighborhood, beforeSize)

def adversary(player):
    return player + 1 - 2*(player-1)

def sandwitchValue(window, player, before): #direction = 0 vert, -1 down, 1 up
    s = ''
    if before>2:
        for cell in range(4):
            s += str(window[cell+before-3])
        if ("1221" in s and player == 1) or ("2112" in s and player == 2):
            return 1.15
    if len(window)-before-1>2:
        for cell in range(4):
            s += str(window[cell+before])
        if ("1221" in s and player == 1) or ("2112" in s and player == 2):
            return 1.15
    return 1

def neighborhoodValue(state,column,line,player):
    up = upwardsNeighborhood(state,column,line)
    down = downwardsNeighborhood(state,column,line)
    vert = verticalNeighborhood(state,column,line)
    windowValues = [windowValue(up[0],player),windowValue(down[0],player),windowValue(vert[0],player)]
    total = 0
    for w in range(3):
        if windowValues[w] > 74:
            total = 1000
    if total < 1000:
        total = windowValue(up[0],player) + windowValue(down[0],player) + windowValue(vert[0],player)
        total *= max(sandwitchValue(up[0],player,up[1]),sandwitchValue(down[0],player,down[1]),sandwitchValue(vert[0],player,vert[1]))
    return total


def windowValue(window, player):
    gap = [[],[],[]]
    currentGapStart = 0
    currentGapSize = 0
    playerPieces = 0
    playerSequence = 0
    adversarySequence = 0
    playerPotential = 0
    playerTopPotential = 0
    playerTopRow = 0
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
        minGap0, minGap1, minGap2 = 0, 0, 0
        if len(gap[0]) > 0: minGap0 = min(gap[0])
        if len(gap[1]) > 0: minGap1 = min(gap[1])
        gapAmount = len(gap[0]) + len(gap[1]) + len(gap[2])
        return playerTopRow**2.5 + 2*playerPieces + (2/(1+min(minGap0,minGap1))*2)*gapAmount**2.1 + (gapAmount/8) + 1.75*playerTopPotential
    else:
        return 0

if len(sys.argv)==1:
    print("Voce deve especificar o numero do jogador (1 ou 2)\n\nExemplo:    ./random_client.py 1")
    quit()

# Alterar se utilizar outro host
host = "http://localhost:8080"

player = int(sys.argv[1])

occupiedSpaces = []
trumpSpeedUp = True
triedAndFailed = False
bestNodes: List['Node'] = None
removing = False
move = None
triedMoves = []
allNeighborhood = []

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
        root: 'Node' = None
        start_time = time.time()
        if not triedAndFailed:
            # Pega a última jogada
            resp = urllib.request.urlopen("%s/ultima_jogada" % host)
            lastMove = eval(resp.read())

            # Se ainda não houver última jogada, você faz a jogada inicial
            if lastMove == (-1,-1):
                print('First move!')
                move = (6,5)
            else:
                # Pega os movimentos possiveis
                resp = urllib.request.urlopen("%s/movimentos" % host)
                validMoves = eval(resp.read())

                # Pega o estado atual do tabuleiro
                resp = urllib.request.urlopen("%s/tabuleiro" % host)
                board = eval(resp.read())

                # Verifica o espaço de um movimento válido para saber se é uma jogada para botar peças ou para retirar
                if board[validMoves[0][0]-1][validMoves[0][1]-1] == 0:
                    removing = False
                    # Se está jogando e não é a jogada inicial, então adiciona aos espaços ocupados a jogada do inimigo
                    #print(f'lastmove[0] = {lastMove[0]}; lastmove[1] = {lastMove[1]}; board = {board}')
                    if board[lastMove[0]-1][lastMove[1]-1] != 0:# Mas somente se a jogada dele não foi de retirar peças
                        occupiedSpaces.append(lastMove)         # Se foi de retirada, então não há como saber onde ele
                    else:                                       # botou a última peça dele, então recalcula os espaços
                        occupiedSpaces.clear()                  # ocupados.
                        for i in range(len(board)):
                            for j in range(len(board[i])):
                                if board[i][j] != 0:
                                    occupiedSpaces.append((i+1,j+1))
                else:
                    removing = True

                # Cria a raíz do minimax com o estado atual (é um max, pois escolhe entre as jogadas do jogador)
                root = Node(True,None,board,None,player)

                if removing:
                    root.expand(validMoves,adversary(player))
                    for c in range(len(root.children)):
                        root.children[c].evaluate()
                else:
                # Poda Trump
                    if trumpSpeedUp:
                        # Pega a vizinhança dos espaços ocupados
                        for i in range(len(occupiedSpaces)):
                            allNeighborhood.extend(upwardsNeighborhoodCoords(root.board,occupiedSpaces[i][0],occupiedSpaces[i][1]))
                            allNeighborhood.extend(downwardsNeighborhoodCoords(root.board,occupiedSpaces[i][0],occupiedSpaces[i][1]))
                            allNeighborhood.extend(verticalNeighborhoodCoords(root.board,occupiedSpaces[i][0],occupiedSpaces[i][1]))

                        # Converte as listas em conjuntos
                        movesTuple = map(tuple, validMoves)
                        usefulNeighborhoodTuple = map(tuple, allNeighborhood)
                        movesSet = set(movesTuple)
                        usefulNeighborhoodSet = set(usefulNeighborhoodTuple)

                        # Dos movimentos possíveis, considera só a vizinhança dos espaços ocupados
                        usefulMovesSet = movesSet & usefulNeighborhoodSet
                        usefulMoves = list(usefulMovesSet)
                    else:
                        usefulMoves = validMoves
                # Poda Trump

                    # Expande um ply
                    root.expand(usefulMoves,player)
                    for c in range(len(root.children)):
                        validRootChildMoves = copy.copy(usefulMoves)
                        validRootChildMoves.remove(root.children[c].edge)
                        if trumpSpeedUp:    #Se tivermos cortado vizinhos distantes, considera novos vizinhos à partir da jogada
                            validRootChildMoves.extend(upwardsNeighborhoodCoords(root.children[c].board,root.children[c].edge[0], root.children[c].edge[1]))
                            validRootChildMoves.extend(downwardsNeighborhoodCoords(root.children[c].board,root.children[c].edge[0], root.children[c].edge[1]))
                            validRootChildMoves.extend(verticalNeighborhoodCoords(root.children[c].board,root.children[c].edge[0], root.children[c].edge[1]))
                            # Remove as duplicatas transformando em conjunto e voltando para lista
                            validRootChildMoves = list(set(validRootChildMoves))
                        depthExpansion(root.children[c], validRootChildMoves, 1, adversary(player))

                    # Verifica se ainda está fazendo muita diferença no tamanho de movimentos considerados
                    if trumpSpeedUp and (len(validMoves) - len(usefulMoves)) < 10:
                        trumpSpeedUp = False
                        print("Fall of the Wall!")

                # Ordena (decrescente) os nodos filhos do estado atual (as possíveis jogadas neste turno) pela pontuação
                bestNodes = sorted(root.children, key=lambda child: child.beta, reverse=True)
                # print(bestNodes)
                # print(f'grandchildren: {root.children[0].children}')
                # print(f'grandgrandchildren: {root.children[0].children[0].children}')
                # print(f'wtfchildren: {root.children[0].children[0].children[0].children}')

        # Se não tem nodos para escolher provavelmente foi um bug ou todos os movimentos possíveis são proibidos
        if move is None:
            if bestNodes is None:
                print("I'm broken. Let's go random.")
                # Pega os movimentos possiveis
                resp = urllib.request.urlopen("%s/movimentos" % host)
                validMoves = eval(resp.read())
                move = random.choice(validMoves)
            else:   # Se tiver, escolhe o primeiro da lista (o maior)
                move = bestNodes[0].edge

        # Executa o movimento
        resp = urllib.request.urlopen("%s/move?player=%d&coluna=%d&linha=%d" % (host,player,move[0],move[1]))
        msg = eval(resp.read())

        # Se com o movimento o jogo acabou, o cliente venceu
        if msg[0]==0:
            print(f'I won by completing my sequence at {move}!')
            done = True
        elif msg[0]<0:
            triedAndFailed = True
            print(f'What? Why can\'t I play on {move}?')
            raise Exception(msg[1])
        else:
            #Se teve sucesso, começa a limpeza
            occupiedSpaces.append(move)
            print(f'I played at {move} after thinking by {time.time() - start_time} seconds')
            player_turn = adversary(player)
            if root is not None:
                s = ''
                #print(root.tree(s,0))
                root.destruction()
            allNeighborhood.clear()
            move = None

    # Descansa um pouco para nao inundar o servidor com requisicoes
    time.sleep(1)
