# TCO Solver using Genetic Algorithm

This repository contains a Python implementation that generates an Optimized Sports Championship Table (TCO) using a Genetic Algorithm (GA). TCO is a combinatorial optimization problem, where the goal is to create a Table that ensures more sports fairness, and also meets commercial and logistics objectives.

## Overview

The TCO solver employs a Genetic Algorithm to iteratively evolve a population of candidate solutions towards an optimal or near-optimal solution. GA operates by mimicking the process of natural selection, where individuals with higher fitness (i.e., those with fewer penalties) are more likely to survive and produce offspring.

To calculate the fitness of each solution, based on the established objectives, evaluation criteria are defined, each receiving a weight (number of penalty points) and being added to the fitness calculation if not met.

## Files

- **genetic_algorithm.py**: Contains the implementation of the Genetic Algorithm, including functions for generating random populations, calculating fitness, performing crossover and mutation operations, and classifying populations based on fitness.
- **tco.py**: Implements the core TCO solver using Pygame for visualization. It initializes the problem, creates the initial population, and iteratively evolves the population while visualizing the best solution found so far.
- **draw_functions.py**: Provides functions for drawing tables and graphs using Pygame. - **utils_tco.py**: Provides functions to generate random populations, calculate penalties, and other functions used by other programs in the application
- **benchmark_tb2025.py**: Calculates the fitness of a solution that will be used as a reference for evaluating the results (Official Table of the 1st Round of the 2025 Brazilian Championship)

## Usage

To run the TCO solver, run the `tco.py` script using Python. The program will stop at generation 2000, or at any desired time by pressing the 'q' key.

You can customize parameters such as population size, number of generations, probability and mutation intensity directly in the `tco.py` script.

## Dependencies

- Python 3.x
- Pygame (for visualization)

Make sure Pygame is installed before running the solver. You can install Pygame using pip:

```bash
pip install pygame
```

## Acknowledgements

This TCO solver was developed as a learning project and is inspired by several online resources and academic materials on Genetic Algorithms, including a project provided as an example by Professor Sérgio Polimante, which is an implementation of a solution to the Traveling Salesman Problem (TSP), a classic problem in combinatorial optimization.

## License

This project is licensed under the [MIT License](LICENSE).