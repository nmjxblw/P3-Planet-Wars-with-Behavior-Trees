import sys

sys.path.insert(0, "../")
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    my_target_planets = [state.planets[f.destination_planet] for f in state.my_fleets()]
    valied_planets = [
        p for p in state.enemy_planets() if p not in my_target_planets
    ]

    if not strongest_planet or len(valied_planets) <= 0:
        return False

    weakest_planets = iter(
        sorted(
            valied_planets,
            key=lambda p: (
                p.num_ships,
                -p.growth_rate
                / (
                    (
                        p.num_ships
                        + state.distance(strongest_planet.ID, p.ID) * p.growth_rate
                        + 1
                    )
                    * state.distance(strongest_planet.ID, p.ID)
                ),
            ),
        )
    )

    try:
        weakest_planet = next(weakest_planets)
        while True:
            require_ships = (
                weakest_planet.num_ships
                + state.distance(strongest_planet.ID, weakest_planet.ID)
                * weakest_planet.growth_rate
                + 1
            )
            if require_ships <= strongest_planet.num_ships / 2:
                return issue_order(
                    state, strongest_planet.ID, weakest_planet.ID, require_ships
                )
            else:
                weakest_planet = next(weakest_planets)
    except StopIteration:
        return False


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


def defense_attacked_planet(state):
    # get all enemy_fleets which are attacking friendly planets
    enemy_targets = [state.planets[fleet.destination_planet] for fleet in state.enemy_fleets()]
    attacked_planets = [
        p for p in state.my_planets() if p in enemy_targets
    ]
    if len(attacked_planets) <= 0:
        return False

    # Determine a most valuable planet.
    attacked_planets.sort(
        key=lambda p: ((p.growth_rate * p.num_ships, p.num_ships, p.growth_rate)),
        reverse=True,
    )
    attacked_planets_iter = iter(attacked_planets)
    unattacked_planets = [
        p for p in state.my_planets() if p not in attacked_planets
    ]
    if len(unattacked_planets) <= 0:
        return False
    try:
        attacked_planets_iter = next(attacked_planets_iter)
        while True:
            enemy_fleets = [
                f
                for f in state.enemy_fleets()
                if f.destination_planet == attacked_planets_iter.ID
            ]
            enemy_fleets_iter = iter(enemy_fleets.sort(key=lambda f: f.turns_remaining))
            try:
                enemy_fleets_iter = next(enemy_fleets_iter)
                while True:
                    require_ships = (
                        enemy_fleets_iter.num_ships
                        + 1
                        - attacked_planets_iter.num_ship
                        - attacked_planets_iter.growth_rate
                        * enemy_fleets_iter.turns_remaining
                    )
                    if require_ships <= 0:
                        enemy_fleets_iter = next(enemy_fleets_iter)
                        continue

                    reinforcement_planets = [
                        p
                        for p in unattacked_planets
                        if state.distance(p.ID, attacked_planets_iter.ID)
                        <= enemy_fleets_iter.turns_remaning
                    ]
                    reinforcement_planets_iter = iter(
                        reinforcement_planets.sort(
                            key=lambda p: p.num_ships, reverse=True
                        )
                    )
                    reinforcement_planets_iter = next(reinforcement_planets_iter)
                    if reinforcement_planets_iter.num_ship - require_ships > 1:
                        return issue_order(
                            state,
                            reinforcement_planets_iter.ID,
                            attacked_planets_iter.ID,
                            require_ships,
                        )
                    else:
                        return issue_order(
                            state,
                            attacked_planets_iter.ID,
                            reinforcement_planets_iter.ID,
                            attacked_planets_iter.num_ships,
                        )
            except StopIteration:
                attacked_planets_iter = next(attacked_planets_iter)

    except StopIteration:
        return False


# def spread_to_most_valueable_neutral_planet(state):
