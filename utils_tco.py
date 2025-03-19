# Criação de Listas a serem usadas na aplicação
# Funções de Cálculo e Manipulação de Dados

import pandas as pd
import numpy as np
import math
import random
import re
from collections import Counter

def generate_teams_list_by_file(arq: str, sep: str, encoding: str):
    """
    Lê um arquivo em formato .csv e cria uma Lista de Dicionários contendo dados de cada equipe do Campeonato
    Campos obrigatórios que devem constar no Arquivo:
      Codigo - Contendo até 2 digítos numéricos )
      Cidade - Nome da Cidade sede do team)
      Latitude - Latitude de Localização da Cidade)
      Longitude - Longitude de Localização da Cidade)

    Parâmetros:
        arq - path do Arquivo
        delimitador - Caractere utilizado para separar as colunas do Arquivo .csv
        encoding - Encoding do arquivo 

    Retorna:
        Lista de dicionário de dados referentes as equipes participantes do Campeonato
    """

    # Ler o arquivo CSV
    df = pd.read_csv(arq, sep=";", encoding="ISO-8859-1", dtype={"Codigo": str})

    # Converter para uma lista de dicionários
    teams = df.to_dict(orient="records")
    return teams

def generate_matrix_distances(teams: list):
    '''
    Gera uma Matriz com os deslocamentos necessários p/ a realização de cada jogo 
    Deslocamento calculado pela distância entre as cidades sede das Equipes envolvidas no jogo

    Parâmetros:
        teams - Lista com os dados das Equipes participantes do Campeonato

    Retorna:
        Matriz com os deslocamentos necessários p/ a realização de cada jogo entre as equipes participantes do Campeonato
    '''
    
    # Criar matriz ( n x n )
    n = len(teams)
    matrix_distances = np.zeros((20, 20))
    
    # Preencher a matriz com distâncias entre cidades
    for i in range(n):
        for j in range(n):
            # Coordenadas das cidades
            city1 = (teams[i]['Latitude'], teams[i]['Longitude'])
            city2 = (teams[j]['Latitude'], teams[j]['Longitude'])

            # Calcular distância
            distance = calculate_distance(city1, city2)

            matrix_distances[i, j] = distance

    return matrix_distances
    
def generate_teams_distance_traveled(matrix_distances: list):
    '''
    Gera uma Lista com o total dos deslocamentos em Km que cada Equipe terá que fazer durante o Campeonato

    Parâmetros:
        matrix_distances - Matriz com os deslocamentos necessários p/ a realização de cada jogo entre as equipes participantes do Campeonato

    Retorna:
        Lista com o Código de cada Equipe e respectivo valor total dos deslocamentos em Km
    '''

    n_teams = len(matrix_distances)

    # Inicializa um dicionário para armazenar a distância percorrida por cada equipe
    teams_distance_traveled = {f"{i:02}": 0 for i in range(1, (n_teams+1))}

    # Calcular a distância percorrida por cada equipe nos jogos fora de casa
    for team in range(n_teams):
        for opponent in range(n_teams):
            if team != opponent:
                # Convertendo índice numérico para string de dois dígitos
                team_key = f"{team+1:02}"
                # Somando a distância percorrida como visitante
                teams_distance_traveled[team_key] += matrix_distances[team][opponent]

    return teams_distance_traveled


def generate_city_n_teams(teams: list):
    """
    Gera uma Lista contendo a Cidade e a respectiva quantidade de Equipes desta Cidade que participam do Campeonato
    
    Parâmetros:
        teams (list): Lista de Dicionários de Equipes

    Retorna:
        Lista com o Nome da Cidade e a quantidade de Equipes sediadas neste cidade que participam do Campeonato
    """

    # Criar uma contagem das cidades
    counter_n_cities = Counter(team['Cidade do Time'] for team in teams)
    
    # Converter para lista de dicionários
    city_n_teams = [{'Cidade': city, 'QtdTimes': city_n_teams} for city, city_n_teams in counter_n_cities.items()]
    
    return city_n_teams

