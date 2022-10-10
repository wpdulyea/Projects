#include "MicroBit.h"

MicroBit    uBit;

// Let's set up some event listeners for buttons and the radio
//
void onButton(MicroBitEvent e)
{
	if (e.source == MICROBIT_ID_BUTTON_A) {
        	uBit.serial.printf("BUTTON A: ");
    		uBit.radio.datagram.send("A");
    	}
	else if (e.source == MICROBIT_ID_BUTTON_B) {
        	uBit.serial.printf("BUTTON B: ");
		uBit.radio.datagram.send("B");
	}
    	uBit.serial.printf("\r\n");
}

void onData(MicroBitEvent)
{
	ManagedString str = uBit.radio.datagram.recv();
	uBit.serial.printf("RX DATA");
	uBit.display.scroll(str);
}

int main()
{
	// Initialise the micro:bit runtime.
    	uBit.init();
	// Register to receive events.
	uBit.messageBus.listen(MICROBIT_ID_BUTTON_A, MICROBIT_BUTTON_EVT_CLICK, onButton);
	uBit.messageBus.listen(MICROBIT_ID_BUTTON_B, MICROBIT_BUTTON_EVT_CLICK, onButton);
    	uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);
    	if( uBit.radio.enable() != MICROBIT_OK) {
		uBit.display.scroll("Failed to enable the Radio", 100);
	}
	uBit.radio.setGroup(10);
	uBit.radio.setTransmitPower(6);
	uBit.radio.setFrequencyBand(10);


    	while(1) {
		uBit.serial.printf("Sleep cycle in main.\r\n");
		uBit.sleep(1000);
	}
}

