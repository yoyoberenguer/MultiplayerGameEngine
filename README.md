# Multiplayer Game Engine
2D Multiplayer game engine (Alpha version) 

To run the demo you will need the following python libraries install on your system 
 1) pygame
 2) matplotlib  
 3) Lz4 

Run first Player1 followed shortly by Player2 

It is setup by default to run the game on the loopback, you can change that it with the following variables:

## Computer 1 (e.g 192.168.1.106)

if __name__ == '__main__':
  SERVER = '192.168.1.106'  
  CLIENT = '192.168.1.112'

## Computer 2 (e.g IP 192.168.1.112)

if __name__ == '__main__':
  SERVER = '192.168.1.106'
  CLIENT = '192.168.1.112'
