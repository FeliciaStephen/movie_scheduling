import random

# Problem parameters
# NUM_MOVIES = 5
# NUM_SCREENS = 3
# SLOTS_PER_DAY = 3
# DAYS_PER_WEEK = 7

# Example data
# movie_names = ["Movie1", "Movie2", "Movie3", "Movie4", "Movie5"]
# seat_requests = [50, 60, 40, 30, 70]
# available_seats = [100, 120, 80]

# Genetic Algorithm parameters
POPULATION_SIZE = 10
MAX_GENERATIONS = 100
CROSSOVER_RATE = 0.7
MUTATION_RATE = 0.1
def generate_schedule():
    population = []
    for _ in range(POPULATION_SIZE):
        schedule = []
        for _ in range(DAYS_PER_WEEK):
            daily_schedule = []
            for _ in range(SLOTS_PER_DAY):
                # Ensure available movies
                available_movies = [movie for movie in range(NUM_MOVIES) if movie not in schedule]
                if not available_movies:
                    break  # No more available movies for the day

                # Debug prints
                # print("available_movies:", available_movies)
                # print("available_seats:", available_seats)
                # print("seat_requests:", seat_requests)

                # Calculate profitability for available movies
                profitability = [(movie, available_seats[movie] / seat_requests[movie]) for movie in available_movies if movie < len(available_seats) and movie < len(seat_requests)]
                # print("debug: profitability", profitability)



                # Sort movies by profitability in descending order
                sorted_movies = sorted(profitability, key=lambda x: x[1], reverse=True)

                # Select top movies based on the number of screens
                selected_movies = [movie for movie, _ in sorted_movies[:NUM_SCREENS]]

                # Add selected movies to the schedule
                daily_schedule.extend(selected_movies)

                # Debug print
                # print("daily_schedule:", daily_schedule)

            schedule.extend(daily_schedule)
        population.append(schedule)
    return population

# Uncomment the following line to debug
# best_schedule = genetic_algorithm()

# Fitness function
def fitness(schedule):
    # Calculate the total profit based on your criteria
    # This is a simplified example, you should customize it based on your profit calculation
    total_profit = sum([seat_requests[movie] for movie in schedule])
    return total_profit

# Selection
def selection(population, fitness_values):
    selected_indices = random.choices(range(POPULATION_SIZE), k=POPULATION_SIZE, weights=fitness_values)
    return [population[i] for i in selected_indices]

# Crossover
def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

# Mutation
def mutation(child):
    if random.random() < MUTATION_RATE:
        mutation_point = random.randint(0, len(child) - 1)
        child[mutation_point] = random.randint(0, NUM_MOVIES - 1)
    return child

# Genetic Algorithm
def genetic_algorithm():
    population = generate_schedule()

    for generation in range(MAX_GENERATIONS):
        # Evaluate fitness of each schedule in the population
        fitness_values = [fitness(schedule) for schedule in population]

        # Select parents
        selected_population = selection(population, fitness_values)

        # Create the next generation through crossover and mutation
        new_population = []
        while len(new_population) < POPULATION_SIZE:
            parent1, parent2 = random.sample(selected_population, 2)

            if random.random() < CROSSOVER_RATE:
                offspring1, offspring2 = crossover(parent1, parent2)
            else:
                offspring1, offspring2 = parent1[:], parent2[:]

            offspring1 = mutation(offspring1)
            offspring2 = mutation(offspring2)

            new_population.extend([offspring1, offspring2])

        population = new_population

    # Find the best schedule in the final population
    best_schedule = max(population, key=fitness)
    return best_schedule

# Main
# best_schedule = genetic_algorithm()
# print("Best Movie Schedule:")
# # Create a list to represent the available slots for each day
# slots_per_day = [[] for _ in range(DAYS_PER_WEEK)]

# # Iterate through the slots and assign movies to available slots
# for movie in best_schedule:
#     day, slot = divmod(movie, SLOTS_PER_DAY)
#     if slot not in [s[1] for s in slots_per_day[day]]:
#         slots_per_day[day].append((movie_names[movie], slot))

# # Print the schedule
# for day, day_schedule in enumerate(slots_per_day):
#     print(f"Day {day + 1}: {day_schedule}")

import random
import json

DAYS_PER_WEEK = 7
SLOTS_PER_DAY = 3


# Get movie names and demand from the user
movies = {}
num_movies = int(input("Enter the number of movies: "))

for _ in range(num_movies):
    movie_name = input("Enter movie name: ")
    demand = int(input(f"Enter demand for {movie_name}: "))
    movies[movie_name] = {"demand": demand}
SCREENS=int(input('Enter the number of screens:'))
# Get the number of seats for each screen
seats_per_screen = {}
for screen in range(SCREENS):
    screen_name = f"Screen{screen + 1}"
    seats_per_screen[screen_name] = int(input(f"Enter the number of seats for {screen_name}: "))

# Initialize schedule
schedule = [[None] * SCREENS for _ in range(DAYS_PER_WEEK * SLOTS_PER_DAY)]

# Count of seats that could not be scheduled
unscheduled_seats = 0

# Main loop to generate schedule
movie_list = list(movies.keys())

for day in range(DAYS_PER_WEEK):
    for slot in range(SLOTS_PER_DAY):
        for screen in range(SCREENS):
            # Shuffle the movie list to randomize selection
            random.shuffle(movie_list)
            movie = None

            for candidate_movie in movie_list:
                if movies[candidate_movie]["demand"] > 0:
                    # Distribute the demand of the movie across screens if needed
                    scheduled_demand = min(
                        movies[candidate_movie]["demand"],
                        seats_per_screen[f"Screen{screen + 1}"],
                    )
                    movies[candidate_movie]["demand"] -= scheduled_demand
                    schedule[day * SLOTS_PER_DAY + slot][screen] = (
                        candidate_movie,
                        scheduled_demand,
                    )

                    # Update unscheduled seats count
                    unscheduled_seats += max(
                        0, movies[candidate_movie]["demand"]
                    )

                    # If demand is still left for the movie, attempt to schedule on other screens
                    for additional_screen in range(SCREENS):
                        if (
                            additional_screen != screen
                            and movies[candidate_movie]["demand"] > 0
                        ):
                            scheduled_demand = min(
                                movies[candidate_movie]["demand"],
                                seats_per_screen[f"Screen{additional_screen + 1}"],
                            )
                            movies[candidate_movie]["demand"] -= scheduled_demand
                            schedule[day * SLOTS_PER_DAY + slot][
                                additional_screen
                            ] = (candidate_movie, scheduled_demand)

                    break  # Stop searching after finding a suitable movie

# Display schedule with varying seats
for day in range(DAYS_PER_WEEK):
    print(f"Day {day + 1}:")
    for slot in range(SLOTS_PER_DAY):
        print(f"{slot * 3:02d}:00am:")
        for screen in range(SCREENS):
            schedule_entry = schedule[day * SLOTS_PER_DAY + slot][screen]
            if schedule_entry:
                movie, demand = schedule_entry
                print(
                    f"{' ' * 16}Screen {screen + 1} ({seats_per_screen[f'Screen{screen + 1}']} seats)\t{movie} ({demand} seats)"
                )

# Display the count of unscheduled seats
print(f"\nSeats that could not be scheduled: {unscheduled_seats}")

# Write movie data to JSON file
with open("movie_data.json", "w") as json_file:
    json.dump(movies, json_file)

print("Movie data has been written to movie_data.json.")

