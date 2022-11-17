#include "MicroBit.h"

MicroBit    uBit;

void calibrateTemp();

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
	else if (e.source == MICROBIT_ID_BUTTON_AB) {
		// Calibrate the temp sensor
		calibrateTemp();
	}
    	uBit.serial.printf("\r\n");
}

void onData(MicroBitEvent)
{
	PacketBuffer data = uBit.radio.datagram.recv();
	uint8_t *str = data.getBytes();
	int data_len = data.length();

	uBit.serial.printf("RX DATA: ");
	for(int i = 0; i < data_len; i++) {
		uBit.serial.sendChar((char)str[i]);
		uBit.display.printChar((char)str[i]);
	}
	uBit.serial.printf("\r\n");
}

void onTempUpdate(MicroBitEvent)
{
	int ctemp = uBit.thermometer.getTemperature();
	ManagedString str(ctemp);

	uBit.display.scroll(str);
}

void calibrateTemp()
{
	int t = uBit.thermometer.getTemperature();
	if( uBit.thermometer.setCalibration(t) != MICROBIT_OK ) {
		uBit.serial.send(ManagedString("Failed to Calibrate Thermometer\r\n"));
	}
}

int main()
{
	// Initialise the micro:bit runtime.
    	uBit.init();
	// Calibrate the temprature sensor prior to registering the event to avoid triggering an
	// event action.
	calibrateTemp();

	// Register to receive events.
	uBit.messageBus.listen(MICROBIT_ID_BUTTON_A, MICROBIT_BUTTON_EVT_CLICK, onButton);
	uBit.messageBus.listen(MICROBIT_ID_BUTTON_B, MICROBIT_BUTTON_EVT_CLICK, onButton);
	uBit.messageBus.listen(MICROBIT_ID_THERMOMETER, MICROBIT_THERMOMETER_EVT_UPDATE, onTempUpdate);
    	uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);
    	if( uBit.radio.enable() != MICROBIT_OK) {
		uBit.display.scroll("Failed to enable the Radio", 100);
	}
	uBit.radio.setGroup(10);
	uBit.radio.setTransmitPower(6);
	uBit.radio.setFrequencyBand(10);
	uBit.thermometer.setPeriod(5000);

    	while(1) {
		uBit.serial.printf("Sleep cycle in main.\r\n");
		uBit.sleep(1000);
	}
}

