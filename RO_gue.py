#RO_gue

import random

############
#Parameters#
############

#The radius around the HERO that will be rendered by the render function
view_range = 10

#Length of phasing event
phasing_length = 5

#Chance each turn for entity in view to awaken if not awake
awaken_chance = 2

#########
#Classes#
#########

#The single entity class holds the hero, the enemies, and the environment
class entity(object):
	def __init__ (self, x, y, depth, symbol, inventory, base_power, base_toughness, speed, awake, flavor):
		self.x = x
		self.y = y
		self.depth = depth
		self.symbol = symbol
		self.inventory = inventory
		self.base_power = base_power
		self.base_toughness = base_toughness
		self.speed = speed
		self.turn = speed
		self.awake = awake
		#Flavor of the entity: 'actor' (HERO/NPC/enemy), 'item', or 'wall'
		self.flavor = flavor
		self.damage = 0

	#Returns the entity's effective power
	def get_power(self):
		effective_power = int(self.base_power - (0.5 * self.damage))
		return (effective_power if effective_power > 0 else 0)

	#Returns the entity's effective toughness
	def get_toughness(self):
		effective_toughness = int(self.base_toughness - (1.0 * self.damage))
		return (effective_toughness if effective_toughness > 0 else 0)

	#AI pathing towards the hero entity
	def pathing(self):
		#Only moves entities that the are within the render range
		if abs(HERO.x - self.x) <= view_range and abs(HERO.y - self.y) <= view_range:
			#If the difference in x distance between the entity and the HERO is greater, the entity moves towards the HERO in the x direction
			if abs(HERO.x - self.x) >  abs(HERO.y - self.y):
				if HERO.x > self.x:
					interact(self,[ 1, 0])
				if HERO.x < self.x:
					interact(self,[-1, 0])
			#If the difference in y distance between the entity and the HERO is greater, the entity moves towards the HERO in the y direction
			if abs(HERO.y - self.y) >  abs(HERO.x - self.x):
				if HERO.y > self.y:
					interact(self,[ 0, 1])
				if HERO.y < self.y:
					interact(self,[ 0,-1])
			#If the x and y distance to the HERO is the same, the entity randomly advances in either the x or y direction
			if abs(HERO.x - self.x) == abs(HERO.y - self.y):
				random_move = random.randrange(0,1)
				if random_move == 0:
					if HERO.x > self.x:
						interact(self,[ 1, 0])
					if HERO.x < self.x:
						interact(self,[-1, 0])
				if random_move == 1:
					if HERO.y > self.y:
						interact(self,[ 0, 1])
					if HERO.y < self.y:
						interact(self,[ 0,-1])

	#Checks to see if self is dead
	def check_death(self):
		if self.get_toughness() <= 0:
			for inventory_item in self.inventory:
				entities.append(item(self.x, self.y, self.depth, inventory_item))
			entities.remove(self)

	#How the entity is represented
	def __repr__(self):
		return(self.symbol)


#Entity type for HERO, the player character
class hero(entity):
	def __init__(self, x, y):
		entity.__init__(self, x, y, 0, '@', [], 10, 10, 10, True, 'actor')
		self.alive = True
		#Whether the HERO is phasing
		self.phasing = False
		#How much longer the HERO will be phasing for
		self.phasing_counter = 0
		#Original and target phasing depths
		self.phasing_depths = [0, 0]

	#Ticks the phasing_counter down by 1
	def phasing_countdown(self):
		if self.phasing == True:
			self.phasing_counter -= 1
		#The countdown ends and the player stabilizes on the new depth
		if self.phasing_counter <= 0:
			self.phasing = False
			self.depth = self.phasing_depths[1]

#Entity type for items
class item(entity):
	def __init__(self, x, y, depth, symbol):
		entity.__init__(self, x, y, depth, symbol, None, None, None, None, False, 'item')

#Entity type for walls
class wall(entity):
	def __init__(self, x, y, depth):
		entity.__init__(self, x, y, depth, '#', None, None, None, None, False, 'wall')

#Entity type for chests
#Treated as an actor so that they can be 'killed' and drop their items, speed is -1 so that they never have a turn
class chest(entity):
	def __init__(self, x, y, depth, inventory):
		entity.__init__(self, x, y, depth, '=', inventory, 0, 1, -1, False, 'actor')

