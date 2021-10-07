import numpy as np
import random
import pygame
import sys
import math
import os
#--------- Colores ---------#
BLACK = (0,0,0)
WHITE = (255,255,255)
WHITEBLACK = (230,230,230)
GREY = (200,200,200)
GREEN = (0,255,0)
RED = (170,17,0)
BLUE = (0,0,255)
PINK = (255, 160, 132)
PINKBLACK = (219, 137, 113)
OTHERBLUE = (63, 94, 199)
#--------- Tamaño de juego y modo ---------#
ROW = 6
COLUMN = 7
CONNECT = 4
EMPTY = 0
PLAYER = 0
AI = 1
PLAYER_PIECE = 1
AI_PIECE = 2
BUTTON_HEIGHT = 30
BUTTON_WIDTH = 100
#--------- Funciones ---------#
def create_board():
  board = np.zeros((ROW,COLUMN))
  return board

def drop_piece(board, row, col, piece):
  board[row][col] = piece

def is_valid_location(board, col):
  return board[ROW-1][col] == 0

def get_next_open_row(board, col):
  for r in range(ROW):
    if board[r][col] == 0:
      return r

def print_board(board):
  print(np.flip(board,0))

def horizontal_col():
  col = COLUMN - 3
  return col

def vertical_row():
  row = ROW-3
  return row

def winning_move(board, piece):
  #check horizontal locations for win
  for c in range (horizontal_col()):
    for r in range(ROW):
      if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
        return True
  #check vertical locations for win
  for c in range (COLUMN):
    for r in range(vertical_row()):
      if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
        return True

  #check positively sloped diaganols
  for c in range (horizontal_col()):
    for r in range(vertical_row()):
      if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
        return True

  #check negatively sloped diaganols
  for c in range (horizontal_col()):
    for r in range(3, ROW):
      if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
        return True

def evaluate_window(window, piece):
  score = 0
  opp_piece = PLAYER_PIECE
  if piece == PLAYER_PIECE:
    opp_piece = AI_PIECE
  
  if window.count(piece) == 4:
    score += 100
  elif window.count(piece) == 3 and window.count(EMPTY) == 1:
    score += 5
  elif window.count(piece) == 2 and window.count(EMPTY) == 2:
    score += 2
  if window.count(opp_piece == 3 and window.count(EMPTY)) ==1:
    score -= 4
  return score

