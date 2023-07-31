# Pocket Cube and Rubik's Cube Solvers
Dealing with artificial intelligence (AI), we were curious how to let computers learn
to solve a scrambled Pocket cube (2x2x2) or Rubik's cube (3x3x3). Okay, this is challenging enough.
Still, wouldn't it be even more fun to demonstrate the results by machines that _mechanically_ solve physical cubes?
Join us on this fascinating endeavor. 

## Overview
This is what we did so far:
1. _Rubik's cube device:_ A team of five students has built a high-performance device for Rubik's cube based on lots 
of fancy hardware and a provided algorithm. The movements to solve a scrambled cube take well below 1 s.
2. _Deep learning:_ In scope of his Master thesis, Finn Lanz has implemented, analyzed, and modified approaches based on reinforcement learning to let computers learn how to solve cubes. Due to required resources, the experiments focused on the Pocket cube.
3. _Pocket cube device:_ I have developed a low-cost device to mechanically solve scrambled Pocket cubes. (Finn and I wanted to have a cool hardware demonstrator for his Master thesis.)

### Pocket cube device
The _Pocket cube solver_ shown in the images below is, on purpose, based low-cost hardware, consisting mainly of an Arduino board, two servo motors, a PWM module, and 3D-printed parts. In case you want to rebuild the device, please note the detailed documentation in the folder "docs" describing assembly, calibration, and the software. All source files (Arduino, Python) are located in "src/pocket_cube_device", and the 3D print files are available on Thingiverse (https://www.thingiverse.com/thing:5822433). Additionally, there is a short video file in "assets/videos" which shows a scrambled Pocket cube being solved.

<img src="./assets/images/PocketCube.jpg" height="125"> <img src="./assets/images/PocketCube_Rotate.jpg" height="125"> <img src="./assets/images/PocketCube_Turn.jpg" height="125">

### Rubik's cube device
The _Rubik's cube solver_ shown in the image below consists of a control cabinet with motor drivers, microcontroller, and such (left) and the hardware containing the cube, motors, cameras, and such (right). The device is
operated by a Laptop connected to the control cabinet. Additionally, there is a short video file in "assets/videos" which shows a cube being scrambled twice (slowly) and solved (much faster). We will provide technical information and source codes after a review - please be patient.

<img src="./assets/images/CubeSolver.jpg" width="500">

### Deep learning
In scope of his Master thesis, Finn has trained several models to solve scrambles Pocket cubes. Furthermore, he has developed a program to scan the colors of Pocket cubes placed in the Pocket cube device and physically unscramble them. The Master thesis is available in the folder "docs" (in German language). Software and models will follow after a review - please be patient.

## Still to come (open)
- Reinforcement learning (source code, trained models)
- Pocket cube application including trained models
- Technical documentation and source codes of Rubik's cube device
- Refactoring of Rubik's cube device

## Contributors
My deepest thanks go to following  magnificent students of our  [Department at HAW Hamburg](https://www.haw-hamburg.de/hochschule/technik-und-informatik/departments/informations-und-elektrotechnik/studium/studiengaenge/), who raised my interest for this topic and contributed by their brilliant work done with remarkable passion:

- Sophie Kirchhoff (Rubik's cube device)
- Finn Lanz (machine learning, integration of Pocket cube hardware)
- Kim Henrik Otte (Rubik's cube device)
- Marvin Paetow (Rubik's cube device)
- Christoph Rathjen (Rubik's cube device)
- Kim Kristin Westphal (Rubik's cube device)

## Contact
Marc Hensel, University of Applied Sciences Hamburg (HAW Hamburg)

http://www.haw-hamburg.de/marc-hensel