def generate_season_games(teams: list):
    '''
    Gera os jogos de um turno do Campeonato, com cada time jogando contra todos os outros uma vez.
    A função embaralha os times e os jogos para gerar uma tabela diferente a cada execução.
    Utiliza-se o algoritmo Round-robin para distribuir os jogos em rodadas.
    O Round Robin funciona rotacionando os times a cada rodada, garantindo que todos joguem contra todos sem repetição na mesma rodada.
    
    Parâmetros:
        teams (list): Lista de Dicionários de Equipes

    Retorna:
        Lista dividida em rodadas, sendo cada rodada um string contendo os jogos
        Cada Rodada é representada por uma sequência de jogos, e cada jogo um sub-string de 4 digitos
        Sendo os 2 primeiros digitos o Código da Equipe Mandante e os 2 últimos o Código da Equipe Visitante
    '''
    
    n_teams = len(teams)
    if n_teams % 2 != 0:
        raise ValueError("O número de times deve ser par!")
    
    list_teams_code = [teams[i]["Codigo"] for i in range(n_teams)]
    random.shuffle(list_teams_code) # Embaralha os times para uma tabela diferente a cada execução

    n_rounds = n_teams - 1
    season_all_games = {i+1: [] for i in range(n_rounds)}

    round_ngames = n_teams // 2
    list_rotate = list_teams_code[1:] # O primeiro time fica fixo
    fixed_team = list_teams_code[0]

    for n_round in range(n_rounds):
        current_round = []

        # Primeiro jogo sempre inclui o time fixo contra o último da lista rotativa
        current_round.append((fixed_team, list_rotate[-1]))

        # Criar os outros jogos da rodada sem repetições
        for i in range(round_ngames - 1):
            current_round.append((list_rotate[i], list_rotate[-(i+2)]))

        season_all_games[n_round + 1] = current_round

        # Rotaciona os times corretamente
        list_rotate = [list_rotate[-1]] + list_rotate[:-1]

    season_games = []

    # Cria uma Lista de rodadas, sendo cada rodada representado por um string com uma sequência de jogos
    for n_round, games in season_all_games.items():
        round_games = ""
        for game in games:
            round_games += (game[0] + game[1])
        season_games.append(round_games)

    return season_games

def generate_random_season_games(teams: list, population_size: int) -> list:
    """
    Gera uma Lista de Tabelas de Jogos de um Turno do Campeonato de forma aleatória
    Cada Tabela é uma Lista de rodadas, sendo cada rodada formada por um string de tamanho fixo ( (n_teams/2) * 4) contendo uma sequência de jogos 
    Restrições básicas:
        - Não é permitida o repetição de jogos entre as mesmas equipes por Turno, independente de quem seja o Mandante
        - Todas as equipes devem possuir jogo em cada rodada e apenas um jogo

    Parâmetros:
        n_teams (int): Quantidade de Equipes participantes do Campeonato
        population_size (int): O tamanho da população, i.e., o número de Tabelas a serem criadas

    Retorna:
        Lista de Tabelas de Jogos
        
    """
    random_season_games = []

    for n_population in range(population_size):
        season_games = generate_season_games(teams)
        random_season_games.append(season_games)

    return random_season_games

def generate_list_games(seq_games: str, piece_len: int = 4) -> list:
    """
    Gera uma Lista de jogos à partir de um string com uma sequência de jogos
    
    Parâmetros:
        seq_games: String com uma sequência de jogos, o tamanho deste string deve ser múltiplo de 4, pois cada jogo é representado por 4 digítos

    Retorna:
        Lista com os Jogos codificados , jogo é representado por 4 digítos
    """
    
    list_games = [seq_games[i:i+piece_len] for i in range(0, len(seq_games), piece_len)]
    
    return list_games

def generate_possible_games(teams = list):
    """
    Gera uma Lista contendo os códigos de todos os jogos possíveis do Campeonato
    
    Parâmetros:
        teams (list): Lista de Dicionários de Equipes

    Retorna:
        Lista com todos os jogos possíveis do Campeonato
    """
    n = len(teams)
    possible_games = []
    
    # Preencher a lista de jogos possíveis
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # Gera os códigos das Equipes que participarão do jogo
            team_code1 = str((i + 1)).zfill(2)
            team_code2 = str((j + 1)).zfill(2)
            # Gera o código do jogo entre as Equipes
            # Sendo a equipe Mandante a aparece primeiro ( 2 primeiras posições ) e portanto a Visante ( 2 últimas posiçoes )
            # Teremos então códigos distintos p/ o jogo de ida e de volta
            game = team_code1 +  team_code2

            # Insere jogo de ida no primeiro turno e jogo de volta no segundo
            possible_games.append(game)

    return possible_games

