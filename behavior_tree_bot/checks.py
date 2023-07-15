

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def test_check(state):
    return True

def be_attacked(state):
    return any(enemy_fleet for enemy_fleet in state.enemy_fleets() \
               if state.planets[enemy_fleet.destination_planet] in state.my_planets())