# Calcula a aptidão da Tabela oficial do 1º turno do Campeonato Brasileiro de 2025 da série A
# Este valor será usado como referência para avaliar os resultados alcançados pelo Algoritimo Genético

from utils_tco import *
from genetic_algorithm import *

arq = "dados/Times_Brasileirao_2025_Serie_A.csv"
sep = ";"
encoding = "ISO-8859-1"
teams = generate_teams_list_by_file(arq, sep, encoding)

matrix_distances = generate_matrix_distances(teams)

teams_distance_traveled = generate_teams_distance_traveled(matrix_distances)

print("\nCálculo das Distâncias das viagens apenas de ida por Equipe:\n")
for team_code, distance in teams_distance_traveled.items():
    team = search_team_by_code(teams, team_code)
    print(f"Equipe {team_code} - {get_team_name(team)} : {distance} km percorridos")
print("\n")

city_n_teams = generate_city_n_teams(teams)

arq_tabela_brasileirao_2025 = "dados/Tabela_Brasileirao_2025_Serie_A.csv"
sep = ";"
encoding = "ISO-8859-1"
tb2025 = generate_season_table_by_file(arq_tabela_brasileirao_2025, sep, encoding, teams)
print("Codificação da Tabela da CBF - Brasileirão 2025 Série A - 1º Turno :\n")
print(tb2025)
print()
tb2025_fitness = calculate_fitness(tb2025, teams, matrix_distances, city_n_teams, teams_distance_traveled)
print(f"Fitness - Tabela da CBF - Brasileirão 2025 Série A - 1º Turno : {tb2025_fitness:.2f}")