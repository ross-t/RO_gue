# RO_gue

#add UI for mage inventory

import random
import sys
import tty
import termios

# parameters
seed = 123
draw_radius = 7
draw_diameter = 2 * draw_radius + 1
max_inventory = 10

class area(object):
  def __init__(self):
    self.entities = {}
    # all entities within draw_radius of the MAGE
    self.loaded_frame = None
    self.loaded_list = None
    self.elapsed_time = 0

  def load_entities(self):
    frame = list(list(None for x in range(draw_diameter)) for y in range(draw_diameter))
    y_range = range(MAGE.y - draw_radius, MAGE.y + draw_radius)
    x_range = range(MAGE.x - draw_radius, MAGE.x + draw_radius)
    for y_index, y_value in enumerate(y_range):
      for x_index, x_value in enumerate(x_range):
        try:
          entity = self.entities[(y_value, x_value)]
          frame[y_index][x_index] = entity
        except KeyError:
          pass
    self.loaded_frame = frame
    self.loaded_list = [item for sublist in frame for item in sublist if item != None]

class entity(object):
  def __init__(self, x, y, name, symbol, color, speed, alive, entity_type, max_energy, regeneration, power, inventory):
    self.x = x
    self.y = y
    self.name = name
    self.symbol = symbol
    self.color = color
    self.speed = speed
    self.alive = alive
    self.entity_type = entity_type
    self.turn = speed
    self.max_energy = max_energy
    self.energy = max_energy
    self.regeneration = regeneration
    self.power = power
    self.inventory = inventory

  def take_turn(self):
    self.path()
    self.regenerate()

  def path(self):
    pass

  def interact(self, interact_y, interact_x):
    # if there are other entities present, then interacts
    try:
      target_entity = WORLD.entities[(interact_y, interact_x)]
      if target_entity.entity_type == 'wall':
        pass
      elif target_entity.entity_type == 'creature':
        self.fight(target_entity = target_entity)
      elif target_entity.entity_type == 'item':
        self.inventory.append(target_entity)
        del WORLD.entities[interact_y, interact_x]

    # if there are no other entities present, then moves
    except KeyError:
      WORLD.entities[(interact_y, interact_x)] = self
      del WORLD.entities[self.y, self.x]
      self.y, self.x = interact_y, interact_x

  def fight(self, target_entity):
    target_entity.energy -= self.power
    target_entity.check_death()

  def regenerate(self):
    self.energy += self.regeneration
    if self.energy > self.max_energy:
      self.energy = self.max_energy

  def check_death(self):
    if self.energy <= 0:
      self.alive = False
      self.drop_items()
      del WORLD.entities[self.y][self.x]

  def drop_items(self):
    drop_attempts = 0
    drop_radius = 5
    while len(self.inventory) > 0 and drop_attempts > 10:
      for item in self.inventory:
        y_drop = self.y + random.randrange(-draw_radius, draw_radius)
        x_drop = self.x + random.randrange(-draw_radius, draw_radius)
        # if there are no obstructions then it places the item
        try:
          obstruction = WORLD.entities[(y_drop, x_drop)]
          drop_attempts += 1 
        except KeyError:
          WORLD.entities[(y_drop, x_drop)] = item
          self.inventory.remove(item)

class wall(entity):
  def __init__(self, x, y):
    entity.__init__(self, x = x, y = y, name = 'wall', symbol = '#', color = 'black', 
                    speed = -1, alive = False, entity_type = 'wall', max_energy = 100,
                    regeneration = 0, power = 0, inventory = [])

class item(entity):
  def __init__(self, x, y, name, symbol):
    entity.__init__(self, x = x, y = y, name = name, symbol = symbol, color = 'green', 
                    speed = -1, alive = False, entity_type = 'item', max_energy = 100,
                    regeneration = 0, power = 0, inventory = [])

class kobold(entity):
  def __init__(self, x, y):
    entity.__init__(self, x = x, y = y, name = 'kobold', symbol = 'k', color = 'red',
                    speed = 5, alive = True, entity_type = 'creature', max_energy = 100,
                    regeneration = 1, power = 10, inventory = [item(None, None, 'meat', '&')])

