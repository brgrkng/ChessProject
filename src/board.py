from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import os
import copy


class Board:

    def __init__(self):
        self.squares = [[0,0,0,0,0,0,0,0] for col in range(COLS)]

        self.last_move= None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self,piece,move, testing=False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        #console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece




        if piece.name =='pawn':

            # en passant capture
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(os.path.join(
                        '../assets/sounds/capture.wav'
                    ))
                    sound.play()

            # pawn en passant

            else:
                self.check_promotion(piece, final)

        # king castling
        if piece.name == 'king':
            if self.castling(initial,final) and not testing:
                diff = final.col-initial.col
                rook = piece.left_rook if (diff<0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        # move
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        #save last move
        self.last_move = move



    def valid_move(self,piece,move):
        return move in piece.moves

    def check_promotion(self,piece,final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self,initial,final):
        return abs(initial.col-final.col) == 2


    def set_true_en_passant(self,piece):
        if not isinstance(piece,Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Piece):
                    self.squares[row][col].piece.en_passant = False

        piece.en_passant = True


    def in_check(self, piece, move):

        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)

        temp_board.move(temp_piece, move, testing=True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_rival_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        return False

    def calc_moves(self,piece,row,col,bool=True):
        '''
        Calculate all the possible moves of a specific pece on a specific position
        '''

        def pawn_moves():
            steps = 1 if piece.moved else 2

            # vertical moves
            start = row+piece.dir
            end = row+(piece.dir*(1+steps))

            for move_row in range(start,end,piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        #create initial and final move squares
                        initial = Square(row,col)
                        final = Square(move_row,col)

                        # create a new move
                        move = Move(initial, final)

                        # check for checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

                    #blocked
                    else:
                        break
                else:
                    break
            # diagonal moves
            move_row = row+piece.dir

            move_cols = [col-1,col+1]

            for move_col in move_cols:
                if Square.in_range(move_row,move_col):
                    if self.squares [move_row][move_col].has_rival_piece(piece.color):
                        # create initial and final move squares
                        initial = Square(row,col)
                        final_piece = self.squares[move_row][move_col].piece
                        final = Square(move_row,move_col,final_piece)

                        #create a move
                        move = Move(initial,final)

                        # check for checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            #en passant
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            #left en passant
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_rival_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if p.name == 'pawn':
                        if p.en_passant:
                            # create initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)

                            # create a move
                            move = Move(initial, final)

                            # check for checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
            #right en passant
            if Square.in_range(col+1) and row == r:
                if self.squares[row][col+1].has_rival_piece(piece.color):
                    p = self.squares[row][col+1].piece
                    if p.name == 'pawn':
                        if p.en_passant:
                            # create initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col+1, p)

                            # create a move
                            move = Move(initial, final)

                            # check for checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)




        def knight_moves():
            # 8 possible moves
            possible_moves = [
                (row-2,col+1),
                (row-1,col+2),
                (row+1,col+2),
                (row+2,col+1),
                (row+2,col-1),
                (row+1,col-2),
                (row-1,col-2),
                (row-2,col-1),
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                print(possible_move)
                if Square.in_range(possible_move_row,possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        # create squares of the move
                        initial = Square(row,col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,possible_move_col,final_piece)
                        # create a new move
                        move = Move(initial,final)

                        #append new valid move
                        # check for checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else:
                                break
                        else:
                            piece.add_move(move)

        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row+row_incr
                possible_move_col = col+col_incr

                while True:

                    if Square.in_range(possible_move_row,possible_move_col):

                        #initial and final
                        initial = Square(row,col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,possible_move_col,final_piece)

                        move = Move(initial,final)

                        #empty = continue looping
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            #append new move
                            # check for checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

                        # has enemy piece = add_move + break
                        elif self.squares[possible_move_row][possible_move_col].has_rival_piece(piece.color):
                            #append a new move
                            # check for checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break

                        # has team piece
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break

                    else:
                        break

                    #incrementing incrs
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col+col_incr

        def king_moves():
            adjs = [
                (row-1,col-1), #up left
                (row-1, col),  #up
                (row - 1, col + 1), # up right
                (row , col - 1) , #left
                (row, col + 1), # right
                (row + 1, col - 1),# down left
                (row + 1, col), # down
                (row + 1, col + 1), #down right
            ]

            #normal moves
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row,possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        #create squares of the new moves
                        initial = Square(row,col)
                        final = Square(possible_move_row,possible_move_col)

                        # create new move
                        move = Move(initial,final)

                        #append new valid move

                        # check for checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else:
                                break
                        else:
                            piece.add_move(move)

            # CASTLING SECTION
            if not piece.moved:

                # King Castling
                right_rook = self.squares[row][7].piece
                if right_rook.name == 'rook':
                    if not right_rook.moved:
                        for iter_col in range(5, 7):
                            if self.squares[row][iter_col].has_piece():
                                break  # Castling not possible
                            if iter_col == 6:
                                piece.right_rook = right_rook

                                # rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)

                                # check for checks
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        piece.add_move(moveK)
                                        right_rook.add_move(moveR)
                                else:
                                    right_rook.add_move(moveR)
                                    piece.add_move(moveK)

                # Queen Castling
                left_rook = self.squares[row][0].piece
                if left_rook.name =='rook':
                    if not left_rook.moved:
                        for iter_col in range(1,4):
                            if self.squares[row][iter_col].has_piece():
                                break # Castling not possible
                            if iter_col==3:
                                piece.left_rook = left_rook

                                # rook move
                                initial = Square(row,0)
                                final = Square(row,3)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)

                                # check for checks
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        piece.add_move(moveK)
                                        left_rook.add_move(moveR)
                                else:
                                    left_rook.add_move(moveR)
                                    piece.add_move(moveK)


        if piece.name == 'pawn':
            pawn_moves()

        elif piece.name =='knight':
            knight_moves()

        elif piece.name =='bishop':
            straightline_moves([
                (-1,1), #upper right
                (-1,-1), # upper left
                (1,1), # down-right
                (1,-1) # down-left
            ])

        elif piece.name =='rook':
            straightline_moves([
                (1,0), #up
                (-1,0), #down
                (0,1), #right
                (0,-1) #left
            ])

        elif piece.name =='queen':
            straightline_moves([
                (1, 0),  # up
                (-1, 0),  # down
                (0, 1),  # right
                (0, -1),  # left
                (-1,1), #upper right
                (-1,-1), # upper left
                (1,1), # down-right
                (1,-1) # down-left
            ])

        elif piece.name =='king':
            king_moves()

    def _create(self):

        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row,col)

    def _add_pieces(self,color):

        row_pawn,row_other = (6,7) if color =='white' else (1,0)

        #pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn,col,Pawn(color))

        #knights
        self.squares[row_other][1] = Square(row_other,1,Knight(color))
        self.squares[row_other][6] = Square(row_other,6,Knight(color))

        #bishops

        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))


        #rooks

        self.squares[row_other][0] = Square(row_other,0,Rook(color))
        self.squares[row_other][7] = Square(row_other,7,Rook(color))

        #queens
        self.squares[row_other][3] = Square(row_other,3,Queen(color))


        #kings
        self.squares[row_other][4] = Square(row_other,4,King(color))
