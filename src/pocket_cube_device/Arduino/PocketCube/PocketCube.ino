/*****************************************************************************************************
 * Pocket cube solver
 *****************************************************************************************************
 * Author: Marc Hensel, http://www.haw-hamburg.de/marc-hensel
 * Project: https://github.com/MarcOnTheMoon/cubes
 * Copyright: 2023, Marc Hensel
 * Version: 2023.07.29
 * License: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
 *****************************************************************************************************
 * Board:
 * - Arduino Uno R3
 * 
 * Modules:
 * - PCA9685 PWM servo driver board
 * - 180° standard servo to turn cube vertically
 * - 270° servo to rotate cube horizontally
 * 
 * Servos used and calibration procedure:
 * - See file Servos.cpp
 *****************************************************************************************************/

#include "Servos.h"
#include "SerialCom.h"

/*****************************************************************************************************
 * Global variables
 *****************************************************************************************************/

SerialCom serialCom;
Servos servos;

/*****************************************************************************************************
 * Standard methods
 *****************************************************************************************************/

/* Initialize program */
void setup() {
  // USB connection to Python script
  Serial.begin(9600);       // Make sure baud rate matches Python script

  // Servos
  servos.initDriver();
  servos.initPositions();

  // Notify Python script that device is ready
  Serial.println("ok");
}

/* Main loop */
void loop() {
  // Read data sent from Python script
  char *receivedData;
  int receivedCount;
  
  receivedData = serialCom.receive(&receivedCount);

  // React on received data
  if (receivedCount > 0) {
    for (int i = 0; i < receivedCount; i++) {
      switch (receivedData[i]) {
        case 'I':                   // Init
          servos.initPositions();
          break;
        case 'L':                   // Left (horizontal)
          servos.rotateLeft();
          break;
        case 'R':                   // Right (horizontal)
          servos.rotateRight();
          break;
        case 'T':                   // Turn vertically
          servos.turnCube();
          break;
        case '>':                   // Send acqknowledge
          Serial.println("ok");
          break;
      }
    }
  }
  delay(250);
}