#Entity type for kobolds
#Basic enemy unit in the game
class kobold(entity):
	def __init__(self, x, y, depth, inventory):
		entity.__init__(self, x, y, depth, 'k', inventory, 5, 25, 20, False, 'actor')

###########
#Rendering#
###########

#Colors text based based on an input_color
def color(input_text, input_color):
	#List of colors to be referenced by the color function
	colors = {
	'black'  :'\033[00m',
	'grey'   :'\033[90m',
	'white'  :'\033[97m',
	'blink'  :'\033[05m',
	'red'	:'\033[91m',
	}
	return(colors[input_color] + input_text + colors['black'])

#Renders the current game state
def render():
	#Generates an empty list of view_range * view_range
	render_world = list(list(color('+','white') for x in range(view_range * 2 + 1)) for y in range(view_range * 2 + 1))
	if HERO.phasing == False:
		#Loops through the entity list
		for entity in entities:
			#Excludes all entities not on the current depth
			if entity.depth == HERO.depth:
				#Checks to make sure that the entity is within view range of the HERO
				if abs(HERO.x - entity.x) <= view_range and abs(HERO.y - entity.y) <= view_range:
					#Places the entity in the correct spot in render_world
					render_world[HERO.y + view_range - entity.y][(view_range * 2) - (HERO.x + view_range - entity.x)] = color(input_text = entity.symbol, input_color = 'black')
	elif HERO.phasing == True:
		#Loops through the entity list for entities on the original depth
		for entity in entities:
			if entity.depth == HERO.phasing_depths[0]:
				#Checks to make sure that the entity is within view range of the HERO
				if abs(HERO.x - entity.x) <= view_range and abs(HERO.y - entity.y) <= view_range:
					#If the entity is on the original depth it's colored grey
					render_world[HERO.y + view_range - entity.y][(view_range * 2) - (HERO.x + view_range - entity.x)] = color(input_text = entity.symbol, input_color = 'grey')
		#Loops through the entity list for entities on the new depth
		for entity in entities:
			if entity.depth == HERO.phasing_depths[1]:
				#Checks to make sure that the entity is within view range of the HERO
				if abs(HERO.x - entity.x) <= view_range and abs(HERO.y - entity.y) <= view_range:
					#Checks for overlap on the two depths
					overlap = False
					if render_world[HERO.y + view_range - entity.y][(view_range * 2) - (HERO.x + view_range - entity.x)] != color('+','white'):
						overlap = True
					#If the entity is on the new depth it's red unless there's an overlap in which case it flashes
					render_world[HERO.y + view_range - entity.y][(view_range * 2) - (HERO.x + view_range - entity.x)] = color(input_text = entity.symbol, input_color = ('red' if overlap == False else 'blink'))
		#Renders the hero above everything else
		render_world[view_range][(view_range * 2) - (view_range)] = color(input_text = HERO.symbol, input_color = ('black'))
					
	#Clears the terminal
	print('\x1b[2J\x1b[H')
	#Prints render_world with a border around it
	print(color('+ ','grey') * (view_range * 2 + 3))
	for row in render_world:
		print(color('+ ','grey') + ' '.join(row) + color(' +','grey'))
	print(color('+ ','grey') * (view_range * 2 + 3))
	#Displays the HERO's current status
	print('')
	print('Location  : [%s, %s] on depth %s]' %(str(HERO.x), str(HERO.y), str(HERO.depth)))
	print('Inventory : [%s]'	%(' '.join(HERO.inventory)))
	print('Power	  : [%s%s]'  %('+' * HERO.get_power(), '_' * (HERO.base_power - HERO.get_power())))
	print('Toughness : [%s%s]'  %('+' * HERO.get_toughness(), '_' * (HERO.base_toughness - HERO.get_toughness())))
	if HERO.phasing == True:
		print(color('PHASING %s' %(HERO.phasing_counter), 'blink'))
	else:
		print('Stable')

####################
#Player interaction#
####################

