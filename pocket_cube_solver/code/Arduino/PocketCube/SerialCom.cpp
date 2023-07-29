/*****************************************************************************************************
 * Communication via serial interface.
 *****************************************************************************************************
 * Author: Marc Hensel, http://www.haw-hamburg.de/marc-hensel
 * Project: https://github.com/MarcOnTheMoon/cubes
 * Copyright: 2023, Marc Hensel
 * Version: 2023.07.29
 * License: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
 *****************************************************************************************************/

#include <Arduino.h>
#include "SerialCom.h"

/*****************************************************************************************************
 * Methods
 *****************************************************************************************************/

/**! Receive characters via the standard serial interface (class Serial).
 * 
 * @param count [out] Stores number of characters received
 * @return array of received characters (at most 32)
 */
char* SerialCom::receive(int *count) {
  static char readBuffer[32];
  int bufferSize = 32;
  int bufferIndex = 0;
  
  while ((Serial.available() > 0) && (bufferIndex < bufferSize)) {
    readBuffer[bufferIndex++] = (char)Serial.read();
    delay(3);
  }
  *count = bufferIndex;
  
  return readBuffer;
}
