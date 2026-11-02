#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;

float calibrationFactor = 23.7354146341; 
//Calibrated using known mass: 3.968kg volts at known: 1.67V volts at zero: 0.03V

float zeroOffset = 0.0;

void setup() {
  Serial.begin(500000);
  Wire.begin();
  Wire.setClock(400000);
  ads.begin();

  //Constants for 860 SPS and +/- 4.096V Gain
  ads.setDataRate(RATE_ADS1115_860SPS); 
  ads.setGain(GAIN_ONE); 
  
  //creation of zero offset
  float sum = 0;
  for(int i = 0; i < 10; i++) {
    //Reading raw data
    int16_t rawADC = ads.readADC_SingleEnded(0);
    
    //Voltage calculator based on setGain
    sum += ads.computeVolts(rawADC);
    
    delay(50);
  }
  zeroOffset = sum / 10.0;
}

void loop() {
  // Read raw data from channel A0
  int16_t adc0 = ads.readADC_SingleEnded(0);
  
  // Calculate the exact voltage
  float volts = ads.computeVolts(adc0);

  //convert voltage to newtons using calculated calibration factor
  float force = (volts - zeroOffset) * calibrationFactor;

  // CSV formatted output
  float time = millis();
  if(time >= 0){
    Serial.print(time);
    Serial.print(",");
    Serial.println(force, 2);
  }
}