#Moves the hero based on user input
def player_input():
	#Takes and stores the player's keyboard input
	current_input = input('\n' + color('INPUT','blink') + '\n').lower()
	#If the input isn't correct, the player is prompted for input
	while current_input not in list(input_table) + HERO.inventory:
		render()
		current_input = input('\nw, a, s, d to move; r and f to phase up and down; item names to use items; space to wait; quit to end the game\n').lower()
	#Movement branch
	if current_input in ('w', 'a', 's', 'd'):
		interact(current_entity = HERO, coordinate_change = input_table[current_input])
	#Phasing branch
	elif current_input in ('r', 'f'):
		#Can only begin phasing if the player is currently stable
		if HERO.phasing == False:
			HERO.phasing_counter = phasing_length
			HERO.phasing = True
			HERO.phasing_depths = [HERO.depth, (HERO.depth + 1 if current_input == 'r' else HERO.depth - 1)]
	#Item branch
	elif current_input in HERO.inventory:
		player_item(current_input = current_input)
	#Pass the turn
	elif current_input == ' ':
		pass
	#Quit the game
	elif current_input == 'quit':
		HERO.alive = False

#Controls item use
def player_item(current_input):
	HERO.inventory.remove(current_input)
	pass

################
#Game mechanics#
################

#Causes the current_entity to deal damage to the target_entity
def damage_entity(current_entity, target_entity):
	target_entity.damage += current_entity.get_power()
	target_entity.check_death()

#Holds all possible player input and converts player input into change in HERO coordinates
input_table = {
	'w'		: [ 0, 1],
	'a'		: [-1, 0],
	's'		: [ 0,-1],
	'd'		: [ 1, 0],
	'r'		: 'phase up',
	'f'		: 'phase down',
	' '		: 'wait',
	'quit'	: 'quit',
	}

#Takes an entity and a list [x, y] for coordinates as arguments
def interact(current_entity, coordinate_change):
	collision = False
	#Handles phasing collision
	if current_entity == HERO and HERO.phasing == True:
		depth_0_wall = False
		depth_1_wall = False
		#Checks the intended destination against all other entity locations
		for target_entity in entities:
			#Only checks entities on the current depth
			if target_entity.depth in HERO.phasing_depths:
				#If the intended destination is a match for any other entity, 
				if current_entity.x + coordinate_change[0] == target_entity.x and current_entity.y + coordinate_change[1] == target_entity.y:
					#If the checked entity is an item, it's added to the moving entity's inventory and removed from the entity list
					#Meaning that items will be picked up even if actors or walls also occupy the same space
					if target_entity.flavor == 'item':
						current_entity.inventory.append(target_entity.symbol)
						entities.remove(target_entity)
					#If the checked entity is not an item, the moving entity deals daamage to it equal to its get_power
					#Structured so that if somehow multiple target entities are on the same tile they will all be damaged
					if target_entity.flavor == 'actor':
						collision = True
						damage_entity(current_entity = current_entity, target_entity = target_entity)
					if target_entity.flavor == 'wall':
						if target_entity.depth == HERO.phasing_depths[0]:
							depth_0_wall = True
						else:
							depth_1_wall = True
		#Wall collisions only happen if thre's a wall on both depths
		if depth_0_wall == True and depth_1_wall == True:
			collision = True
	#Handles normal collision
	else:
		#Checks the intended destination against all other entity locations
		for target_entity in entities:
			#Only checks entities on the current depth
			if target_entity.depth == current_entity.depth:
				#If the intended destination is a match for any other entity, 
				if current_entity.x + coordinate_change[0] == target_entity.x and current_entity.y + coordinate_change[1] == target_entity.y:
					#If the checked entity is an item, it's added to the moving entity's inventory and removed from the entity list
					#Meaning that items will be picked up even if actors or walls also occupy the same space
					if target_entity.flavor == 'item':
						current_entity.inventory.append(target_entity.symbol)
						entities.remove(target_entity)
					#If the checked entity is not an item, the moving entity deals daamage to it equal to its get_power
					#Structured so that if somehow multiple target entities are on the same tile they will all be damaged
					if target_entity.flavor == 'actor':
						collision = True
						damage_entity(current_entity = current_entity, target_entity = target_entity)
					if target_entity.flavor == 'wall':
						collision = True

	#An object will move if it isn't colliding with an actor AND either it isn't colliding with a wall
	if collision == False:
		current_entity.x += coordinate_change[0]
		current_entity.y += coordinate_change[1]

#Chance to awaken if the entity is within the HERO's field of view
def awaken(current_entity):
	if current_entity.depth == HERO.depth and abs(HERO.x - current_entity.x) <= view_range and abs(HERO.y - current_entity.y) <= view_range:
		if random.randrange(awaken_chance) == 0:
			current_entity.awake = True

