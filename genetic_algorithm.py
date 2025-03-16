# Description: This file contains the implementation of the genetic algorithm for the football scheduling problem.

import random
from typing import List, Tuple
from utils_tco import *

def calculate_fitness(season: list, teams: list, matrix_distances: list, city_n_teams: list, teams_distance_traveled: list) -> float:
    """
    Calcula a aptidão da solução ( Tabela de 1 turno do Campeonato )
    O Cálculo é feito através da soma de penalidades que contrariam critérios que definem a confecção de uma Tabela Idealizada
    Quanto menor for soma, mais apta é a solução

    Parâmetros:
        season (list): Lista com os jogos codificados
        teams (list): Lista de Dicionários de Equipes
        matrix_distances (list): Matriz com os deslocamentos necessários p/ a realização de cada jogo entre as equipes participantes do Campeonato
        city_n_teams (list): Lista contendo a Cidade e a respectiva quantidade de Equipes desta Cidade que participam do Campeonato
        teams_distance_traveled - Lista com o Código de cada Equipe e o respectivo valor total dos deslocamentos em Km desta Equipe como Visitante durante o Campeonato

    Retorna:
        float: Total de penalidades 
    """
    fitness = 0
    n_rounds = len(season)
    n_teams = len(teams)

    home = [''] * n_teams
    last_opponent = [''] * n_teams

    teams_season_distance_traveled = {f"{i:02}": 0 for i in range(1, (n_teams+1))}
    
    for n_round in range(n_rounds):
        city_round_n_games = city_n_teams.copy()
        for city in city_round_n_games:
            city['JogosRodada'] = 0
        round_games = generate_list_games(season[n_round], 4)
        for game in round_games:
            team1_code = game[:2]
            team2_code = game[2:]
            team1 = search_team_by_code(teams, team1_code)
            team2 = search_team_by_code(teams, team2_code)
            team1_city = get_team_city(team1)
            team2_city = get_team_city(team2)
            team1_index = int(team1_code) - 1
            team2_index = int(team2_code) - 1
            distance = matrix_distances[team2_index, team1_index]
            teams_season_distance_traveled[team2_code] += distance
            team1_last_home = home[team1_index]
            team1_last_opponent = last_opponent[team1_index]
            team2_last_home = home[team2_index]
            team2_last_opponent = last_opponent[team2_index]
            fitness += calculate_penalty_last_home(team1_last_home, team2_last_home)
            fitness += calculate_penalty_last_opponent(teams, team1_city, team1_last_opponent, team2_city, team2_last_opponent)
            fitness += calculate_penalty_ideal_city_round_n_games(team1_city, city_round_n_games)
            home[team1_index] = 1
            home[team2_index] = 0
            last_opponent[team1_index] = team2_code
            last_opponent[team2_index] = team1_code
    
    fitness += calculate_penalty_balanced_travel(teams_distance_traveled, teams_season_distance_traveled)

    return fitness

def order_crossover(parent1: List[str], parent2: List[str], possible_games: List[str]) -> List[str]:
    """
    Perform order crossover (OX) between two parent sequences to create a child sequence.

    Parameters:
    - parent1 (List[str]): The first parent sequence.
    - parent2 (List[str]): The second parent sequence.
    - possible_games (List[str]): The list of possible games.

    Returns:
    List[str]: The child sequence resulting from the order crossover.
    """
    
    parent1_seq_games = "" 
    for current_round in parent1:
        parent1_seq_games += current_round
    parent2_seq_games = "" 
    for current_round in parent2:
        parent2_seq_games += current_round
    child_seq_games = parent1_seq_games
    round_size = len(parent1[0])

    n_games_half_season = len(possible_games) // 2 # Nº de jogos por turno
    n_games_parent = n_games_half_season // 2 # Nº máximo de jogos a terem o mando de campo trocado entre os pais
    n_changes = 0

    remaining_games = possible_games.copy()

    for _ in range(n_games_half_season):

        n_remaining_games = len(remaining_games)
        if n_remaining_games == 0:
            break

        game = remaining_games[random.randint(0, ( n_remaining_games - 1))]
        team1_code = game[:2]
        team2_code = game[2:]
        game_inv = team2_code + team1_code

        if game_inserted(parent1_seq_games, game):
            old_game = game
        else:
            old_game = game_inv

        if game_inserted(parent2_seq_games, game):
            new_game = game
        else:
            new_game = game_inv

        if new_game != old_game:
            child_seq_games = change_game(child_seq_games, old_game, new_game)
            n_changes += 1
            if n_changes == n_games_parent:
                break


        remove_game(remaining_games, game)
        remove_game(remaining_games, game_inv)

    child = generate_list_games(child_seq_games, round_size)

    return child

