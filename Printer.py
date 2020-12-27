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

def print_in_color(msg, color = colorCodes.ORANGE):
    # print(f"\033[{style};{color};{backgroundColor + 10}m {msg} {ENDC}")
	# print(f"\033[{style};{color};{newBackground}m {msg} {ENDC}")
	print(u"\u001b[38;5;" + str(color) + "m" + msg + " \u001b[0m")

# ombre printing
def print_clientMessage(msg):
	print_in_color(msg, color = colorCodes.PURPLE)

def print_state(msg):
	print_in_color(msg, color = colorCodes.CYAN)

def print_info(msg):
	print_in_color(msg, color = colorCodes.YELLOW)

def print_to_client_screen_orange(msg):
	print_in_color(msg, color = colorCodes.ORANGE)

def print_to_client_screen_green(msg):
	print_in_color(msg, color = colorCodes.GREEN)
