import sys

sys.path.insert(0, "../")
from planet_wars import issue_order

def find_closest_strong_planet(state, my_planets, target_planet):
    if len(my_planets) < 1:
        return None,None

    distance = state.distance(my_planets[0].ID, target_planet.ID)
    closest_planet = my_planets[0]
    #exp = target_planet.growth_rate / (target_planet.num_ships + target_planet.growth_rate * distance + 1) * distance
    for planet in my_planets:
        curr_distance = state.distance(planet.ID, target_planet.ID)
        curr_exp = target_planet.growth_rate / (target_planet.num_ships + target_planet.growth_rate * curr_distance + 1) * curr_distance
        if curr_distance < distance  and planet.num_ships >= target_planet.num_ships + target_planet.growth_rate * curr_distance + 1:
            distance = curr_distance
            #exp = curr_exp
            closest_planet = planet

    return closest_planet, distance


# def attack_weakest_enemy_planet(state):
#     strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

#     my_target_planets = [state.planets[f.destination_planet] for f in state.my_fleets()]
#     valied_planets = [p for p in state.enemy_planets() if p not in my_target_planets]


    
#     if not strongest_planet or len(valied_planets) <= 0:
#         return False

#     weakest_planets = iter(
#         sorted(
#             valied_planets,
#             key=lambda p: (
#                 p.num_ships,
#                 -p.growth_rate
#                 / (
#                     (
#                         p.num_ships
#                         + state.distance(strongest_planet.ID, p.ID) * p.growth_rate
#                         + 1
#                     )
#                     * state.distance(strongest_planet.ID, p.ID)
#                 ),
#             ),
#         )
#     )



#     try:
#         weakest_planet = next(weakest_planets)
#         while True:
#             require_ships = (
#                 weakest_planet.num_ships
#                 + state.distance(strongest_planet.ID, weakest_planet.ID)
#                 * weakest_planet.growth_rate
#                 + 1
#             )
#             if require_ships <= strongest_planet.num_ships / 2:
#                 return issue_order(
#                     state, strongest_planet.ID, weakest_planet.ID, require_ships
#                 )
#             else:
#                 weakest_planet = next(weakest_planets)
#     except StopIteration:
#         return False

def attack_weakest_enemy_planet(state):
    my_target_planets = [state.planets[f.destination_planet] for f in state.my_fleets()]
    valied_planets = [p for p in state.enemy_planets() if p not in my_target_planets]

    if len(valied_planets) < 1:
        return False
    
    attack_List = []

    valied_planets.sort(key=lambda t: t.num_ships, reverse=False)

    attack_planets = state.my_planets()
    
    for enemy_planet in valied_planets:
        attack_planet, distance= find_closest_strong_planet(state, attack_planets, enemy_planet)
        if attack_planet:
            attack_List.append(issue_order(state, attack_planet.ID, enemy_planet.ID, enemy_planet.num_ships + 1 + distance * enemy_planet.growth_rate))
            attack_planets.remove(attack_planet)

    if not attack_List:
        return False
    else:
        return attack_List


def spread_to_weakest_neutral_planet(state):
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    my_target_planets = [state.planets[f.destination_planet] for f in state.my_fleets()]
    valied_planets = [p for p in state.neutral_planets() if p not in my_target_planets]

    if not strongest_planet or len(valied_planets) <= 0:
        return False

    weakest_planets = iter(
        sorted(
            valied_planets,
            key=lambda p: (
                -p.growth_rate
                / ((p.num_ships + 1) * state.distance(strongest_planet.ID, p.ID)),
                p.num_ships,
            ),
        )
    )

    try:
        weakest_planet = next(weakest_planets)
        while True:
            require_ships = weakest_planet.num_ships + 1

            if require_ships <= strongest_planet.num_ships / 2:
                return issue_order(
                    state, strongest_planet.ID, weakest_planet.ID, require_ships
                )
            else:
                weakest_planet = next(weakest_planets)
    except StopIteration:
        return False

# def spread_to_weakest_neutral_planet(state):
#     my_target_planets = [state.planets[f.destination_planet] for f in state.my_fleets()]
#     valied_planets = [p for p in state.neutral_planets() if p not in my_target_planets]