###############
#ASCII map gen#
###############

#Establishes the HERO entity, the player character
HERO = hero(0, 0)

#Establishes a list of entities to be looped through
entities = [HERO]

#Different ascii map symbols and their rspective object types
tile_types = {
	'@': hero,
	'#': wall,
	'k': kobold,
	'=': chest,
	'$': item,
	'.': None,
	}

#Parses the ASCII map input and places entities
def parse_map(ascii_map, entities, target_depth):
	#Splits the ASCII map into a list of rows
	ascii_map = ascii_map.split("\n")
	#Flips the row list so that the bottom row has an index of 0 instead of the top one
	ascii_map.reverse()
	#Finds the dimensions of the map
	height = len(ascii_map)
	width = len(ascii_map[0])
	#For each x and y coordinate
	for x in range(width):
		for y in range(height):
			#The tile at that particular vaue
			tile = ascii_map[y][x]
			#Generates any appropriate entities and adds them to the entity list
			if tile_types[tile] == None:
				pass
			elif tile_types[tile] == hero:
				HERO.x, HERO.y, HERO.depth = x - width//2, y - height//2, target_depth
			elif tile_types[tile] == wall:
				entity = tile_types[tile](x - width//2, y - height//2, target_depth)
				entities.append(entity)
			elif tile_types[tile] in (kobold, chest):
				entity = tile_types[tile](x - width//2, y - height//2, target_depth, [])
				entities.append(entity)
			else:
				entity = item(x - width//2, y - height//2, target_depth, tile)
				entities.append(entity)

#The ASCII map itself
map_0 = \
'''\
########################
#kkk.......#...........#
#kkkk......#...........#
#kkk.......#........$..#
#.k........#...........#
#..........#...........#
#......................#
#......................#
#......................#
#......................#
#..........k...........#
#..........k...........#
######...kkkkk....######
#..........k...........#
#..........k...........#
#......................#
#......................#
#......................#
#......................#
#..........#...........#
#..........#.........k.#
#..$.......#........kkk#
#.@........#.......kkkk#
#..........#........kkk#
########################'''

map_1 = \
'''\
########################
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#........$.#.$.........#
#..........#...........#
########################
#..........#...........#
#........$.#.$.........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
#..........#...........#
########################'''

#Calls parse_map to generate the appropriate entities
parse_map(ascii_map = map_0, entities = entities, target_depth = 0)
parse_map(ascii_map = map_1, entities = entities, target_depth = -1)

################
#Main Game Loop#
################

#One unit of time passing for the selected current_entity
def tick_entity(current_entity):
	#Only iterates through entities that are 'actors', i.e. NPCs
	if current_entity.flavor == 'actor':
		#Advances each enemy forward by one turn
		current_entity.turn -= 1
		#If the enemy's turn counter is at 0, it does stuff!
		if current_entity.turn == 0:
			#First the current_entity's turn counter is reset
			current_entity.turn = current_entity.speed
			#Only acts if the current_entity is awake
			if current_entity.awake == True:
				#If the current_entity is the HERO, it does stuff
				if current_entity == HERO:
					#Each turn decreases the phase counter until no longer phasing
					HERO.phasing_countdown()
					#Renders the current game state
					render()
					#Requests user input and tries to execute it
					player_input()
				#Otherwise if the current_entity isn't the HERO, it does other stuff
				if current_entity != HERO:
					#Calls the AI to move the current_entity
					current_entity.pathing()
			#Chance to awaken if the current_entity is asleep
			else:
				awaken(current_entity = current_entity)

#Clears the terminal window
print('\x1b[2J\x1b[H')

#A loop that holds all of the main game functions
while HERO.alive == True:
	#Loops through the entity list
	for current_entity in entities:
		if HERO.phasing == True:
			#Only iterates through entities on the current phasing depths
			if current_entity.depth in HERO.phasing_depths:
				tick_entity(current_entity = current_entity)
		else:
			#Only iterates through entities on the current depth
			if current_entity.depth == HERO.depth:
				tick_entity(current_entity = current_entity)
	#At the end of every loop, checks to see whether the HERO is dead
	HERO.check_death()

#Endstate for the game
render()
print('\n')
print('Congratulations, you lost!')