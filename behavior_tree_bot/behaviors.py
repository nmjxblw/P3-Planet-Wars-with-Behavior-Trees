import sys
import logging
import math

sys.path.insert(0, "../")
from planet_wars import issue_order


def find_closest_strong_planet(state, my_planets, target_planet):
    if len(my_planets) < 1:
        return None

    distance = state.distance(my_planets[0].ID, target_planet.ID)
    closest_planet = my_planets[0]
    # exp = target_planet.growth_rate / (target_planet.num_ships + target_planet.growth_rate * distance + 1) * distance
    for planet in my_planets:
        curr_distance = state.distance(planet.ID, target_planet.ID)
        if (
            curr_distance < distance
            and planet.num_ships - 1
            >= target_planet.num_ships + target_planet.growth_rate * curr_distance + 1
        ):
            distance = curr_distance
            # exp = curr_exp
            closest_planet = planet

    return closest_planet


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
        attack_planet = find_closest_strong_planet(state, attack_planets, enemy_planet)
        if attack_planet:
            require_ships = (
                enemy_planet.num_ships
                + 1
                + state.distance(attack_planet.ID, enemy_planet.ID)
                * enemy_planet.growth_rate
            )
            attack_List.append(
                issue_order(state, attack_planet.ID, enemy_planet.ID, require_ships)
            )
            attack_planets.remove(attack_planet)

    if not attack_List:
        return False
    else:
        return attack_List


def spread_to_weakest_neutral_planet(state):
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    target_planets = [state.planets[f.destination_planet] for f in state.fleets]
    valied_planets = [p for p in state.neutral_planets() if p not in target_planets]

    if not strongest_planet or len(valied_planets) <= 0:
        return False

    weakest_planets = sorted(
        valied_planets,
        key=lambda p: (p.num_ships, -p.growth_rate),
    )

    strongest_planet_remaining_ships = strongest_planet.num_ships
    solutions = []
    for p in weakest_planets:
        require_ships = p.num_ships + 1
        if (
            strongest_planet_remaining_ships - require_ships
            >= strongest_planet.num_ships / 2
        ):
            solutions.append(
                issue_order(state, strongest_planet.ID, p.ID, require_ships)
            )
            strongest_planet_remaining_ships -= require_ships

    return solutions


def defense_attacked_planet(state):
    if len(state.my_planets()) <= 1:
        return False
    enemy_fleets = [f for f in state.enemy_fleets()]
    enemy_fleets.sort(key=lambda f: f.turns_remaining)
    enemy_targets = [f.destination_planet for f in state.enemy_fleets()]
    solutions = []
    for f in enemy_fleets:
        source_plants_list = [
            fleet.source_planet
            for fleet in state.fleets
            if f.destination_planet == fleet.destination_planet
        ]
        if f.destination_planet in state.my_planets():
            remaining_ships = (
                state.planets[f.destination_planet].num_ships
                + f.turns_remaining * state.planets[f.destination_planet].growth_rate
                - f.num_ships
            )
            if remaining_ships > 0:
                continue
        else:
            remaining_ships = (
                state.planets[f.destination_planet].num_ships
                + f.turns_remaining * state.planets[f.destination_planet].growth_rate
                - f.num_ships
            )
            remaining_ships = -abs(remaining_ships)

        require_ships = 1 - remaining_ships
        def_planets = [
            p
            for p in state.my_planets()
            if f.turns_remaining + 2
            >= state.distance(p.ID, f.destination_planet)
            >= f.turns_remaining + 1
            and p.ID not in source_plants_list
        ]
        def_planets.sort(
            key=lambda p: (
                state.distance(p.ID, f.destination_planet),
                p.num_ships,
            )
        )
        if len(def_planets) <= 0:
            continue
        else:
            for p in def_planets:
                require_ships += (
                    state.distance(p.ID, f.destination_planet) - f.turns_remaining
                ) * state.planets[f.destination_planet].growth_rate
                ships_on_planet = p.num_ships
                if p.ID in enemy_targets:
                    for fleet in enemy_fleets:
                        if fleet.destination_planet == p.ID:
                            ships_on_planet = (
                                p.num_ships
                                + fleet.turns_remaining
                                * state.planets[p.ID].growth_rate
                                - fleet.num_ships
                            )
                            break
                if ships_on_planet < 1:
                    continue
                elif (
                    require_ships + 1 >= math.ceil(p.num_ships * 2 / 3)
                    or p.num_ships < state.planets[f.destination_planet].num_ships
                ):
                    continue
                else:
                    solutions.append(
                        issue_order(state, p.ID, f.destination_planet, require_ships)
                    )
                    break
    return solutions
