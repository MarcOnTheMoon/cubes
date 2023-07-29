/*****************************************************************************************************
 * Communication via serial interface.
 *****************************************************************************************************
 * Author: Marc Hensel, http://www.haw-hamburg.de/marc-hensel
 * Project: https://github.com/MarcOnTheMoon/cubes
 * Copyright: 2023, Marc Hensel
 * Version: 2023.07.29
 * License: CC BY-NC-SA 4.0, see https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en
 *****************************************************************************************************/

#ifndef _SERIAL_COM_H_
#define _SERIAL_COM_H_

class SerialCom {
  public:
    char* receive(int *count);

  private:
};

#endif
