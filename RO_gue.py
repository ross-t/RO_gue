#RO_gue

# currently in progress:
# making raw files for items and other entities

import math
import random

############
#Parameters#
############

#The radius around the HERO that will be rendered by the render function
view_range = 15
#Length of phasing event
phasing_length = 5
#Chance each turn for entity in view to awaken if not awake
awaken_chance = 1
#Length of the log display on screen
log_length = 5
#Size within which the world will try to place the dungeon
floor_size = 50
#Mininum and maximum room side dimension
room_min = 5
room_max = 10
#The number of room attempts made in floor generation
room_attempts = 50
#Number of enemies and items spawned per floor
enemy_spawn = 15
item_spawn = 2

# paths to 
enemies_path = 'raws.enemies.txt'
items_path = 'raws.items.txt'

##################
#World Generation#
##################

#Class to hold an individual game floor
class floor(object):
	def __init__(self, number):
		self.number = number
		self.entities = []

	#Generates the floor randomly
	def generate(self):
		#Attempts to place empty rooms in the floor
		def make_room(floor):
			#Dimensions for the room
			x_dim = random.randrange(room_min, room_max)
			y_dim = random.randrange(room_min, room_max)
			#Placement for the room
			x_placement = random.randrange(1, floor_size - x_dim)
			y_placement = random.randrange(1, floor_size - y_dim)
			#Lists of x and y coordinates covered by the room
			tiles_x = list(x + x_placement for x in range(x_dim))
			tiles_y = list(y + y_placement for y in range(y_dim))
			#Replaces walls with empty space with the defined parameters
			for y in tiles_y:
				for x in tiles_x:
					floor[y][x] = '.'

		#Make a full floor with floor_size dimensions
		gen_floor = list(['#'] * floor_size for x in range(floor_size))

		#Generates empty rooms within the floor
		for x in range(room_attempts):
			make_room(floor = gen_floor)

		#Tries to place the HERO if this is the first floor generated
		if len(WORLD) == 1:
			while True:
				hero_x = random.randrange(1, floor_size)
				hero_y = random.randrange(1, floor_size)
				if gen_floor[hero_y][hero_x] == '.':
					gen_floor[hero_y][hero_x] = '@'
					break

		#Spawns enemies on the current floor
		enemy_count = 0
		while enemy_count < enemy_spawn:
			enemy_x = random.randrange(1, floor_size)
			enemy_y = random.randrange(1, floor_size)
			if gen_floor[enemy_y][enemy_x] == '.':
				spawn_enemy = enemy_list[random.randrange(len(enemy_list))]
				gen_floor[enemy_y][enemy_x] = spawn_enemy
				enemy_count += 1

		#Spawns items on the current floor
		item_count = 0
		while item_count < item_spawn:
			item_x = random.randrange(1, floor_size)
			item_y = random.randrange(1, floor_size)
			if gen_floor[item_y][item_x] == '.':
				spawn_item = item_list[random.randrange(len(item_list))]
				gen_floor[item_y][item_x] = spawn_item
				item_count += 1

		#Places entities in the entities list
		#For each x and y coordinate
		for x in range(floor_size):
			for y in range(floor_size):
				#The tile at that particular value
				tile = gen_floor[y][x]
				#Generates any appropriate entities and adds them to the entity list
				if tile == '@':
					HERO.x, HERO.y, HERO.depth = x, y, self.number
				elif tile == '#':
					self.entities.append(wall(x = x, y = y, depth = self.number))
				elif tile == 'k':
					self.entities.append(kobold(x = x, y = y, depth = self.number, inventory = []))
				elif tile == '$':
					self.entities.append(item(x = x, y = y, depth = self.number, symbol = '$'))

		#Visualizes the floor in ascii before it's made into entities
		#print('\n'.join(''.join(x) for x in gen_floor) + '\n')

	#How the floor is represented
	def __repr__(self):
		return(self.number)

##########
#Entities#
##########

#The single entity class holds the hero, the enemies, and the environment
class entity(object):
	def __init__ (self, x, y, depth, symbol, inventory, base_power, base_toughness, speed, awake, flavor, name):
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
		self.name = name
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
		#Only moves entities that are within the render range
		if abs(HERO.x - self.x) <= view_range and abs(HERO.y - self.y) <= view_range:
			#All neighbouring cells [actual x, actual y, relative x, relative y]
			candidates = [[self.x - 1, self.y, -1, 0], [self.x + 1, self.y, 1, 0], [self.x, self.y - 1, 0, -1], [self.x, self.y + 1, 0, 1]]
			#Iterates through them and removes ones that are occupied by anything besides the HERO
			for candidate in candidates:
				for target_entity in WORLD[self.depth].entities:
					if target_entity.x == candidate[0] and target_entity.y == candidate[1]:
						if target_entity != HERO and target_entity.flavor != 'item':
							if candidate in candidates:
								candidates.remove(candidate)

			#Gets the distance of each candidate from the HERO position
			distances = list(math.sqrt((HERO.x - candidate[0])**2 + (HERO.y - candidate[1])**2) for candidate in candidates)
			#Returns the valid candidate neighbouring cell with the lowest distance to the HERO
			interact(self, candidates[distances.index(min(distances))][2:4])

	#Checks to see if self is dead
	def check_death(self):
		if self.get_toughness() <= 0:
			for inventory_item in self.inventory:
				WORLD[self.depth].entities.append(item(x = self.x, y = self.y, depth = self.depth, symbol = inventory_item))
				log.add('the %s drops the %s' %(self, inventory_item))
			if self == HERO:
				log.add('you die')
				self.alive = False
				WORLD[self.depth].entities.remove(self)
			else:
				log.add('the %s dies' %(self))
				WORLD[self.depth].entities.remove(self)

	#How the entity is represented
	def __repr__(self):
		return(self.name)

