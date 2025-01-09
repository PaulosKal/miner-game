import arcade
import random
import time

#game preferences
screen_width = 1080
screen_height = 768
map_size = 30 #recommended: 30  max: 100
map_range = 2  #recommended: 2  min: 1
size = 5  #recommended: 5
speed = 4  #recommended: 4
ore_capacity = 10  #per upgrade class. Recommended: 10
fuel_capacity = 100  #per upgrade class. Recommended: 100
allowed_depth = 14  #per upgrade class. Recommended: 2*number_of_ver_blocks/9
damage_withstanding = 25  #per upgrade class. Recommended: 25
number_of_hor_blocks = 18  #recommended: odd number, >= 18
number_of_ver_blocks = 63  #recommended: 63  allowed: 9*k
hiden_map = False
starting_money = 200  #recommended: 200
blocks = [["Vectors/Blocks/Bedrock.png", 1, arcade.color.BATTLESHIP_GREY], ["Vectors/Blocks/Dirt.png", 2, arcade.color.CHAMOISEE], ["Vectors/Blocks/Stone.png", 4, arcade.color.LAVENDER_GRAY], ["Vectors/Blocks/Coal.png", 4, arcade.color.CHARCOAL, 50], ["Vectors/Blocks/Iron.png", 4, arcade.color.WHEAT, 80], ["Vectors/Blocks/Lapis_lazuli.png", 4, arcade.color.UA_BLUE, 100], ["Vectors/Blocks/Gold.png", 4, arcade.color.GOLD, 170], ["Vectors/Blocks/Redstone.png", 4, arcade.color.CANDY_APPLE_RED, 250], ["Vectors/Blocks/Diamond.png", 4, arcade.color.DIAMOND, 400], ["Vectors/Blocks/Emerald.png", 4, arcade.color.HARLEQUIN, 600]]  #[[Path, resistance, map_color, value], [Path, resistance, map_color, value], ...]
probability = [[6966, 11685, 97742, 98593, 99082, 99113, 99209, 99910, 99997, 100000], [5922, 11702, 97245, 98288, 98873, 98946, 99066, 99893, 99995, 100000], [4923, 10657, 97573, 98611, 99201, 99273, 99391, 99926, 99995, 100000], [4964, 10660, 98224, 99248, 99846, 99877, 99995, 0, 0, 100000], [3988, 9584, 98263, 99294, 99881, 99886, 99993, 0, 0, 100000], [3000, 8669, 98368, 99402, 99998, 0, 100000, 0, 0, 0], [3000, 8760, 98391, 99420, 100000, 0, 0, 0, 0, 0], [1000, 15310, 98542, 99464, 100000, 0, 0, 0, 0, 0], [0, 78861, 98577, 99482, 100000, 0, 0, 0, 0, 0]]  #[Bedrock, Dirt, ...], [Bedrock, Dirt, ...], ...]

#game hotkeys
map_hide_key = arcade.key.M
reset_key = arcade.key.R
activate_key = arcade.key.E

#do not touch anything bellow this line!
#---------------------------------------------------------------------------------------------------------

#adjust values to adapt in game standards
map_size /= 100
block_size = 16*size
map_block_size = map_size*block_size/map_range
map_diamensions = [int(screen_width*map_size/map_block_size), int(screen_height*map_size/map_block_size)]
speed *= 4
if(number_of_hor_blocks%2 == 1):
	starting_x = block_size*number_of_hor_blocks//2
else:
	starting_x = block_size*number_of_hor_blocks//2 - block_size//2
starting_y = block_size*number_of_ver_blocks + block_size//2

#initialise list of position of blocks
coordinations = []
for j in range(number_of_ver_blocks + 2):
	temp_cords = []
	for i in range(number_of_hor_blocks + 2):
		if(j == 0 or i == 0 or i == number_of_hor_blocks + 1):
			temp_cords.append(0)
		else:
			temp_cords.append(-1)
	coordinations.append(temp_cords)

