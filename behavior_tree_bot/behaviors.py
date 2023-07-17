import sys
import logging

sys.path.insert(0, "../")
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    my_target_planets = [state.planets[f.destination_planet] for f in state.my_fleets()]
    valied_planets = [p for p in state.enemy_planets() if p not in my_target_planets]

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
                return [
                    issue_order(
                        state, strongest_planet.ID, weakest_planet.ID, require_ships
                    ),
                    issue_order(
                        state, strongest_planet.ID, weakest_planet.ID, require_ships
                    ),
                ]
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
    # first we need to know the how many planets do we have
    if len(state.my_planets()) <= 1:
        # This strategy only works on more than 2 planets. it's over.
        return False

    # define some helpful fucntion or short cut
    # def my_planets and sort it by num_ships, the first one is the strongest planet
    my_planets = sorted(
        [p for p in state.my_planets()], key=lambda p: p.num_ships, reverse=True
    )
    # my most powerful planet
    my_strongest_planet = my_planets[0]
    # get my fleets
    my_fleets = state.my_fleets()

    # get all enemy fleets which target my planets,
    # sort them by the turns_remaining
    enemy_fleets = sorted(
        [
            f
            for f in state.enemy_fleets()
            if state.planets[f.destination_planet] in state.my_planets()
        ],
        key=lambda f: f.turns_remaining,
    )
    # since we run the check attacked and it returns true,
    # so we dont have to check the num of enemy_fleets any more.

    # A shortcut to know if the planet is attacked
    is_attacked = lambda p: any(f for f in enemy_fleets if f.destination_planet == p.ID)

    # A shortcut to get all fleets fly to given planet
    fleets_to_p = lambda p: sorted(
        [f for f in state.fleets if f.destination_planet == p.ID],
        key=lambda f: f.turns_remaining,
    )

    # A shortcut to know the max
    # and min of reinforcements can be send form the planet
    def reinforcements_can_send(p):
        enemy_fleets_on_the_way = get_enemy_fleets_on_the_way(p)

        if p.num_ships >= enemy_fleets_on_the_way[0]["remaining_ships"] >= 1:
            max_reinfocements = enemy_fleets_on_the_way[0]["remaining_ships"] - 1
        elif enemy_fleets_on_the_way[0]["remaining_ships"] > p.num_ships:
            max_reinfocements = p.num_ships - 1
        else:
            max_reinfocements = 0

        if (
            p.num_ships
            >= enemy_fleets_on_the_way[len(enemy_fleets_on_the_way) - 1][
                "remaining_ships"
            ]
            >= 1
        ):
            min_reinfocements = (
                enemy_fleets_on_the_way[len(enemy_fleets_on_the_way) - 1][
                    "remaining_ships"
                ]
                - 1
            )
        elif (
            enemy_fleets_on_the_way[len(enemy_fleets_on_the_way) - 1]["remaining_ships"]
            - 1
            > p.num_ships
        ):
            min_reinfocements = (
                enemy_fleets_on_the_way[len(enemy_fleets_on_the_way) - 1][
                    "remaining_ships"
                ]
                - p.num_ships
                - 1
            )
        else:
            min_reinfocements = 0
        return max_reinfocements, min_reinfocements

    # before the next step, def a helper func
    # get a list of fleets are on the way to target planet
    # sort them by turns_remaining.
    # fleets = [
    #               {
    #                   Order of arrival at the planets:{
    #                       "turns_remaining": f.turns_remaining,
    #                        "num_ships": f.num_ships,
    #                        "remaining_ships": remaining_ships, # planet remaninig_ships when fleet arrives
    #                  }
    #                                                       }
    #                                                           ]
    def get_enemy_fleets_on_the_way(p):
        if not is_attacked(p):
            return [
                {
                    "rank": 0,
                    "turns_remaining": 0,
                    "source_planet": 0,
                    "destination_planet": 0,
                    "num_ships": 0,
                    "remaining_ships": p.num_ships,
                    "total_trip_length": 0,
                    "owner": 0,
                }
            ]
        fleets = []
        last_turns_remaining = 0
        remaining_ships = p.num_ships
        counter = 0
        for f in fleets_to_p(p):
            turns_for_growth = f.turns_remaining - last_turns_remaining
            if remaining_ships >= 1:
                growth_rate = p.growth_rate
            elif remaining_ships == 0:
                growth_rate = 0
            else:
                growth_rate = -p.growth_rate

            remaining_ships += turns_for_growth * growth_rate
            if f.owner == 1:
                remaining_ships += f.num_ships
            else:
                remaining_ships -= f.num_ships
                fleets.append(
                    {
                        "rank": counter,
                        "turns_remaining": f.turns_remaining,
                        "source_planet": f.source_planet,
                        "destination_planet": f.destination_planet,
                        "num_ships": f.num_ships,
                        "remaining_ships": remaining_ships,
                        "total_trip_length": f.total_trip_length,
                        "owner": f.owner,
                    }
                )
                counter += 1
            last_turns_remaining = f.turns_remaining

        fleets.sort(key=lambda x: x["rank"])

        return fleets

    # Then we need to know wich one of our planets is attacked by the enemy
    # And sort the planets by the value (expectations).

    my_attacked_planets = [
        state.planets[f.destination_planet]
        for f in enemy_fleets
        if state.planets[f.destination_planet] in state.my_planets()
    ]

    my_attacked_planets = sorted(
        my_attacked_planets,
        key=lambda p: (
            p.num_ships,
            p.growth_rate,
        ),
        reverse=True,
    )

    # Now we need to determine which planets
    # are capable of providing timely fleets
    # to the attacked planet.
    def reinforcement_planets(attacked_p, turns_remaining):
        t_planets = state.my_planets()
        t_planets.remove(attacked_p)
        p_list = []
        for p in t_planets:
            if state.distance(attacked_p.ID, p.ID) <= turns_remaining:
                p_list.append(p)
        p_list.sort(key=lambda p: (-p.num_ships, state.distance(p.ID, attacked_p.ID)))
        return p_list

    # now we initialize the solution dict
    # hit: solutions is the only meanningful thing.
    # we need to return it and create our action node.
    # format     [renforcement_planet,attack_planet.ID,num_ships]
    solutions = []

    # Some functions used to implement defensive strategies.
    # Last resort:Evacuate all fleets
    def evacuate_all_fleets(start_p, destination_p):
        solutions.append(
            issue_order(state, start_p.ID, destination_p.ID, start_p.num_ships - 1)
        )

    # min strategy:Requesting reinforcements from nearby planets.
    def send_min_reinforce(attacked_p, s_list):
        s_num_ships = my_strongest_planet.num_ships
        for s in s_list:
            solutions.append(issue_order(state, s[0].ID, attacked_p.ID, s[1]))
            if s_num_ships - s[1] >= my_attacked_planet.num_ships:
                solutions.append(
                    issue_order(state, my_strongest_planet.ID, s[0].ID, s[1])
                )
                s_num_ships -= s[1]

    def send_max_reinforce(attacked_p, s_list):
        s_num_ships = my_strongest_planet.num_ships
        for s in s_list:
            solutions.append(issue_order(state, s[0].ID, attacked_p.ID, s[2]))
            if s_num_ships - s[2] >= my_attacked_planet.num_ships:
                solutions.append(
                    issue_order(state, my_strongest_planet.ID, s[0].ID, s[2])
                )
                s_num_ships -= s[2]

    # create an iter
    my_attacked_planets = iter(my_attacked_planets)

    try:
        my_attacked_planet = next(my_attacked_planets)
        while True:
            # first we need to know what's min num of require ships
            enemy_fleets_on_the_way = get_enemy_fleets_on_the_way(my_attacked_planet)

            turns_remaining = enemy_fleets_on_the_way[0]["turns_remaining"]
            min_require_ships = 1 - enemy_fleets_on_the_way[0]["remaining_ships"]
            max_require_ships = (
                1
                - enemy_fleets_on_the_way[len(enemy_fleets_on_the_way) - 1][
                    "remaining_ships"
                ]
            )
            if max_require_ships <= 0:
                # this means we can finially save the planet wtihout any operates
                # so just leave it
                my_attacked_planet = next(my_attacked_planets)
                continue
            # Heuristic strategy:Requesting reinforcements from nearby planets.
            reinforcement_planets_list = reinforcement_planets(
                my_attacked_planet, turns_remaining
            )

            if len(reinforcement_planets_list) <= 0:
                # no reinforcement_planet
                t_planets = state.my_planets()
                t_planets.remove(my_attacked_planet)
                near_by_p = sorted(
                    t_planets,
                    key=lambda p: (
                        state.distance(p.ID, my_attacked_planet.ID),
                        p.num_ships,
                    ),
                )
                evacuate_all_fleets(my_attacked_planet, near_by_p[0])
                my_attacked_planet = next(my_attacked_planets)
                continue
            max_reinforce = 0
            min_reinforce = 0
            s_list = []
            for reinforce_p in reinforcement_planets_list:
                max_f, min_f = reinforcements_can_send(reinforce_p)
                max_reinforce += max_f
                min_reinforce += min_f
                s_list.append([reinforce_p, min_f, max_f])
                if max_require_ships <= min_require_ships:
                    send_min_reinforce(my_attacked_planet, s_list)
                    my_attacked_planet = next(my_attacked_planets)
                elif max_require_ships <= max_reinforce:
                    send_max_reinforce(my_attacked_planet, s_list)
                    my_attacked_planet = next(my_attacked_planets)
            if max_reinforce < min_require_ships:
                # We were unable to rescue our planet during
                # the first wave of attack. We will evacuate
                # all fleets to the nearby strongest planet
                # and abandon the current planet.
                revage = False
                for f in enemy_fleets_on_the_way:
                    if (
                        state.planets[f["source_planet"]].num_ships
                        + state.distance(my_attacked_planet.ID, f["source_planet"])
                        * state.planets[f["source_planet"]].growth_rate
                        + 1
                        <= my_attacked_planet.num_ships - 1
                    ):
                        evacuate_all_fleets(
                            my_attacked_planet, state.planets[f["source_planet"]]
                        )
                        revage = True
                        break
                if not revage:
                    evacuate_all_fleets(
                        my_attacked_planet, reinforcement_planets_list[0]
                    )
            else:
                send_min_reinforce(my_attacked_planet, s_list)
            my_attacked_planet = next(my_attacked_planets)
    except StopIteration:
        return solutions
