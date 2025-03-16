# Gera Tabela Otimizada de Jogos de Campeonato Esportivo utilizando Algoritmo Genético

import pygame
from pygame.locals import *
import random
import itertools
from genetic_algorithm import mutate, order_crossover,  calculate_fitness, sort_population
from utils_tco import *
from draw_functions import draw_paths, draw_plot, draw_cities
import sys
import numpy as np
import pygame

# Define constant values
# pygame
WIDTH, HEIGHT = 800, 400
NODE_RADIUS = 10
FPS = 30
PLOT_X_OFFSET = 450

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


# Initialize problem

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


possible_games = generate_possible_games(teams)

# GA
N_TEAMS = len(teams)
POPULATION_SIZE = N_TEAMS * 10
N_GENERATIONS = None
MUTATION_PROBABILITY = 0.5
MUTATION_ITENSITY = 0.1

# Cria a População Inicial de Soluções ( TCO - Tabela de Campeonato Otimizado )
# Cada Solução é uma sequência de jogos ( Cromossomo ), onde cada jogo é representado por um código de 4 digítos ( Gene )
# Cada código de jogo contém o código da Equipe Mandante e da Visitante
# Portanto, os jogos de ida e de volta terão códigos distintos
population = generate_random_season_games(teams, POPULATION_SIZE)

best_fitness_values = []
best_solutions = []

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TCO Solver using Pygame")
clock = pygame.time.Clock()
generation_counter = itertools.count(start=1)  # Start the counter at 1

# Main game loop
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

    population_fitness = [calculate_fitness(individual, teams, matrix_distances, city_n_teams, teams_distance_traveled) for individual in population]

    population, population_fitness = sort_population(
        population,  population_fitness)

    best_fitness = calculate_fitness(population[0], teams, matrix_distances, city_n_teams, teams_distance_traveled)
    best_solution = population[0]

    best_fitness_values.append(best_fitness)
    best_solutions.append(best_solution)

    draw_plot(screen, list(range(len(best_fitness_values))),
              best_fitness_values, y_label="Fitness - Sum of Penalties (points)")

    # draw_cities(screen, cities_locations, RED, NODE_RADIUS)
    # draw_paths(screen, best_solution, BLUE, width=3)
    # draw_paths(screen, population[1], rgb_color=(128, 128, 128), width=1)

    print(f"Generation {generation}: Best fitness = {round(best_fitness, 2)}")

    new_population = [population[0]]  # Keep the best individual: ELITISM

    while len(new_population) < POPULATION_SIZE:

        # selection
        # simple selection based on first 10 best solutions
        # parent1, parent2 = random.choices(population[:10], k=2)

        # solution based on fitness probability
        probability = 1 / np.array(population_fitness)
        parent1, parent2 = random.choices(population, weights=probability, k=2)

        # child1 = order_crossover(parent1, parent2)
        child1 = order_crossover(parent1, parent1, possible_games)

        child1 = mutate(child1, MUTATION_PROBABILITY, MUTATION_ITENSITY, teams) 

        new_population.append(child1)

    population = new_population

    pygame.display.flip()
    clock.tick(FPS)


# save the best individual in a file if it is better than the one saved.
tco_file = "dados/Tabela_Brasileirao_2025_Serie_A_Otimizada.csv"
sep = ";"
encoding = "ISO-8859-1"
generate_tco_file(best_solution, tco_file, sep, encoding, teams)

print_list_games_by_round(best_solution, teams)

# exit software
pygame.quit()
sys.exit()