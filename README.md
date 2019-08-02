# Multiplayer Game Engine
2D Multiplayer game engine (Alpha version) 

![alt text](https://github.com/yoyoberenguer/MultiplayerGameEngine/blob/master/Multiplayer.PNG)

To run the demo you will need the following python libraries install on your system 
 1) pygame
 2) matplotlib  
 3) Lz4 

Make sure to allow the demo to run (connecting to port 1024 and 1025).
Make sure port 1024 and 1025 are not used by another process.
The program will not run without the Asset folder.

Run first Player1 followed shortly by Player2 

The demo is setup by default to run on the loopback to be able to start 
Player1 and Player2 scripts on the same computer. Therefore, you can run 
player 2 on a different machine to experience the network sound effect and players 
synchronization throughout the network. 

When Player1 script is lauched, it will try 5 times to connect to a client. 
If no clients are connecting during that time, Player1 will timeout and start the demo without player2.
This is a demo version, in the future the connections between server/client(s) will be done with a menu.

## Computer 1 (e.g 192.168.1.106)

if __name__ == '__main__':

  SERVER = '192.168.1.106'  
  CLIENT = '192.168.1.112'

## Computer 2 (e.g IP 192.168.1.112)

if __name__ == '__main__':

  SERVER = '192.168.1.106'  
  CLIENT = '192.168.1.112'

Space bar to shoot 

Directional keys to control spaceship
