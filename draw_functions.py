
import pylab
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib
import pygame
from typing import List, Tuple
import random
from utils_tco import *

matplotlib.use("Agg")

def draw_plot(screen: pygame.Surface, x: list, y: list, x_label: str = 'Generation', y_label: str = 'Fitness') -> None:
    """
    Draw a plot on a Pygame screen using Matplotlib.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the plot on.
    - x (list): The x-axis values.
    - y (list): The y-axis values.
    - x_label (str): Label for the x-axis (default is 'Generation').
    - y_label (str): Label for the y-axis (default is 'Fitness').

    @author: SérgioPolimante
    """
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    ax.plot(x, y)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    plt.tight_layout()

    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    size = canvas.get_width_height()
    surf = pygame.image.fromstring(raw_data, size, "RGB")
    screen.blit(surf, (0, 0))
    
def draw_team_games(screen, season: list, teams:list, rgb_color: Tuple[int, int, int], title_rgb_color: Tuple[int, int, int], x_offset=450, y_offset=20, font_size=20):
    """
    Desenha a tabela dos jogos de um time escolhido aleatoriamente
    
    Parâmetros
        screen (pygame.Surface): Tela do pygame onde será desenhado o texto.
        season (list): Lista com os jogos codificados
        teams (list): Lista de Dicionários de Equipes
        rgb_color (tuple): Tupla com os valores da cor (rgb) a ser usada p/ imprimir os jogos devem ser impressos
        title_rgb_color (tuple): Tupla com os valores da cor (rgb) a ser usada p/ imprimir o título com o nome da Equipe que terá seus jogos mostrados
        x_offset: Posição X inicial para desenhar o texto.
        y_offset: Posição Y inicial para desenhar o texto.
        font_size: Tamanho da fonte utilizada para desenhar o texto.
    """
    pygame.draw.rect(screen, rgb_color, (( x_offset - 10), ( y_offset - 10 ), 350, 420), 2) 

    team = random.choice(teams)
    team_code = team["Codigo"]
    team_name = get_team_name(team)

    font = pygame.font.SysFont(None, font_size)  # Define a fonte
    
    # Exibir título
    title_text = f"Tabela do {team_name}"
    title_surface = font.render(title_text, True, title_rgb_color)
    screen.blit(title_surface, ((x_offset+50), y_offset))
    y_offset += font_size + 5  # Espaçamento após o título

    # Iterar sobre os jogos do time e desenhá-los na tela
    for i, current_round in enumerate(season, start=1):
        for j in range(0, len(current_round), 4):
            team1_code = current_round[j:j+2]
            team2_code = current_round[j+2:j+4]
            if ( team1_code == team_code ) or ( team2_code == team_code ):
                if team1_code == team_code:
                    team2 = search_team_by_code(teams, team2_code)
                    text_game =  team_name + " x " + get_team_name(team2)
                else:
                    team1 = search_team_by_code(teams, team1_code)
                    text_game =  get_team_name(team1) + " x " + team_name
                text_round = f"Rodada {i}: {text_game}"
                text_surface = font.render(text_round, True, rgb_color)
                screen.blit(text_surface, (x_offset, y_offset))
                y_offset += font_size  # Espaçamento entre as linhas
                break