#garage is the only building that uses more than one texture
garage_closed = arcade.load_texture("Vectors/Buildings/Garage_closed.png")
garage_open = arcade.load_texture("Vectors/Buildings/Garage_open.png")

#load sounds
sound_engine = arcade.load_sound("Sounds/Engine.mp3")
sound_drill = arcade.load_sound("Sounds/Drill.mp3")
sound_dirt = arcade.load_sound("Sounds/Dirt.mp3")
sound_stone = arcade.load_sound("Sounds/Stone.mp3")
sound_ore = arcade.load_sound("Sounds/Ore.mp3")

class MyGame(arcade.Window):
	def __init__(self, width, height, title):
		#initialise game window and basic parameters to use
		super().__init__(width, height, title)
		self.left_boundary = 0
		self.right_boundary = screen_width
		self.bottom_boundary = 0
		self.top_boundary = screen_height
		self.brightness = 100
		self.message = [0, ""]
		self.cash = starting_money
		self.building_touch = "None"
		self.excavator_list = None
		self.block_list = None
		self.set_mouse_visible(False)
		self.hiden_map = hiden_map
		self.garage_menu = False
		self.sound_engine_player = None
		self.sound_drill_player = None

	def setup(self):
		#excavator characteristics
		self.excavator_list = arcade.SpriteList()
		self.excavator = arcade.Sprite("Vectors/Excavator.png", size/5)
		self.excavator.center_x = starting_x
		self.excavator.center_y = starting_y
		self.excavator.upgrade_class = 1
		self.excavator.speed = speed*self.excavator.upgrade_class
		self.excavator.ore_capacity = ore_capacity*self.excavator.upgrade_class
		self.excavator.fuel_capacity = fuel_capacity*self.excavator.upgrade_class
		self.excavator.allowed_depth = allowed_depth*self.excavator.upgrade_class
		self.excavator.damage_withstanding = damage_withstanding*self.excavator.upgrade_class
		self.excavator.depth = 0
		self.excavator.damage = 0
		self.excavator.ores = []
		self.excavator.fuel = self.excavator.fuel_capacity
		self.excavator.pos = [0, 0]
		self.excavator.pos[0] = (starting_x - block_size//2)//block_size + 1
		self.excavator.pos[1] = (starting_y - block_size//2)//block_size + 1
		self.excavator.target_x = self.excavator.pos[0]
		self.excavator.target_y = self.excavator.pos[1]
		self.excavator_list.append(self.excavator)
		
		#buildings
		self.buildings_list = arcade.SpriteList()
		self.garage = arcade.Sprite("Vectors/Buildings/Garage_closed.png", size/3.205128)
		self.garage.center_x = starting_x - 6*block_size
		self.garage.center_y = starting_y
		self.buildings_list.append(self.garage)
		self.fuel_station = arcade.Sprite("Vectors/Buildings/Fuel_station.png", size/5.9375)
		self.fuel_station.center_x = starting_x
		self.fuel_station.center_y = starting_y
		self.buildings_list.append(self.fuel_station)
		self.metal_factory = arcade.Sprite("Vectors/Buildings/Metal_factory.png", size/13.765648)
		self.metal_factory.center_x = starting_x + 7*block_size
		self.metal_factory.center_y = starting_y
		self.buildings_list.append(self.metal_factory)

		#blocks - where the game world is built
		self.block_list = arcade.SpriteList()
		for j in range(number_of_ver_blocks + 1):
			for i in range(2):
				self.block = arcade.Sprite(blocks[0][0], size)
				self.block.center_x = i*(number_of_hor_blocks*block_size + block_size//2) + (i - 1)*block_size//2
				self.block.center_y = j*block_size + block_size//2
				self.block.resistance = blocks[0][1]
				self.block_list.append(self.block)
		for i in range(number_of_hor_blocks + 2):
			self.block = arcade.Sprite(blocks[0][0], size)
			self.block.center_x = i*block_size - block_size//2
			self.block.center_y = -block_size//2
			self.block.resistance = blocks[0][1]
			self.block_list.append(self.block)
		for j in range(number_of_ver_blocks):   #block generator
			for i in range(number_of_hor_blocks):
				layer = j//(number_of_ver_blocks//9)
				block_id = random.randint(1, 100000)
				for k in range(len(blocks)): #block types
					if(block_id <= probability[layer][k]):
						self.block = arcade.Sprite(blocks[k][0], size)
						self.block.center_x = i*block_size + block_size//2
						self.block.center_y = j*block_size + block_size//2
						coordinations[j + 1][i + 1] = k
						self.block.resistance = blocks[k][1]
						self.block_list.append(self.block)
						break

		#start playing engine sound
		self.sound_engine_player = sound_engine.play(volume = 0.5, loop = True)

	def on_draw(self):
		arcade.start_render()

		#buildings, blocks and excavator
		self.buildings_list.draw()
		self.block_list.draw()
		self.excavator_list.draw()

		#Text values and runtime messages
		arcade.draw_text("Cash: {}$".format(self.cash), self.left_boundary + 10, self.bottom_boundary + 30, arcade.color.WHITE, 14, bold = True)
		
		if(self.excavator.allowed_depth >= self.excavator.depth):
			k = arcade.color.WHITE
		else:
			k = arcade.color.RED
		arcade.draw_text("Depth: {}".format(self.excavator.depth), self.left_boundary + 10, self.bottom_boundary + 10, k, 14, bold = True)
		
		if(self.excavator.damage <= 0.33*self.excavator.damage_withstanding):
			k = arcade.color.WHITE
		elif(self.excavator.damage <= 0.66*self.excavator.damage_withstanding):
			k = arcade.color.YELLOW
		else:
			k = arcade.color.RED
		arcade.draw_text("Damage: {}%".format(int(self.excavator.damage/self.excavator.damage_withstanding*100)), self.right_boundary - 105, self.bottom_boundary + 50, k, 14, bold = True)
		
		if(self.excavator.fuel > 0.15*self.excavator.fuel_capacity):
			k = arcade.color.WHITE
		else:
			k = arcade.color.RED
		arcade.draw_text("Fuel: {}%".format(int(self.excavator.fuel/self.excavator.fuel_capacity*100)), self.right_boundary - 97, self.bottom_boundary + 30, k, 14, bold = True)
		
		if(len(self.excavator.ores) < self.excavator.ore_capacity):
			k = arcade.color.WHITE
		else:
			k = arcade.color.RED
		arcade.draw_text("Ores: {}/{}".format(len(self.excavator.ores), self.excavator.ore_capacity), self.right_boundary - 100, self.bottom_boundary + 10, k, 14, bold = True)
		
		if(time.time() - self.message[0] < 2):  #display messages created less than 2 seconds ago
			arcade.draw_text(self.message[1], self.left_boundary + 10, self.top_boundary - 20 - 15*(self.message[1].count("\n")), arcade.color.GREEN, 14, bold = True)
		
		#user visited garage and chooses between options
		if(self.garage_menu):
			k = "1. Repair\n2. Upgrade - Cost: {}$".format(300*self.excavator.upgrade_class)
			arcade.draw_text(k, self.left_boundary + 10, self.top_boundary - 20 - 15*(k.count("\n")), arcade.color.WHITE, 14, bold = True)

		#draw map at specific place, size, diamensions number/colour of blocks
		if(not self.hiden_map):
			for j in range(map_diamensions[1]):
				for i in range(map_diamensions[0]):
					if(self.excavator.pos[1] + map_diamensions[1]//2 - j >= 0 and self.excavator.pos[0] - map_diamensions[0]//2 + i >= 0):
						try:
							if(coordinations[self.excavator.pos[1] + map_diamensions[1]//2 - j][self.excavator.pos[0] - map_diamensions[0]//2 + i] >= 0):
								k = blocks[coordinations[self.excavator.pos[1] + map_diamensions[1]//2 - j][self.excavator.pos[0] - map_diamensions[0]//2 + i]][2]
							else:
								k = arcade.color.BLACK
						except IndexError:
							k = arcade.color.BLACK
					else:
						k = arcade.color.BLACK
					arcade.draw_point(self.excavator.center_x - screen_width*map_size//2 + map_block_size/2 + i*map_block_size, self.excavator.center_y + screen_height//2 - map_block_size/2 - j*map_block_size, k, map_block_size)
					if(i == map_diamensions[0]//2 and j == map_diamensions[1]//2):
						arcade.draw_point(self.excavator.center_x - screen_width*map_size//2 + map_block_size/2 + i*map_block_size, self.excavator.center_y + screen_height//2 - map_block_size/2 - j*map_block_size, arcade.color.RED, map_block_size//2)

	def on_key_press(self, key, modifiers):
		if(not self.garage_menu):  #garage menu should be closed
			
			#calculate target block
			if(self.excavator.change_x == 0 and self.excavator.change_y == 0):
				if(key == arcade.key.UP):
					self.excavator.angle = 90
					if(self.excavator.pos[1] < number_of_ver_blocks + 1):
						self.excavator.target_y = self.excavator.pos[1] + 1
				elif(key == arcade.key.DOWN):
					self.excavator.angle = -90
					if(self.excavator.pos[1] > 1):
						self.excavator.target_y = self.excavator.pos[1] - 1
				elif(key == arcade.key.LEFT):
					self.excavator.angle = 180
					if(self.excavator.pos[0] > 1):
						self.excavator.target_x = self.excavator.pos[0] - 1
				elif(key == arcade.key.RIGHT):
					self.excavator.angle = 0
					if(self.excavator.pos[0] < number_of_hor_blocks):
						self.excavator.target_x = self.excavator.pos[0] + 1
				k = coordinations[self.excavator.target_y][self.excavator.target_x]
				
				#decide if moving is allowed or display errors
				if(k == 0):
					self.message[0] = time.time()
					self.message[1] = "You can't break bedrock!"
					self.excavator.target_x = self.excavator.pos[0]
					self.excavator.target_y = self.excavator.pos[1]
				if(len(self.excavator.ores) == self.excavator.ore_capacity and k > 2):
					self.message[0] = time.time()
					self.message[1] = "No more space onboard!"
					self.excavator.target_x = self.excavator.pos[0]
					self.excavator.target_y = self.excavator.pos[1]
				if((k != -1 and self.excavator.fuel < blocks[k][1]/2 + 0.25) or self.excavator.fuel < 0.25):
					
					#problem with stopping sounds, I will try to fix that later
					#if(self.sound_engine_player):
						#sound_engine.stop(self.sound_engine_player)  #engine stop
					
					self.message[0] = time.time()
					self.message[1] = "Not enough fuel!"
					self.excavator.target_x = self.excavator.pos[0]
					self.excavator.target_y = self.excavator.pos[1]
				if(self.excavator.damage > self.excavator.damage_withstanding):
					self.message[0] = time.time()
					self.message[1] = "You damaged your excavator!"
					self.excavator.target_x = self.excavator.pos[0]
					self.excavator.target_y = self.excavator.pos[1]
			
			#resetting the excavator if damaged - costs a fortune, ores collected are lost
			if(key == reset_key):
				if(self.cash >= 1000):
					self.excavator.center_x = starting_x
					self.excavator.center_y = starting_y
					self.excavator.damage = 0
					self.excavator.ores = []
					self.excavator.fuel = self.excavator.fuel_capacity
					self.excavator.pos[0] = (starting_x - block_size//2)//block_size + 1
					self.excavator.pos[1] = (starting_y - block_size//2)//block_size + 1
					self.excavator.target_x = self.excavator.pos[0]
					self.excavator.target_y = self.excavator.pos[1]
					self.cash -= 1000 + 100*self.excavator.depth
					self.message[0] = time.time()
					self.message[1] = "Excavator reset: -{}$".format(1000 + 100*self.excavator.depth)
					self.excavator.depth = 0
				else:
					self.message[0] = time.time()
					self.message[1] = "Not enough money!"
			
			if(key == activate_key):

				#repair or upgrade equipment
				if(self.building_touch == "Garage"):
					self.garage_menu = True
				
				#fill the excavator with fuel
				elif(self.building_touch == "Fuel station"):
					k = int(self.excavator.fuel_capacity - self.excavator.fuel)  #missing fuel
					if(self.cash >= 2*k):  #2 dollars per liter
						#fill it up to the brim
						self.excavator.fuel += k
						self.cash -= 2*k
						self.message[0] = time.time()
						self.message[1] = "Fuel costs: -{}$".format(2*k)
					elif(self.cash > 0):
						#fill it up depending on your money
						k = self.cash
						self.excavator.fuel += self.cash/2
						self.cash = 0
						self.message[0] = time.time()
						self.message[1] = "Fuel costs: -{}$".format(k)
					else:
						self.message[0] = time.time()
						self.message[1] = "Not enough money!"
				
				#sell ores depending on their prices
				elif(self.building_touch == "Metal factory"):
					ore_cash = 0
					for ore in self.excavator.ores:
						ore_cash += blocks[ore][3]
					self.excavator.ores = []
					self.cash += ore_cash
					self.message[0] = time.time()
					self.message[1] = "Sold ores: +{}$".format(ore_cash)
		
		else:  #garage menu is open, waiting for option
			if(key == arcade.key.KEY_1):
				
				#repair excavator
				k = int(self.excavator.damage)
				if(self.cash >= 30*k):  #30 dollars per 1 damage
					#set damage to 0%
					self.excavator.damage = 0
					self.cash -= 30*k
					self.message[0] = time.time()
					self.message[1] = "Repairing costs: -{}$".format(30*k)
				elif(self.cash > 0):
					#fix it as much as you can afford
					k = self.cash
					self.excavator.damage -= self.cash/30
					self.cash = 0
					self.message[0] = time.time()
					self.message[1] = "Repairing costs: -{}$".format(k)
				else:
					self.message[0] = time.time()
					self.message[1] = "Not enough money!"
			
			elif(key == arcade.key.KEY_2):
				
				#upgrade class - costs 300 dollars times current class
				k = 300*self.excavator.upgrade_class
				if(self.cash >= k):
					self.excavator.upgrade_class += 1
					self.excavator.speed = speed*self.excavator.upgrade_class
					self.excavator.ore_capacity = ore_capacity*self.excavator.upgrade_class
					self.excavator.fuel_capacity = fuel_capacity*self.excavator.upgrade_class
					self.excavator.allowed_depth = allowed_depth*self.excavator.upgrade_class
					self.excavator.damage_withstanding = damage_withstanding*self.excavator.upgrade_class
					self.message[0] = time.time()
					self.message[1] = "Upgrading costs: -{}$".format(k)
				else:
					self.message[0] = time.time()
					self.message[1] = "Not enough money!"

			else:
				pass
			self.garage_menu = False

	def on_key_release(self, key, modifiers):
		#view or hide map
		if(key == map_hide_key):
			if(self.hiden_map):
				self.hiden_map = False
			else:
				self.hiden_map = True

	def update(self, delta_time):
		self.excavator_list.update()
		if(self.excavator.target_x != self.excavator.pos[0] or self.excavator.target_y != self.excavator.pos[1]):
			#move and destroy blocks
			
			#problem with sounds, I will try to fix that later
			#self.sound_drill_player = sound_drill.play(loop = False)
			k = 1
			blocks_hit_list = arcade.check_for_collision_with_list(self.excavator, self.block_list)
			for block in blocks_hit_list:
				k = block.resistance
			self.excavator.change_x = (self.excavator.target_x - self.excavator.pos[0])*self.excavator.speed//k
			self.excavator.change_y = (self.excavator.target_y - self.excavator.pos[1])*self.excavator.speed//k
		else:
			#when stopped, check if there is a block to destroy

			#problem with stopping sounds, I will try to fix that later
			#if(self.sound_drill_player):
				#try:
					#sound_drill.stop(self.sound_drill_player)
				#except ValueError:  #sound is already stopped
					#pass
			blocks_hit_list = arcade.check_for_collision_with_list(self.excavator, self.block_list)
			for block in blocks_hit_list:
				#destroy block (and collect ore)
				if(coordinations[self.excavator.pos[1]][self.excavator.pos[0]] == 1):  #dirt
					sound_dirt.play()
				elif(coordinations[self.excavator.pos[1]][self.excavator.pos[0]] == 2):  #stone
					sound_stone.play()
				elif(coordinations[self.excavator.pos[1]][self.excavator.pos[0]] > 2):  #ores
					sound_ore.play()
					self.excavator.ores.append(coordinations[self.excavator.pos[1]][self.excavator.pos[0]])
				coordinations[self.excavator.pos[1]][self.excavator.pos[0]] = -1
				self.excavator.fuel -= block.resistance/2
				block.kill()
			
			#check if the excavator touches any buildings
			blocks_hit_list = arcade.check_for_collision_with_list(self.excavator, self.buildings_list)
			if(blocks_hit_list == []):
				#nothing is touched by the excavator
				self.building_touch = "None"
				self.garage.texture = garage_closed
			else:
				#a building is touched
				for block in blocks_hit_list:
					if(block.center_x == self.garage.center_x):
						self.building_touch = "Garage"
						self.garage.texture = garage_open
					elif(block.center_x == self.fuel_station.center_x):
						self.garage.texture = garage_closed
						self.building_touch = "Fuel station"
					else:
						self.garage.texture = garage_closed
						self.building_touch = "Metal factory"
		
		#if moving, stop at the center of a block
		if((self.excavator.change_x > 0 and self.excavator.center_x >= self.excavator.target_x*block_size - block_size//2) or (self.excavator.change_x < 0 and self.excavator.center_x <= self.excavator.target_x*block_size - block_size//2)):
			self.excavator.change_x = 0
			self.excavator.center_x = self.excavator.target_x*block_size - block_size//2
			self.excavator.pos[0] = (self.excavator.center_x + block_size//2)//block_size
			self.excavator.fuel -= 0.25
		elif((self.excavator.change_y > 0 and self.excavator.center_y >= self.excavator.target_y*block_size - block_size//2) or (self.excavator.change_y < 0 and self.excavator.center_y <= self.excavator.target_y*block_size - block_size//2)):
			self.excavator.change_y = 0
			self.excavator.center_y = self.excavator.target_y*block_size - block_size//2
			self.excavator.pos[1] = (self.excavator.center_y + block_size//2)//block_size
			self.excavator.fuel -= 0.25

		#take damage from excessive depth
		if(self.excavator.depth > self.excavator.allowed_depth and self.excavator.damage < self.excavator.damage_withstanding):
			self.excavator.damage += 0.01*((self.excavator.depth - self.excavator.allowed_depth)**2)
		
		#calculate other game parameters
		self.left_boundary = self.excavator.center_x - screen_width//2
		self.right_boundary = self.excavator.center_x + screen_width//2
		self.bottom_boundary = self.excavator.center_y - screen_height//2
		self.top_boundary = self.excavator.center_y + screen_height//2
		arcade.set_viewport(self.left_boundary, self.right_boundary, self.bottom_boundary, self.top_boundary)
		self.excavator.depth = -int(self.excavator.center_y/block_size) + number_of_ver_blocks
		self.brightness = 100*(1 - self.excavator.depth/number_of_ver_blocks)
		arcade.set_background_color((int(80*self.brightness/100), int(114*self.brightness/100), int(167*self.brightness/100)))

#initialise game
game = MyGame(screen_width, screen_height, "Miner")
game.setup()
arcade.run()