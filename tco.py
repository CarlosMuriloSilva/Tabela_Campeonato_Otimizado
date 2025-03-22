# Gera Tabela Otimizada de Jogos de Campeonato Esportivo utilizando Algoritmo Genético

import pygame
from pygame.locals import *
import random
import itertools
from genetic_algorithm import mutate, order_crossover,  calculate_fitness, sort_population
from utils_tco import *
from draw_functions import draw_plot, draw_team_games
import sys
import numpy as np

# Define os valores das constantes
# pygame
WIDTH, HEIGHT = 800, 450
FPS = 30

# Define as cores a serem usada no pygam
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Inicializa o problema

# Lê o arquivo como os dados das Equipes Participantes do Campeonato Esportivo e gera uma lista de dicionários
arq = "dados/Times_Brasileirao_2025_Serie_A.csv"
sep = ";"
encoding = "ISO-8859-1"
teams = generate_teams_list_by_file(arq, sep, encoding)

# Gera uma Matriz com os deslocamentos necessários p/ a realização de cada jogo ( distância entre as cidades sede das Equipes envolvidas no jogo)
matrix_distances = generate_matrix_distances(teams)

# Somatório das distâncias a serem percorridas por cada Equipe ( pois toda Equipe irá visitar as outras uma vez )
# Levando em conta apenas a viagem de ida
# sum_total_distance = np.sum(matrix_distances)
# print(f"Soma Total de Deslocamentos: {sum_total_distance:.2f} km\n")

# Gera uma Lista com o Código de cada Equipe e o respectivo valor total dos deslocamentos em Km desta Equipe como Visitante durante o Campeonato
teams_distance_traveled = generate_teams_distance_traveled(matrix_distances)

# Gera uma lista com o nome de cada Cidade e o nº de equipes participantes do Campeonato sediadas nela
city_n_teams = generate_city_n_teams(teams)

# Gera uma lista com os códigos de todos os possíveis jogos
possible_games = generate_possible_games(teams)

# Constantes do Algoritmo Genético
N_TEAMS = len(teams)
POPULATION_SIZE = N_TEAMS * 20
N_GENERATIONS = None
N_MAX_GENERATIONS = 2000
MUTATION_PROBABILITY = 0.5
MUTATION_ITENSITY = 0.1

# Cria a População Inicial de Soluções ( TCO - Tabela de Campeonato Otimizado )
# Cada Solução é uma sequência de jogos ( Cromossomo ), onde cada jogo é representado por um código de 4 digítos ( Gene )
# Cada código de jogo contém o código da Equipe Mandante e da Visitante
# Portanto, os jogos de ida e de volta terão códigos distintos
population = generate_random_season_games(teams, POPULATION_SIZE)

best_fitness_values = []
best_solutions = []

# Inicializa o Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TCO Solver using Pygame")
clock = pygame.time.Clock()
generation_counter = itertools.count(start=1)  # Start the counter at 1

# Loop principal 
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    generation = next(generation_counter)

    screen.fill(WHITE)

    # Gera um Lista com o fitness (aptidão) de cada individuo 
    population_fitness = [calculate_fitness(individual, teams, matrix_distances, city_n_teams, teams_distance_traveled) for individual in population]

    # Ordena a população de acordo com a sua aptidão (fitness)
    population, population_fitness = sort_population(
        population,  population_fitness)

    # Calcula o fitness (aptidão) do melhor individuo (Tabela com o menor número de penalidades)
    best_fitness = calculate_fitness(population[0], teams, matrix_distances, city_n_teams, teams_distance_traveled)
    best_solution = population[0]

    # Armazena a melhor solução e seu respectivo fitness em listas distintas
    best_fitness_values.append(best_fitness)
    best_solutions.append(best_solution)

    # Mostra o gráfico com a evolução do valor de fitness da melhor solução X o nº da geração
    draw_plot(screen, list(range(len(best_fitness_values))),
              best_fitness_values, y_label="Fitness - Sum of Penalties (points)")
    
    # Mostra a sequência de jogos um dos times (escolhido aleatoriamente) extraída da Tabela da melhor solução encontrada na respectiva geração
    draw_team_games(screen, best_solution, teams, BLACK, BLUE)

    print(f"Generation {generation}: Best fitness = {round(best_fitness, 2)}")

    if generation == N_MAX_GENERATIONS:
        break

    # Mantém na nova população a melhor solução encontrada na geração atual (Elitismo)
    new_population = [population[0]]

    while len(new_population) < POPULATION_SIZE:

        # seleção baseada na probabilidade de aptidão, isto é, individuos melhores adaptados (fitness menor) tem maior chance de serem escolhidos
        probability = 1 / np.array(population_fitness)
        parent1, parent2 = random.choices(population, weights=probability, k=2)

        # cria novo individuo à partir do cruzamento dos 2 indivíduos escolhidos anteriormente
        child1 = order_crossover(parent1, parent2, possible_games)

        # realiza ou não mutação no novo individuo
        child1 = mutate(child1, MUTATION_PROBABILITY, MUTATION_ITENSITY, teams) 

        new_population.append(child1)

    population = new_population

    pygame.display.flip()
    clock.tick(FPS)

# grava a melhor solução encontrada em um arquivo
tco_file = "dados/Tabela_Brasileirao_2025_Serie_A_Otimizada.csv"
sep = ";"
encoding = "ISO-8859-1"
generate_tco_file(best_solution, tco_file, sep, encoding, teams)

# mostra os jogos da melhor solução encontrada no terminal
print_list_games_by_round(best_solution, teams)

# exit software
pygame.quit()
sys.exit()