def mutate(solution:  List[str], mutation_probability: float, mutation_intensity: float, teams: List[dict]) ->  List[str]:
    """
    Mutate a solution by inverting a segment of the sequence with a given mutation probability.

    Parameters:
    - solution (List[str]): The solution sequence to be mutated.
    - mutation_probability (float): The probability of mutation for each individual in the solution.
    - mutation_intensity (float): The intensity of the mutation for each individual in the solution.

    Returns:
    List[str]: The mutated solution sequence.
    """
    mutated_solution = solution.copy()
    n_changes = 0

    # Check if mutation should occur    
    if random.random() < mutation_probability:
        return mutated_solution
    
    n_round1 = random.randint(0, (len(mutated_solution) - 1))
    n_round2 = ""
    while n_round2 != n_round1:
        n_round2 = random.randint(0, (len(mutated_solution) - 1))
    round1 = mutated_solution[n_round1]
    round2 = mutated_solution[n_round2]
    mutated_solution[n_round1] = round2
    mutated_solution[n_round2] = round1

    teams_code = [team["Codigo"] for team in teams]
    n_mutations = int(len(teams_code) * mutation_intensity) 
    remaining_teams = teams_code.copy()

    for _ in range(n_mutations):
        team_code = remaining_teams[random.randint(0, (len(remaining_teams) - 1))]
        home = random.randint(0, 1)
        for n_round in range(len(mutated_solution)):

            current_round = mutated_solution[n_round]
            list_games = generate_list_games(current_round, 4)

            for n_game in range(len(list_games)):

                game = list_games[n_game]
                team1_code = game[:2]
                team2_code = game[2:]

                if  ( team1_code != team_code ) and ( team2_code != team_code ):
                    continue

                if ( team1_code not in remaining_teams ) or ( team2_code not in remaining_teams ):
                    if  ( team1_code == team_code ):
                        home = 1
                    else:
                        home = 0                    
                    continue

                new_game = game
                if ( team1_code == team_code ):
                    if home == 1:
                        home = 0
                    else:
                        new_game = team2_code + team1_code 
                        home = 1

                if ( team2_code == team_code ):
                    if home == 1:
                        new_game = team2_code + team1_code
                        home = 0
                    else:
                        home = 1
                if new_game != game:
                    list_games[n_game] = new_game
                    # n_changes += 1
                    # print("Mutação: ", game, " -> ", new_game)
                break

            mutated_solution[n_round] = "".join(list_games)

        remaining_teams.remove(team_code)

    # print("Mutations: ", n_changes)

    return mutated_solution

def sort_population(population: List[List[str]], fitness: List[float]) -> Tuple[List[List[str]], List[float]]:
    """
    Sort a population based on fitness values.

    Parameters:
    - population (List[List[str]]): The population of solutions, where each solution is represented as a list.
    - fitness (List[float]): The corresponding fitness values for each solution in the population.

    Returns:
    Tuple[List[List[str]], List[float]]: A tuple containing the sorted population and corresponding sorted fitness values.
    """
    # Combine lists into pairs
    combined_lists = list(zip(population, fitness))

    # Sort based on the values of the fitness list
    sorted_combined_lists = sorted(combined_lists, key=lambda x: x[1])

    # Separate the sorted pairs back into individual lists
    sorted_population, sorted_fitness = zip(*sorted_combined_lists)

    return sorted_population, sorted_fitness
    


