/*****************************************************************************************************
 * Servo motors for PocketCube solver.
 *****************************************************************************************************
 * Author: Marc Hensel, http://www.haw-hamburg.de/marc-hensel
 * Project: https://github.com/MarcOnTheMoon/cubes
 * Copyright: 2023, Marc Hensel
 * Version: 2023.07.29
 * License: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
 *****************************************************************************************************
 * Vertical turn servo:
 * - MG996R Digital high torque metal gear servo
 * - Datasheet: https://www.electronicoscaldas.com/datasheet/MG996R_Tower-Pro.pdf
 * - Supplier and downloads: https://www.az-delivery.de/en/products/az-delivery-servo-mg996r
 * 
 * Horizontal servo:
 * - Miuzei MS24 20 kg RC digital servo (270°)
 * - Datasheet: https://images-na.ssl-images-amazon.com/images/I/81Lbgu+nG6L.pdf
 * - Supplier: https://www.amazon.de/Miuzei-Wasserdicht-Metallgetriebe-Starrfl%C3%BCgel-intelligenten/dp/B0BBZFDJJ6?th=1
 * 
 * Calibration procedure:
 * 1. Set 0° position of rotation servo:
 * 
 * 2. Set vertical turn:
 *    a) Set TURN_SERVO_MIN so that the far bar just touches the cube.
 *    b) Set TURN_SERVO_MAX so that the cube is pushed far enough to be turned and dragged back into position.
 *    c) Set TURN_DELAY_MS so that there is only a very brief pause between forward and backward movement.
 *    
 * 3. Set 90°, 180°, and 270° positions of rotation servo:
 *****************************************************************************************************/

#include <Arduino.h>
#include <Wire.h>
#include "Config.h"
#include "Servos.h"

/*****************************************************************************************************
 * Global variables
 *****************************************************************************************************/

// Ticks for PCA9685 board corresponding to 0°, 90°, 180°, and 270°
int rotationTicks[] = {
  ROTATE_SERVO_0,
  ROTATE_SERVO_90,
  ROTATE_SERVO_180,
  ROTATE_SERVO_270
};

/*****************************************************************************************************
 * Initialization
 *****************************************************************************************************/

/**! Init PCA9685 servo board.
 */
void Servos::initDriver(void) {
  pwm = Adafruit_PWMServoDriver();
  pwm.begin();
  pwm.setPWMFreq(PWM_FREQUENCY_HZ);
}

/**! Init positions of servos.
 * 
 * - Turn servo holding cube
 * - Rotation servo at 0°
 */
void Servos::initPositions(void) {
  // Vertical turn
  pwm.setPWM(TURN_SERVO_CHANNEL, 0, TURN_SERVO_MIN);
  delay(TURN_DELAY_MS);

  // Horizontal rotation
  rotateTo(0);
  delay(2 * ROTATE_DELAY_MS);
}

/*****************************************************************************************************
 * Horizontal rotation
 *****************************************************************************************************/

/**! Rotate servo 90° to the left.
 */
void Servos::rotateLeft(void) {
  if (rotationAngleDegree > 0)
    rotateTo(rotationAngleDegree - 90);
  else
    rotateTo(270);
}

/**! Rotate servo 90° to the right.
 */
void Servos::rotateRight(void) {
  if (rotationAngleDegree < 270)
    rotateTo(rotationAngleDegree + 90);
  else
    rotateTo(0);
}

/**! Rotate servo to a multiple of 90°.
 * 
 * @param angleDegree Target angle in [0, 90, 180, 270] degrees
 */
void Servos::rotateTo(int angleDegree) {
  if ((angleDegree == 0) || (angleDegree == 90) || (angleDegree == 180) || (angleDegree == 270)) {
    int numberSteps90 = abs(rotationAngleDegree - angleDegree) / 90;
    int pcaTicks = rotationTicks[angleDegree / 90];
    
    pwm.setPWM(ROTATE_SERVO_CHANNEL, 0, pcaTicks);
    delay(numberSteps90 * ROTATE_DELAY_MS);
    rotationAngleDegree = angleDegree;
  }
}

/*****************************************************************************************************
 * Vertical turn
 *****************************************************************************************************/

/**! Turn cube vertically.
 * 
 * Turn consists of following  sequence:
 * 1. Push cube away, so that it "falls" to its side.
 * 2. Pull cube back in place.
 */
void Servos::turnCube(void) {
  pwm.setPWM(TURN_SERVO_CHANNEL, 0, TURN_SERVO_MAX);
  delay(TURN_DELAY_MS);
  pwm.setPWM(TURN_SERVO_CHANNEL, 0, TURN_SERVO_MIN);
  delay(TURN_DELAY_MS);
}
