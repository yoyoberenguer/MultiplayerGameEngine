# 2D Multiplayer Game Engine
## 2D shmups multiplayer game engine (Alpha version) 

![alt text](https://github.com/yoyoberenguer/MultiplayerGameEngine/blob/master/Multiplayer.png)

To run the demo you will need the following python libraries install on your system 
 1) pygame
 2) matplotlib  
 3) Lz4 

**Make sure to allow ports 1024, 1025 through your firewall**.

**Make sure port 1024 and 1025 are not used by another process**.

**The program will not run without the Asset folder.**

### Run first Player1 followed shortly by Player2 

The demo is setup by default to run on the loopback to be able to start 
Player1 and Player2 scripts on the same computer. Therefore, you can run 
player 2 on a different machine to experience the network sound effect and players 
synchronization throughout the network. 

When Player1 script is launch, it will try 5 times to connect to a client. 
Player1 will timeout and start the demo without player2 if no client are capable of connecting during that time.
This is a demo version, in the future the connections between server/client(s) will be done with a menu.

## Computer 1 (e.g 192.168.1.106)

if __name__ == '__main__':

  SERVER = '192.168.1.106'  
  CLIENT = '192.168.1.112'

## Computer 2 (e.g IP 192.168.1.112)

if __name__ == '__main__':

  SERVER = '192.168.1.106'  
  CLIENT = '192.168.1.112'


**key**         |    Assignement 
--------------- | -------------------
**Spacebar**    |    primary shoot
**left arrow**  |    Left turn
**right arrow** |    right turn
**up arrow**    |    going forward
**down arrow**  |    going back
**ESC**         |    quit


