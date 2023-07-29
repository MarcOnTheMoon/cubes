/*****************************************************************************************************
 * Configration of PocketCube solver.
 *****************************************************************************************************
 * Author: Marc Hensel, http://www.haw-hamburg.de/marc-hensel
 * Project: https://github.com/MarcOnTheMoon/cubes
 * Copyright: 2023, Marc Hensel
 * Version: 2023.07.29
 * License: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
 *****************************************************************************************************/

#ifndef _CONFIG_H_
#define _CONFIG_H_

/*****************************************************************************************************
 * Servo driver PWM board
 *****************************************************************************************************/

/* Pulse widths for f = 50 Hz:
 * - Period: T = 1000 ms / 50 = 20 ms (corresponding to 4096 ticks of PCA9685)
 * - Ticks: t = 4096 ticks / 20 ms = 204,8 ticks/ms
 * - Theoretically:
 * 
 *     ms    | 0.5 | 1.0 | 1.5 | 2.0 | 2.5
 *     ------+-----+-----+-----+-----+-----
 *     ticks | 102 | 205 | 307 | 410 | 512
 */
#define PWM_FREQUENCY_HZ 50     // PCA9685: PWM frequency
#define TURN_SERVO_CHANNEL 0    // Channel the turn servo is connected to
#define ROTATE_SERVO_CHANNEL 1  // Channel the rotation servo is connected to

/*****************************************************************************************************
 * Servo angle calibration
 *****************************************************************************************************/

// Vertical "turn" servo (turn cube vertically)
#define TURN_SERVO_MIN 100        // Far crossbar just holding cube
#define TURN_SERVO_MAX 380        // Close crossbar pushing cube over

// Horizontal "rotation" servo (turn lower cube layer horizontally)
#define ROTATE_SERVO_0   102      // 0°
#define ROTATE_SERVO_90  247      // 90°
#define ROTATE_SERVO_180 397      // 180°
#define ROTATE_SERVO_270 533      // 270°

/*****************************************************************************************************
 * Servo time delays
 *****************************************************************************************************/

#define TURN_DELAY_MS 550       // Delay for each direction (forward, backward)
#define ROTATE_DELAY_MS 650     // Delay for each 90° turn

#endif