#     if len(valied_planets) < 1:
#         return False
    
#     weakest_planet = min(valied_planets, key=lambda t: t.num_ships, default=None)
#     attack_planet, distance= find_closest_strong_planet(state, state.my_planets(), weakest_planet)

#     if not attack_planet:
#         return False
#     else:
#         return issue_order(state, attack_planet.ID, weakest_planet.ID, weakest_planet.num_ships + 1 + distance * weakest_planet.growth_rate)

def defense_attacked_planet(state):
    # this means we dont have any planets
    if len(state.my_planets()) <= 0:
        # we cant do this plan, just return False
        return False

    # some shortcuts
    def get_fleets_attack(p):
        enemy_fleets = []
        for f in state.enemy_fleets():
            if state.planets[f.destination_planet] == p or f.destination_planet == p:
                enemy_fleets.append(f)
        return enemy_fleets

    def remaining_ships(p):
        if is_not_attacked(p):
            return True
        fleets_list = get_fleets_attack(p)
        fleets = iter(fleets_list.sort(key=lambda f: f.turns_remaining))
        try:
            fleet = next(fleets)
            remaining_ships = p.num_ships
            turns_for_growth = fleet.turns_remaining
            while True:
                remaining_ships += -fleet.num_ships + turns_for_growth * p.growth_rate
                turns_for_growth = fleet.turns_remaining
                fleet = next(fleets)
                turns_for_growth = fleet.turns_remaining - turns_for_growth
        except StopIteration:
            return remaining_ships

    def get_reinforcement_fleets(p):
        fleets = [f for f in state.my_fleets if f.destination_planet == p.ID]
        fleets.sort(key=lambda f: (f.turns_remaining, -f.num_ships))
        return fleets

    can_def = lambda p: remaining_ships(p) > 0

    enemy_targets = [
        state.planets[fleet.destination_planet] for fleet in state.enemy_fleets()
    ]
    attacked_planets = [p for p in state.my_planets() if p in enemy_targets]
    is_attacked = lambda p: p in attacked_planets
    is_not_attacked = lambda p: p not in attacked_planets
    unattacked_planets = [p for p in state.my_planets() if is_not_attacked(p)]
    # shortcuts end

    # none of our planets is attacked
    # abort this plan
    if len(attacked_planets) <= 0:
        return False

    # Determine a most valuable planets and sort them
    attacked_planets.sort(
        key=lambda p: ((p.growth_rate * p.num_ships, p.num_ships, p.growth_rate)),
        reverse=True,
    )
    # set an iterater
    attacked_planets = iter(attacked_planets)

    try:
        attacked_planet = next(attacked_planets)
        while True:
            # if the planet can survive, leave it and go to the next planet
            if can_def(attacked_planet):
                attacked_planet = next(attacked_planets)
                continue
            # find the most powerful planet as a reinforcement
            reinforcement_planets = state.my_planets()
            reinforcement_planets.remove(attacked_planet)
            reinforcement_planets.sort(
                key=lambda p: (
                    p.num_ships / state.distance(p.ID, attacked_planet.ID),
                    p.num_ships,
                ),
                reverse=True,
            )
            reinforcement_planets = iter(reinforcement_planets)
            try:
                reinforcement_planet = next(reinforcement_planets)
                if is_attacked(reinforcement_planet):
                    saveable = (
                        remaining_ships(reinforcement_planet)
                        + remaining_ships(attacked_planet)
                        > 0
                    )
                    if saveable:
                        return issue_order(
                            state,
                            reinforcement_planet.ID,
                            attacked_planet.ID,
                            1 - remaining_ships(attacked_planet),
                        )
                elif (
                    reinforcement_planet.num_ships + remaining_ships(attacked_planet)
                    > 0
                ):
                    return issue_order(
                        state,
                        reinforcement_planet.ID,
                        attacked_planet.ID,
                        1 - remaining_ships(attacked_planet),
                    )
            except StopIteration:
                # this shouldn't happen, reinforcement_planet is empty
                False

    except StopIteration:
        return False
