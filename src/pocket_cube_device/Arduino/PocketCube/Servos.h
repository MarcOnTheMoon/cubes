/*****************************************************************************************************
 * Servo motors for PocketCube solver.
 *****************************************************************************************************
 * Author: Marc Hensel, http://www.haw-hamburg.de/marc-hensel
 * Project: https://github.com/MarcOnTheMoon/cubes
 * Copyright: 2023, Marc Hensel
 * Version: 2023.07.29
 * License: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
 *****************************************************************************************************/

#ifndef _SERVOS_H_
#define _SERVOS_H_

#include <Adafruit_PWMServoDriver.h>

class Servos {

  /*****************************************************************************************************
   * Attributes
   *****************************************************************************************************/
  private:
    int rotationAngleDegree = 0;    // Current rotation position
    Adafruit_PWMServoDriver pwm;    // PCA9685 (PWM servo board)

  /*****************************************************************************************************
   * Methods
   *****************************************************************************************************/
  public:
    void initDriver(void);
    void initPositions(void);
    void rotateLeft(void);
    void rotateRight(void);
    void turnCube(void);

  private:
    void rotateTo(int angleDegree);
};

#endif