def generate_season_table_by_file(arq: str, sep: str, encoding: str, teams: list):
    """
    Lê um arquivo em formato .csv com a Tabela de jogos do primeiro turno de um Campeonato e gera uma Lista com estes jogos de maneira codificada
    Campos obrigatórios que devem constar no Arquivo:
      Num_Jogo - Número do Jogo
      Num_Rodada - Número da Rodada
      Mandante - Equipe Mandante
      Visitante - Equipe Visitante

    Parâmetros:
        arq - path do Arquivo
        delimitador - Caractere utilizado para separar as colunas do Arquivo .csv
        encoding - Encoding do arquivo 
        teams - Lista com os dados das Equipes Participantes

    Retorna:
        Lista dividida em rodadas, sendo cada rodada um string contendo os jogos
        Cada Rodada é representada por uma sequência de jogos, e cada jogo um sub-string de 4 digitos
        Sendo os 2 primeiros digitos o Código da Equipe Mandante e os 2 últimos o Código da Equipe Visitante
    """

    # Ler o arquivo CSV
    df = pd.read_csv(arq, sep=";", encoding="ISO-8859-1", dtype={"Num_Jogo": str})

    # Converter para uma lista de dicionários
    games = df.to_dict(orient="records")

    nrounds = len(teams) - 1
    season_games = ['' for _ in range(nrounds)]

    # Cria uma Lista de rodadas, sendo cada rodada representado por um string com uma sequência de jogos
    for game in games:
        n_round = game["Num_Rodada"]
        game_team1_name = game["Mandante"]
        game_team1_code = search_team_by_name(teams, game_team1_name)["Codigo"]
        game_team2_name = game["Visitante"]
        game_team2_code = search_team_by_name(teams, game_team2_name)["Codigo"] 
        game_code = game_team1_code + game_team2_code
        season_games[(n_round - 1)] = season_games[(n_round - 1)] + game_code

    return season_games

def generate_tco_file(tco: list, arq: str, sep: str, encoding: str, teams: list):
    """
    Gera um arquivo em formato .csv com a Tabela Otimizada de jogos de um Campeonato

    Parâmetros:
        tco - Lista com todas as rodadas do primeiro turno do Campeonato
        arq - path completo do Arquivo a ser gerado
        delimitador - Caractere a ser utilizado para separar as colunas do Arquivo .csv
        encoding - Encoding do arquivo 
    """
    
    # Criando e escrevendo no arquivo CSV manualmente
    with open(arq, mode="w", encoding=encoding) as tco_file_csv:
        # Escrevendo o cabeçalho
        tco_file_csv.write("Num_Jogo" + sep + "Num_Rodada" + sep + "Mandante" + sep + "Visitante\n")
    
        n_game = 0

        # Escrevendo os dados
        for n_round, seq_games in enumerate(tco, start=1):
            list_games = generate_list_games(seq_games, 4)
            for game in list_games:
                team1_code = game[:2]
                team2_code = game[2:]
                team1 = search_team_by_code(teams, team1_code)
                team1_name = team1["Nome do Time"]
                team2 = search_team_by_code(teams, team2_code)
                team2_name = team2["Nome do Time"]
                n_game += 1
                tco_file_csv.write(str(n_game) + sep + str(n_round) + sep +  team1_name + sep + team2_name + "\n")

def calculate_distance(local1: tuple, local2: tuple):
    """
    Calcula a distância entre duas coordenadas geográficas usando a fórmula de Haversine.

    Parâmetros:
        local1 - Latitude e Longitude da primeira cidade em Graus Decimais
        local2 - Latitude e Longitude da segunda cidade em Graus Decimais

    Retorna:
        Distância em quilômetros entre os dois pontos
    """

    # Raio médio da Terra em km
    R = 6371.0  

    # Converter graus para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [local1[0], local1[1], local2[0], local2[1]])

    # Diferença das coordenadas
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distância final
    distancia = R * c
    return distancia

def calculate_penalty_last_home(team1_last_home: int, team2_last_home: int) -> float:
    """
    Calcula a penalidade verificando se repete a mesma situação relativa a mando de campo ( Mandante / Visitante ) da rodada anterior das Equipes envolvidas em determinado jogo

    Parâmetros:
        team1_last_home (int) - 0 ( Time Mandante no jogo foi Visitante na rodada anterior ) ou 1 ( Time Mandante no jogo foi também Mandante na rodada anterior )
        team2_last_home (int) - 0 ( Time Visitante no jogo foi Visitante também na rodada anterior ) ou 1 ( Time Visitante no jogo foi  Mandante na rodada anterior )

    Retorna:
        float: Penalidade caso a situação ideal não foi encontrada
    """
    penalty = 0.00
    
    if team1_last_home == 1:
        penalty += 500.00

    if team2_last_home == 0:
        penalty += 500.00

    return penalty