#HERO, the player entity
class hero(entity):
	def __init__(self):
		entity.__init__(self, 0, 0, 0, '@', ['$'], 10, 10, 10, True, 'actor', 'hero')
		self.alive = True
		#Whether the HERO is phasing
		self.phasing = False
		#How much longer the HERO will be phasing for
		self.phasing_counter = 0
		#Original and target phasing depths
		self.phasing_depths = [0, 0]
		#Sneak stat which modifies how easily enemies wake up
		self.sneak = 3

	#Ticks the phasing_counter down by 1
	def phasing_countdown(self):
		if self.phasing == True:
			self.phasing_counter -= 1
			#The countdown ends and the player stabilizes on the new depth
			if self.phasing_counter <= 0:
				self.phasing = False
				WORLD[self.depth].entities.remove(self)
				self.depth = self.phasing_depths[1]
				WORLD[self.depth].entities.append(self)
				log.add('you stabilize on depth %s' %(self.depth))

#items entities
class item(entity):
	def __init__(self, x, y, depth, symbol):
		entity.__init__(self, x, y, depth, symbol, None, None, None, None, False, 'item', 'item')

#wall entities
class wall(entity):
	def __init__(self, x, y, depth):
		entity.__init__(self, x, y, depth, '#', None, None, None, None, False, 'wall', 'wall')

#chest entitites
#Treated as an actor so that they can be 'killed' and drop their items, speed is -1 so that they never have a turn
class chest(entity):
	def __init__(self, x, y, depth, inventory):
		entity.__init__(self, x, y, depth, '=', inventory, None, 1, -1, False, 'actor', 'chest')

#kobold entities
#Basic enemy unit in the game
class kobold(entity):
	def __init__(self, x, y, depth, inventory):
		entity.__init__(self, x, y, depth, 'k', inventory, 7, 20, 20, False, 'actor', 'kobold')

#Log of in-game actions
class log(object):
	def __init__(self):
		self.current = ['you wake up on floor 0']
		self.past = []

	#Moves the current log data to the past log data
	def clear(self):
		self.past += self.current
		self.current = []

	#Adds a new log to current
	def add(self, entry):
		self.current.append(entry)

	#How the entity is represented
	def __repr__(self):
		if HERO.alive == True:
			return('\n'.join(self.current[:log_length]) + ('\n...' if len(self.current) > log_length else ''))
		else:
			self.clear()
			return('\n'.join(self.past))


###########
#Rendering#
###########

