# this class is responsible for all the printing statemenets and color changes

import math
styleCodes = {
	"NORMAL": 0,
	"BOLD": 1,
	"ITALIC": 3,
	"UNDERLINE": 4,
}

ENDC = '\033[0m'

class colorCodes:
	WHITE = 255
	BLACK = 232
	PINK_RED = 206
	PURPLE = 141
	CYAN = 123
	YELLOW = 226
	ORANGE = 209
	GREEN = 154
	RED = 211

# multiple printing functions, each is different by color
# printing in colors (bonus)
def print_in_color(msg, color = colorCodes.ORANGE):
	print(u"\u001b[38;5;" + str(color) + "m" + msg + " \u001b[0m\n")

def print_clientMessage(msg):
	print_in_color(msg, color = colorCodes.PINK_RED)

def print_state(msg):
	print_in_color(msg, color = colorCodes.CYAN)

def print_info(msg):
	print_in_color(msg, color = colorCodes.YELLOW)

def print_to_client_screen_orange(msg):
	print_in_color(msg, color = colorCodes.ORANGE)

def print_to_client_screen_green(msg):
	print_in_color(msg, color = colorCodes.GREEN)

def error(msg):
	print_in_color(msg, color = colorCodes.RED)