def calculate_penalty_last_opponent(teams: list, team1_city: str, team1_last_opponent: str, team2_city: str, team2_last_opponent: str) -> float:
    """
    Calcula a penalidade verificando se na rodada anterior alguma das equipes enfrentou uma equipe da mesma cidade (clássico) e nesta rodada enfrenta outra equipe da mesma cidada

    Parâmetros:
        teams (list): Lista de Dicionários de Equipes
        team1_city (str) - Nome da Cidade do time Mandante
        team1_last_opponent (str) - Código do adversário na rodada anterior do time Mandante
        team2_city (str) - Nome da Cidade do time Visitante
        team2_last_opponent (str) - Código do adversário na rodada anterior do time Visitante
        
    Retorna:
        float: Penalidade caso a situação ideal não foi encontrada
    """

    penalty = 0.00
    
    if team1_city == team2_city:
        if team1_last_opponent != '':
            team1_last_opponent_city = get_team_city(search_team_by_code(teams, team1_last_opponent))
        else:
            team1_last_opponent_city = ''
        if team1_last_opponent_city == team1_city:
            penalty += 1000
        if team2_last_opponent != '':
            team2_last_opponent_city = get_team_city(search_team_by_code(teams, team2_last_opponent))
        else:
            team2_last_opponent_city = '' 
        if team2_last_opponent_city == team2_city:
            penalty += 1000
    
    return penalty
    
