# Pocket Cube and Rubik's Cube Solvers
Dealing with artificial intelligence (AI), we were curious how to let computers learn
to solve a scrambled Pocket cube (2x2x2) or Rubik's cube (3x3x3). Okay, this is challenging enough.
Still, wouldn't it be even more fun to demonstrate the results by machines that _mechanically_ solve physical cubes?
Join us on this fascinating endeavor. 

## Overview
This is what we did so far:
1. _Rubik's cube:_ A team of five students has built a high-performance device for Rubik's cube based on lots 
of fancy hardware and a provided algorithm. The movements to solve a scrambled cube take well below 1 s.
2. _Machine learning:_ A student has implemented published approaches, analyzed modifications, and clearly
improved the performance. Due to required resources, the experiments focused on the Pocket
cube, however, the approaches should be transferable to Rubik's cube as well.
3. _Pocket cube:_ In the context of the work on machine learning methods, I have developed a simple low-cost
device to mechanically solve scrambled Pocket cubes.

### Rubik's cube solver
We will make details of the machine for Rubik's cube available in a dedicated sub folder in due time.
(Please be patient. I need to prepare the data.)

- For the moment, enjoy the image below, showing the control cabinet with motor drivers, microcontroller,
and such (left) and the hardware containing the cube, motors, cameras, and such (right). The device is
operated by a Laptop connected to the control cabinet.
- Additionally, there is a short video file in "assets/videos" which shows a cube being scrambled twice (slowly)
and solved (much faster). 

<img src="./assets/images/CubeSolver.jpg" width="500">

### Deep learning and Pocket cube solver
As of today (July 7, 2023), the Master thesis on machine learning (A* and Monte Carlo Tree Search,
combined with deep learning) will be finalized within the next days. We will make the thesis available
as soon as possible. Other data such as software and results will follow after a review.

- The images below give you an impression of the low-cost hardware, consisting mainly of an Arduino board,
two servo motors, a PWM module, and 3D-printed parts.
- In case you want to rebuild the device, you can download the 3D print files on Thingiverse
(https://www.thingiverse.com/thing:5822433).
- Source codes for the Arduino and a comfortable Python API as well as a document describing assembly,
calibration, the software, and such will follow.
- Additionally, there is a short video file in "assets/videos" which shows a scrambled Pocket cube being solved.

<img src="./assets/images/PocketCube.jpg" height="150"><img src="./assets/images/PocketCube_Rotate.jpg" height="150"><img src="./assets/images/PocketCube_Turn.jpg" height="150">

## Contributors
This project is not a one-man-show. My deepest thanks go to my magnificent students at HAW Hamburg,
who raised my interest for this topic and contributed by their brilliant work done with remarkable passion:

- Sophie Kirchhoff (Rubik's cube device)
- Finn Lanz (machine learning, integration of Pocket cube hardware)
- Kim Henrik Otte (Rubik's cube device)
- Marvin Paetow (Rubik's cube device)
- Christoph Rathjen (Rubik's cube device)
- Kim Kristin Westphal (Rubik's cube device)

## Contact
Marc Hensel, University of Applied Sciences Hamburg (HAW Hamburg)

http://www.haw-hamburg.de/marc-hensel