def score_position(board, piece):
  score = 0  
  #Score center column
  center_array = [int(i) for i in list(board[:, COLUMN//2])]
  center_count = center_array.count(piece)
  score += center_count * 3
  # Score horizontal
  for r in range(ROW):
    row_array = [int(i) for i in list(board[r,:])]
    for c in range (COLUMN-3):
      window = row_array[c:c+CONNECT]
      score += evaluate_window(window, piece)
  # Score vertical
  for c in range(COLUMN):
    col_array = [int(i) for i in list(board[:,c])]
    for r in range(ROW-3):
      window = col_array[r:r+CONNECT]
      score += evaluate_window(window, piece)

  # Score Diagonal positive
  for r in range(ROW-3):
    for c in range(COLUMN-3):
      window = [board[r+i][c+i] for i in range(CONNECT)]
      score += evaluate_window(window, piece)

  for r in range(ROW-3):
    for c in range(COLUMN-3):
      window = [board[r+3-i][c+i] for i in range(CONNECT)]
      score += evaluate_window(window, piece)

  return score

def is_terminal_node(board):
  return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
  valid_locations = get_valid_locations(board)
  is_terminal = is_terminal_node(board)
  if depth == 0 or is_terminal:
    if is_terminal:
      if winning_move(board, AI_PIECE):
        return (None, 10000000000)
      elif winning_move(board, PLAYER_PIECE):
        return (None, -10000000000)
      else: #Game is over, no more valid moves
        return (None, 0)
    else: #Depth is zero
      return (None, score_position(board, AI_PIECE))
  if maximizingPlayer:
    value = -math.inf
    column = random.choice(valid_locations)
    for col in valid_locations:
      row = get_next_open_row(board,col)
      b_copy = board.copy()
      drop_piece(b_copy, row, col, AI_PIECE)
      new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
      if new_score > value:
        value = new_score
        column = col
      alpha = max(alpha, value)
      if alpha >= beta:
        break
    return column, value
  else:#minimazingPlayer
    value = math.inf
    column = random.choice(valid_locations)
    for col in valid_locations:
      row = get_next_open_row(board, col)
      b_copy = board.copy()
      drop_piece(b_copy, row, col, PLAYER_PIECE)
      new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
      if new_score < value:
        value = new_score
        column = col
      beta = min(beta, value)
      if alpha >= beta:
        break
    return column, value

def get_valid_locations(board):
  valid_locations = []
  for col in range(COLUMN):
    if is_valid_location(board, col):
      valid_locations.append(col)
  return valid_locations

def pick_best_move(board, piece):
  valid_locations = get_valid_locations(board)
  best_score = -100000
  best_col = random.choice(valid_locations)
  for col in valid_locations:
    row = get_next_open_row(board, col)
    temp_board = board.copy()
    drop_piece(temp_board, row, col, piece)
    score = score_position(temp_board, piece)
    if score > best_score:
      best_score = score
      best_col = col
  return best_col

def draw_text(surface,text,size,x,y,color):
  font = pygame.font.Font('./assets/VT323-Regular.ttf', size)
  text_surface = font.render(text, True, color)
  text_rect = text_surface.get_rect()
  text_rect.midtop = (x,y)
  surface.blit(text_surface, text_rect)
  icon = pygame.image.load("./assets/favicon.ico")
  pygame.display.set_icon(icon)

def draw_board(board):
  for c in range(COLUMN):
    for r in range(ROW):
      pygame.draw.rect(screen, OTHERBLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE , SQUARESIZE, SQUARESIZE), width=0)
      pygame.draw.circle(screen, GREY,(int(c*SQUARESIZE+SQUARESIZE/2-5), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS, width=0)
      pygame.draw.circle(screen, BLACK,(int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS, width=0)


  for c in range(COLUMN):
    for r in range(ROW):
      if board[r][c] == PLAYER_PIECE:
        pygame.draw.circle(screen, WHITE,(int(c*SQUARESIZE+SQUARESIZE/2), height - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS, width=0)
        pygame.draw.circle(screen, WHITEBLACK,(int(c*SQUARESIZE+SQUARESIZE/2), height - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS - 10, width=0)
        pygame.draw.circle(screen, WHITE,(int(c*SQUARESIZE+SQUARESIZE/2), height - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS -15, width=1)

      elif board[r][c] == AI_PIECE:
        pygame.draw.circle(screen, PINK,(int(c*SQUARESIZE+SQUARESIZE/2), height - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS, width=0)
        pygame.draw.circle(screen, PINKBLACK,(int(c*SQUARESIZE+SQUARESIZE/2), height - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS - 10, width=0)
        pygame.draw.circle(screen, PINK,(int(c*SQUARESIZE+SQUARESIZE/2), height - int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS - 15, width=1)

  pygame.display.update()

def show_go_screen():
  while True:
    screen.fill(BLACK)
    draw_text(screen, "oooo | Conecta 4 | oooo", 65, width // 2, height // 8, RED)
    draw_text(screen, "Instrucciones:", 37, width // 2, height // 3, PINK )
    draw_text(screen, "Concatena las fichas en diagonal,", 27, width // 2, height //2 - 30, PINK)
    draw_text(screen, "vertical u horizontal.", 27, width // 2, height // 2, PINK)
    draw_text(screen, "Moves tu ficha con el mouse y bajas con click.", 27, width // 2, height // 2 +30, PINK)
    draw_text(screen, "Elegí una de las tres opciones de abajo", 27, width // 2, height // 2 +60, PINK)
    """ draw_text(screen, "Click para jugar (ta dificil eh)", 40, width // 2, height * 3/4, WHITE) """
    draw_text(screen, "Creado por LucasDev - 2021", 20, width // 2, height - 65, RED)
    draw_text(screen, "Musica por Cumbiomaniaco", 20, width // 2, height - 45, RED)

    mx, my = pygame.mouse.get_pos()
    button_p_vs_p = pygame.Rect(width // 6 - BUTTON_WIDTH // 2, height * 3/4, BUTTON_WIDTH, BUTTON_HEIGHT)
    button_p_vs_ai = pygame.Rect(width // 2 - BUTTON_WIDTH // 2, height * 3/4, BUTTON_WIDTH, BUTTON_HEIGHT)
    button_ai_vs_ai = pygame.Rect(width - width // 6 - BUTTON_WIDTH // 2, height * 3/4, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, OTHERBLUE, button_p_vs_p)
    pygame.draw.rect(screen, RED, button_p_vs_ai)
    pygame.draw.rect(screen, PINK, button_ai_vs_ai)
    draw_text(screen, "J vs J", 30, width // 6, height * 3/4, WHITE)
    draw_text(screen, "J vs IA", 30, width // 2, height * 3/4, WHITE)
    draw_text(screen, "IA vs IA", 30, width - width // 6, height * 3/4, BLACK)
    if button_p_vs_p.collidepoint((mx, my)):
      pygame.draw.rect(screen, WHITEBLACK, button_p_vs_p)
      draw_text(screen, "J vs J", 30, width // 6, height * 3/4, BLACK)
      if click == True:
        p_vs_p()
    if button_p_vs_ai.collidepoint((mx, my)):
      pygame.draw.rect(screen, WHITEBLACK, button_p_vs_ai)
      draw_text(screen, "J vs IA", 30, width // 2, height * 3/4, BLACK)
      if click == True:
        p_vs_ai()
    if button_ai_vs_ai.collidepoint((mx, my)):
      pygame.draw.rect(screen, WHITEBLACK, button_ai_vs_ai)
      draw_text(screen, "IA vs IA", 30, width - width // 6, height * 3/4, BLACK)
      if click == True:
        ai_vs_ai()


    click = False
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          pygame.quit()
          sys.exit()
      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
          click = True
    pygame.display.update()

def restart_board():
  board = np.zeros((ROW,COLUMN))
  return board

def ia_wins(ran):
  random.shuffle(ran)
  return ran[0]
#--------- Pygame ---------#
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Cuatro en linea - @LucasDev")

SQUARESIZE = 100
RADIUS = SQUARESIZE / 2 - 10
width = COLUMN * SQUARESIZE
height = (ROW + 1) * SQUARESIZE
size = (width, height)

screen = pygame.display.set_mode(size)
""" draw_board(board) #Dibujo del campo de juego tipo pygame
pygame.display.update()  """
pygame.mouse.set_visible(1) #No se ve la fecha del mouse - 0 y 1
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, './assets/VT323-Regular.ttf')
myfont = pygame.font.Font(filename, 40) #Definir fuente
pygame.mixer.music.load("./assets/cumbiamusic.wav")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(loops=-1)
click = False

#--------- Bucle principal ---------#
def p_vs_p():

  running = True
  board = create_board() #llama a la función que crea el tablero
  print_board(board) #Hace un print por consola del board
  turn = random.randint(PLAYER, AI) #Comienzo aleatorio
  draw_board(board) #Dibujo del campo de juego tipo pygame
  while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          running = False
      if event.type == pygame.MOUSEMOTION:
        pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE), width=0)
        posx = event.pos[0]
        if turn == PLAYER:
          pygame.draw.circle(screen, WHITE, (posx, int(SQUARESIZE/2)), RADIUS)
          pygame.draw.circle(screen, WHITEBLACK, (posx, int(SQUARESIZE/2)), RADIUS-10)
          pygame.draw.circle(screen, WHITE, (posx, int(SQUARESIZE/2)), RADIUS-15, width=1)
        if turn == AI:
          pygame.draw.circle(screen, PINK, (posx, int(SQUARESIZE/2)), RADIUS)
          pygame.draw.circle(screen, PINKBLACK, (posx, int(SQUARESIZE/2)), RADIUS-10)
          pygame.draw.circle(screen, PINK,(posx, int(SQUARESIZE/2)), RADIUS-15, width=1)
      pygame.display.update()

      if event.type == pygame.MOUSEBUTTONDOWN:
        pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
        #PLAYER MOVE
        if turn == PLAYER:
          posx = event.pos[0]
          col = int(math.floor(posx/SQUARESIZE))

          if is_valid_location(board, col):
            row = get_next_open_row(board,col)
            drop_piece(board, row, col, PLAYER_PIECE)

            if winning_move(board, PLAYER_PIECE):
              label = myfont.render('Gano lx jugadorx 1!', True, WHITE)
              text_rect = label.get_rect()
              text_rect.midtop = (width//2, 20)
              screen.blit(label, text_rect)
              running = False

        #P2 MOVE
        else:
          posx = event.pos[0]
          col = int(math.floor(posx/SQUARESIZE))
            
          if is_valid_location(board, col):
            row = get_next_open_row(board,col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
              label = myfont.render('Gano lx jugadorx 2!', True, PINK)
              text_rect = label.get_rect()
              text_rect.midtop = (width//2, 20)
              screen.blit(label, text_rect)
              running = False

        print_board(board)
        draw_board(board)
        pygame.display.update()
        turn += 1
        turn = turn % 2
        if not running:
          pygame.time.wait(5000)

def p_vs_ai():
  running = True
  board = create_board() #llama a la función que crea el tablero
  draw_board(board) #Dibujo del campo de juego tipo pygame
  print_board(board) #Hace un print por consola del board
  turn = random.randint(PLAYER, AI) #Comienzo aleatorio
  while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          running = False
      if event.type == pygame.MOUSEMOTION:
        pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE), width=0)
        posx = event.pos[0]
        if turn == PLAYER:
          pygame.draw.circle(screen, WHITE, (posx, int(SQUARESIZE/2)), RADIUS)
          pygame.draw.circle(screen, WHITEBLACK, (posx, int(SQUARESIZE/2)), RADIUS-10)
          pygame.draw.circle(screen, WHITE, (posx, int(SQUARESIZE/2)), RADIUS-15, width=1)
      pygame.display.update()

      if event.type == pygame.MOUSEBUTTONDOWN:
        pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
        #PLAYER MOVE
        if turn == PLAYER:
          posx = event.pos[0]
          col = int(math.floor(posx/SQUARESIZE))

          if is_valid_location(board, col):
            row = get_next_open_row(board,col)
            drop_piece(board, row, col, PLAYER_PIECE)

            if winning_move(board, PLAYER_PIECE):
              label = myfont.render('Lograste imposible o_o', True, WHITE)
              text_rect = label.get_rect()
              text_rect.midtop = (width//2, 20)
              screen.blit(label, text_rect)
              running = False
            turn += 1
            turn = turn % 2
            print_board(board)
            draw_board(board)
    #AI MOVE
    if turn == AI and running:
      #col = random.randint(0, COLUMN-1)
      #col = pick_best_move(board, AI_PIECE)
      col, minimax_score = minimax(board, 5, -math.inf, math.inf, True) #más grande el numero, más pasos adelante esta
      if is_valid_location(board, col):
        """ pygame.time.wait(500) """
        row = get_next_open_row(board,col)
        drop_piece(board, row, col, AI_PIECE)

        if winning_move(board, AI_PIECE):
          label = myfont.render(ia_wins(["Vite' como somo la pc", "Ya gane?", "Ni la viste venir eh", "Suerte la prox", "Perdón, solo sé ganar", "Fui creado por LucasDev, que quere"]), True, PINK)
          text_rect = label.get_rect()
          text_rect.midtop = (width//2, 20)
          screen.blit(label, text_rect)
          running = False

        print_board(board)
        draw_board(board)
        pygame.display.update()
        turn += 1
        turn = turn % 2
    if not running:
      pygame.time.wait(5000)

def ai_vs_ai():
  running = True
  board = create_board() #llama a la función que crea el tablero
  draw_board(board) #Dibujo del campo de juego tipo pygame
  print_board(board) #Hace un print por consola del board
  turn = random.randint(PLAYER, AI) #Comienzo aleatorio
  while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          running = False
    if turn == PLAYER and running:
      col = random.randint(0, COLUMN-1)
      #col = pick_best_move(board, PLAYER_PIECE)
      #col, minimax_score = minimax(board, 4, -math.inf, math.inf, True) #más grande el numero, más pasos adelante esta
      if is_valid_location(board, col):
        pygame.time.wait(700)
        row = get_next_open_row(board,col)
        drop_piece(board, row, col, PLAYER_PIECE)

        if winning_move(board, PLAYER_PIECE):
          label = myfont.render(ia_wins(["Bien jugado maquina", "AI vs AI, quien diria", "Si gano yo, gano yo tambien"]), True, WHITE)
          text_rect = label.get_rect()
          text_rect.midtop = (width//2, 20)
          screen.blit(label, text_rect)
          running = False
        
        print_board(board)
        draw_board(board)
      turn += 1
      turn = turn % 2
    if turn == AI and running:
      col = random.randint(0, COLUMN-1)
      #col = pick_best_move(board, AI_PIECE)
      #col, minimax_score = minimax(board, 4, -math.inf, math.inf, True) #más grande el numero, más pasos adelante esta
      if is_valid_location(board, col):
        pygame.time.wait(700)
        row = get_next_open_row(board,col)
        drop_piece(board, row, col, AI_PIECE)

        if winning_move(board, AI_PIECE):
          label = myfont.render(ia_wins(["Bien jugado maquina", "AI vs AI, quien diria", "Si gano yo, gano yo tambien"]), True, PINK)
          text_rect = label.get_rect()
          text_rect.midtop = (width//2, 20)
          screen.blit(label, text_rect)
          running = False
        
        print_board(board)
        draw_board(board)
        pygame.display.update()

      turn += 1
      turn = turn % 2
    if not running:
      pygame.time.wait(5000)

show_go_screen()