def calculate_penalty_ideal_city_round_n_games(team1_city: str, city_round_n_games: list) -> float:
    """
    Calcula a penalidade verificando a quantidade de jogos na rodada que acontecem na mesma cidade
    O ideal seria que a quantidade de jogos não ultrapasse o valor referente a metade do nº de times da Cidade
    Se o nº de times da cidade for impar soma-se 1 a divisão por inteiro do nº de times por 2

    Parâmetros:
        team1_city (str) - Nome da Cidade do time Mandante
        city_round_n_games (list) - Lista com o Nome de cadade Cidade, o total de equipes sediadas nela e a quantidade de jogos já contabilizados na rodada
        
    Retorna:
        float: Penalidade caso a situação ideal não foi encontrada
    """

    penalty = 0

    for city in city_round_n_games:
        if city["Cidade"] == team1_city:
            city_n_teams = city["QtdTimes"]
            if city_n_teams  > 1:
                ideal_n_games = ( city_n_teams // 2 ) + (city_n_teams % 2)
                city["JogosRodada"] += 1
                city_round_n_games = city["JogosRodada"]
                if city_round_n_games > ideal_n_games:
                    penalty += 300
            break

    return penalty

def calculate_penalty_balanced_travel(teams_distance_traveled: list, teams_season_distance_traveled: list):
    """
    Calcula a penalidade verificando a diferença entre a distância percorrida por cada equipe no turno e a metade da distância que esta equipe irá percorrer durante todo o campeonato
    A finalidade com isto é que a maioria dos times tenham a quantidade total de deslocamentos balanceadas por turno

    Parâmetros:
        teams_distance_traveled (list) - Lista com o Código de cada Equipe e o total de deslocamentos (Km) que ela irá percorrer durante todo o campeonato
        teams_season_distance_traveled (list) - Lista com o Código de cada Equipe e o total de deslocamentos (Km) que ela irá percorrer durante o primeiro turno do campeonato
    Retorna:
        float: Penalidade caso a situação ideal não foi encontrada
    """

    penalty = 0.00

    for team_code, total_distance in teams_distance_traveled.items():
        half_total_distance = total_distance / 2
        team_season_distance_traveled = teams_season_distance_traveled[team_code]
        dif = half_total_distance - team_season_distance_traveled
        if dif < 0:
            dif = -dif
        penalty += dif
    
    return penalty

def search_team_by_code(teams: list, team_code: str):
    '''
    Pesquisa o elemento com os dados da Equipe através do código desta Equipe

    Parâmetros:
        teams - Lista com os dados das Equipes participantes do Campeonato

    Retorna:
        Elemento com os dados da Equipe
    '''
    
    team_result = next((team for team in teams if team["Codigo"] == team_code), None)
    return team_result

def search_team_by_name(teams: list, team_name: str):
    '''
    Pesquisa o elemento com os dados da Equipe através do Nome desta Equipe

    Parâmetros:
        teams - Lista com os dados das Equipes participantes do Campeonato

    Retorna:
        Elemento com os dados da Equipe
    '''
    
    team_name = re.sub(r'\s+', ' ', team_name).strip()
    team_result = next((team for team in teams if team["Nome do Time"] == team_name), None)
    return team_result

def get_team_localization(team: dict):
    '''
    Cria tupla com a Latitude e Longitude da Cidade sede de determinada Equipe

    Parâmetros:
        team - Elemento com os dados de determinada Equipe

    Retorna:
        Tupla com a Latitude e Longitude da Equipe
    '''
    
    latitude = team["Latitude"]
    longitude = team["Longitude"]
    team_localization = (latitude,longitude)
    return team_localization

def get_team_name(team: dict):
    '''
    Informa o Nome de determinada Equipe

    Parâmetros:
        team - Elemento com os dados de determinada Equipe

    Retorna:
        String com o Nome da Equipe
    '''
    
    team_name = team["Nome do Time"]
    return team_name

def get_team_city(team: dict):
    '''
    Informa a Cidade Sede de determinada Equipe

    Parâmetros:
        team - Elemento com os dados de determinada Equipe

    Retorna:
        String com o Nome Cidade Sede de determinada Equipe
    '''
    team_city = team["Cidade do Time"]
    return team_city

def game_inserted(seq_games: str, game: str):
    '''
    Verifica se um determinado jogo já foi inserido na string com a uma sequência de jogos codificados

    Parâmetros:
        seq_games - Sequência de jogos codificados
        game - Código do jogo a ser procurado
        
    Retorna:
        Boolean
    '''
    
    game_inserted = False

    for i in range(0, len(seq_games), 4):
        current_game = seq_games[i:i + 4]
        if current_game == game:
            game_inserted = True
            break

    return game_inserted


def team_inserted(current_round: str, team_code1: str, team_code2: str):
    """
    Verifica se uma das Equipes já foi inserida em algum jogo na rodada
    
    Parâmetros:
        current_round (str): String com os jogos já programados p/ a rodada
        team_code1 (str): Código da Equipe 1
        team_code2 (str): Código da Equipe 2
        
    Retorna:
        Boolean
    """

    if current_round == "":
        return False

    current_round_size = len(current_round)
    team_inserted = False

    for i in range(0, current_round_size, 2):
        code = current_round[i:i + 2]
        if code == team_code1 or code == team_code2:
            team_inserted = True
            break
    
    return team_inserted

def change_game(seq_games: str, game: str, new_game: str):
    """
    Troca o Mando de campo de determinado jogo
    
    Parâmetros:
        seq_games (str): String com os jogos codificados
        game (str): Código do Jogo a ter mando trocado
        new_game (str): Novo Código do Jogo
        
    Retorna:
        String com a nova sequência dos jogos
    """
    
    if len(game) != 4 or len(new_game) != 4:
        return seq_games
    
    list_games = generate_list_games(seq_games, 4)
    
    try:
        index = list_games.index(game)  # Encontra a posição do jogo procurado
        list_games[index] = new_game  # Substitui pelo novo jogo
    except ValueError:
        pass
    
    return "".join(list_games) 

def remove_game(list_games: list, game: str):
    """
    Remove determinado jogo de uma Lista com diversos jogos codificados
    
    Parâmetros:
        list_games (list): Lista com os jogos codificados
        game (str): Código do Jogo a ter removido da Lista
        
    Retorna:
        Lista de jogos
    """
    
    try:
        list_games.remove(game)
    except:
        pass

def print_list_games_by_round(season: list, teams:list):
    """
    Imprime todos os jogos do Turno do Campeonato por Rodada
    
    Parâmetros:
        list_games (list): Lista com os jogos codificados
        teams - Lista com os dados das Equipes participantes do Campeonato
    """
    
    for i, current_round in enumerate(season, start=1):
        print(f"\nRodada {i}:")
        games = []
        for j in range(0, len(current_round), 4):
            team1 = search_team_by_code(teams, current_round[j:j+2])
            team2 = search_team_by_code(teams, current_round[j+2:j+4])
            games.append(get_team_name(team1) + " x " + get_team_name(team2))

        for n_game, game in enumerate(games):
            print(f"{n_game+1} - {game}")