class mage(entity):
  def __init__(self):
    entity.__init__(self, x = 0, y = 0, name = 'mage', symbol = 'M', color = 'purple',
                    speed = 5, alive = True, entity_type = 'creature', max_energy = 100,
                    regeneration = 2, power = 10, inventory = [item(None, None, 'sword', '!')])

  def take_turn(self):
    action_complete = False
    while action_complete != True:
      render()
      print(('\n' + color_text(text = 'INPUT', color = 'default') + '\n').lower())
      current_input = getch()
      action_complete = self.parse_input(user_input = current_input)
    self.regenerate()

  def parse_input(self, user_input):
    if user_input in direction_table:
      movement = direction_table[user_input]
      self.interact(interact_y = self.y + movement[0], interact_x = self.x + movement[1])
      return True
    elif user_input == 's':
      self.regenerate()
      return True
    elif user_input == '?':
      print(clear_screen)
      print(help_screen)
      getch()
      return False
    elif user_input == 'Q':
      self.alive = False
      return True
    else:
      return False


# user input
direction_table = {
  'q': (-1, -1), 'w': (-1,  0), 'e': (-1, +1),
  'a': ( 0, -1),                'd': ( 0, +1),
  'z': (+1, -1), 'x': (+1,  0), 'c': (+1, +1)}

def getch(): # https://github.com/joeyespo/py-getch
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

help_screen = """
controls

movement     ? : help
q  w  e      s : wait and regenerate
 \ | /       .
a - - d      .
 / | \       .
a  s  d      Q : quit

to attack, walk into enemies
to pick up items, walk into them

energy is used to fight and cast spells
energy is depleted by taking damage
when you run out of energy you die

[press any key to continue]
"""

# rendering
clear_screen = '\x1b[2J\x1b[H'

def color_text(text, color):
  colors = {
    'default' :'\033[00m',
    'black'   :'\033[30m',
    'ltgrey'  :'\033[37m',
    'dkgrey'  :'\033[90m',
    'red'     :'\033[31m',
    'green'   :'\033[32m',
    'yellow'  :'\033[33m',
    'blue'    :'\033[34m',
    'purple'  :'\033[35m',
    'cyan'    :'\033[36m'}

  return colors[color] + text

def render():
  WORLD.load_entities()
  render_frame = list(list(color_text('.', 'ltgrey') for x in range(draw_diameter)) for y in range(draw_diameter))
  for y in range(draw_diameter):
    for x in range(draw_diameter):
      if WORLD.loaded_frame[y][x] != None:
        render_frame[y][x] = color_text(text = WORLD.loaded_frame[y][x].symbol, color = WORLD.loaded_frame[y][x].color)
 
  map_elements = []
  map_elements.append(color_text(text = '- ', color = 'dkgrey') * (draw_radius * 2 + 3))
  for row in render_frame:
    map_elements.append(color_text(text = '| ', color = 'dkgrey') + ' '.join(row) + color_text(text = ' |' , color = 'dkgrey'))
  map_elements.append(color_text(text = '- ', color = 'dkgrey') * (draw_radius * 2 + 3))

  ui_elements = []
  total_pips = 10 
  current_pips = int(MAGE.energy / (MAGE.max_energy / total_pips))
  ui_elements.append('Energy  : [%s%s] %s/%s'  %('+' * current_pips, '_' * (total_pips - current_pips), MAGE.energy, MAGE.max_energy))
  ui_elements.append('Location: [%s, %s]' %(str(MAGE.x), str(MAGE.y * -1)))
  ui_elements.append('Time    : %s' %(WORLD.elapsed_time))

  inventory_elements = []

  # write to terminal
  print(clear_screen)
  for line in map_elements + ui_elements:
    print(line)

# initialization
if seed:
  random.seed(seed)

WORLD = area()
MAGE = mage()
WORLD.entities[(MAGE.y, MAGE.x)] = MAGE

#
# test area
#

WORLD.entities[(-5, 0)] = wall(-5, 0)
WORLD.entities[( 5, 0)] = kobold( 5, 0)

#
# /test area
#

# more initialization
WORLD.load_entities()

# main loop
while MAGE.alive == True:
  WORLD.elapsed_time += 1
  for entity in WORLD.loaded_list:
    if entity.alive == True:
      entity.turn -= 1
      if entity.turn == 0:
        entity.turn = entity.speed
        entity.take_turn()