#Colors text based based on an input_color
def color(input_text, input_color):
	#List of colors to be referenced by the color function
	colors = {
	'black'  :'\033[01m',
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
		#Loops through the entity list for the current floor
		for entity in WORLD[HERO.depth].entities:
			#Checks to make sure that the entity is within view range of the HERO
			if abs(HERO.x - entity.x) <= view_range and abs(HERO.y - entity.y) <= view_range:
				#Places the entity in the correct spot in render_world
				render_world[HERO.y + view_range - entity.y][(view_range * 2) - (HERO.x + view_range - entity.x)] = color(input_text = entity.symbol, input_color = 'black')
	elif HERO.phasing == True:
		#Loops through the entity list for entities on the original depth
		for entity in WORLD[HERO.phasing_depths[0]].entities:
			#Checks to make sure that the entity is within view range of the HERO
			if abs(HERO.x - entity.x) <= view_range and abs(HERO.y - entity.y) <= view_range:
				#If the entity is on the original depth it's colored grey
				render_world[HERO.y + view_range - entity.y][(view_range * 2) - (HERO.x + view_range - entity.x)] = color(input_text = entity.symbol, input_color = 'grey')
		#Loops through the entity list for entities on the new depth
		for entity in WORLD[HERO.phasing_depths[1]].entities:
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
	print('Location  : [%s, %s] on depth %s' %(str(HERO.x), str(HERO.y), str(HERO.depth)))
	print('Inventory : [%s]'	%(' '.join(HERO.inventory)))
	print('Power	  : [%s%s]'  %('+' * HERO.get_power(), '_' * (HERO.base_power - HERO.get_power())))
	print('Toughness : [%s%s]'  %('+' * HERO.get_toughness(), '_' * (HERO.base_toughness - HERO.get_toughness())))
	if HERO.phasing == True:
		print(color('\nPHASING %s\n' %(HERO.phasing_counter), 'blink'))
	else:
		print('\nstable\n')
	print(log)
	log.clear()


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
			log.add('you begin phasing ' + ('up' if current_input == 'r' else 'down' ))
			#If the new floor doesn't exist: generates it
			if HERO.phasing_depths[1] not in WORLD:
				WORLD[HERO.phasing_depths[1]] = floor(HERO.phasing_depths[1])
				WORLD[HERO.phasing_depths[1]].generate()

	#Item branch
	elif current_input in HERO.inventory:
		player_item(current_input = current_input)
	#Pass the turn
	elif current_input == ' ':
		log.add('you wait')
	#Quit the game
	elif current_input == 'quit':
		log.add('you resign')
		HERO.alive = False

#Controls item use
def player_item(current_input):
	HERO.inventory.remove(current_input)
	log.add('you use the %s' %(current_input))
	if current_input == '$':
		HERO.damage = 0

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
		#Checks the intended destination against all other entity locations on both phasing_depths
		for target_entity in WORLD[HERO.phasing_depths[0]].entities + WORLD[HERO.phasing_depths[1]].entities:
			#If the intended destination is a match for any other entity, 
			if current_entity.x + coordinate_change[0] == target_entity.x and current_entity.y + coordinate_change[1] == target_entity.y:
				#If the checked entity is an item, it's added to the moving entity's inventory and removed from the entity list
				#Meaning that items will be picked up even if actors or walls also occupy the same space
				if target_entity.flavor == 'item':
					current_entity.inventory.append(target_entity.symbol)
					log.add('the %s picks up the %s' %(current_entity, target_entity.symbol))
					WORLD[target_entity.depth].entities.remove(target_entity)
				#If the checked entity is not an item, the moving entity deals daamage to it equal to its get_power
				#Structured so that if somehow multiple target entities are on the same tile they will all be damaged
				if target_entity.flavor == 'actor':
					collision = True
					#No infighting within species, only between them
					if type(target_entity) != type(current_entity):
						log.add('the %s attacks the %s' %(current_entity, target_entity))
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
		#Checks the intended destination against all other entity locations on the same depth as the hero
		for target_entity in WORLD[HERO.depth].entities:
			#If the intended destination is a match for any other entity, 
			if current_entity.x + coordinate_change[0] == target_entity.x and current_entity.y + coordinate_change[1] == target_entity.y:
				#If the checked entity is an item, it's added to the moving entity's inventory and removed from the entity list
				#Meaning that items will be picked up even if actors or walls also occupy the same space
				if target_entity.flavor == 'item':
					current_entity.inventory.append(target_entity.symbol)
					log.add('the %s picks up the %s' %(current_entity, target_entity.symbol))
					WORLD[target_entity.depth].entities.remove(target_entity)
				#If the checked entity is not an item, the moving entity deals daamage to it equal to its get_power
				#Structured so that if somehow multiple target entities are on the same tile they will all be damaged
				if target_entity.flavor == 'actor':
					collision = True
					#No infighting within species, only between them
					if type(target_entity) != type(current_entity):
						log.add('the %s attacks the %s' %(current_entity, target_entity))

						damage_entity(current_entity = current_entity, target_entity = target_entity)
				if target_entity.flavor == 'wall':
					collision = True

	#An object will move if it isn't colliding with an actor AND either it isn't colliding with a wall
	if collision == False:
		current_entity.x += coordinate_change[0]
		current_entity.y += coordinate_change[1]

#Chance to awaken if the entity is within the HERO's field of view
def awaken(current_entity):
	if abs(HERO.x - current_entity.x) <= view_range and abs(HERO.y - current_entity.y) <= view_range:
		if random.randrange(awaken_chance * (HERO.sneak if current_entity != HERO else 1)) == 0:
			current_entity.awake = True
			log.add('the %s wakes up' %(current_entity))

################
#Main Game Loop#
################

#Makes the hero
HERO = hero()

#Initial map and floor generation
WORLD = {0:floor(0)}
WORLD[0].generate()
WORLD[0].entities.append(HERO)

#Log for actions since the last turn
log = log()

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
				else:
					#Calls the AI to move the current_entity
					current_entity.pathing()
			#Chance to awaken if the current_entity is asleep
			else:
				awaken(current_entity = current_entity)

#Clears the terminal window
print('\x1b[2J\x1b[H')

#A loop that holds all of the main game functions
while HERO.alive == True:
	#Behaves differently depending on whether or not the HERO is phasing
	if HERO.phasing == True:
		#Only iterates through entities on the current phasing depths
		for current_entity in WORLD[HERO.phasing_depths[0]].entities:
			tick_entity(current_entity = current_entity)
		for current_entity in WORLD[HERO.phasing_depths[1]].entities:
			tick_entity(current_entity = current_entity)
	elif HERO.phasing == False:
		#Only iterates through entities on the current depth
		for current_entity in WORLD[HERO.depth].entities:
			tick_entity(current_entity = current_entity)
	#TESTING
	#break

#Endstate for the game
render()
print('\nCongratulations, you lost!\n')
