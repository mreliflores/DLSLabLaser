const unsigned int numReadings = 2500;
unsigned int analogVals[numReadings];
long t, t0;
String str;
String params[1];
int sr;

#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setTimeout(5);
  sbi(ADCSRA, ADPS2);
  cbi(ADCSRA, ADPS1);
  cbi(ADCSRA, ADPS0);
}

void loop() {
  // put your main code here, to run repeatedly:
  int strCount = 0;
  if (Serial.available() > 0) {
    
    str = Serial.readString();
    str.trim();

    while (str.length() > 0) {
      int index = str.indexOf('x');
      if (index == -1) {
        params[strCount++] = str;
        break;
      }
      else {
        params[strCount++] = str.substring(0, index);
        str = str.substring(index + 1);
      }
    }

    sr = params[0].toInt(); //Scan Rate
    //ac = params[1].toInt(); //acumulations

    switch (sr) {
      case 2:
        cbi(ADCSRA, ADPS2);
        cbi(ADCSRA, ADPS1);
        sbi(ADCSRA, ADPS0);
        break;
      case 4:
        cbi(ADCSRA, ADPS2);
        sbi(ADCSRA, ADPS1);
        cbi(ADCSRA, ADPS0);
        break;
      case 8:
        cbi(ADCSRA, ADPS2);
        sbi(ADCSRA, ADPS1);
        sbi(ADCSRA, ADPS0);
        break;
      case 16:
        sbi(ADCSRA, ADPS2);
        cbi(ADCSRA, ADPS1);
        cbi(ADCSRA, ADPS0);
        break;
      case 32:
        sbi(ADCSRA, ADPS2);
        cbi(ADCSRA, ADPS1);
        sbi(ADCSRA, ADPS0);
        break;
      case 64:
        sbi(ADCSRA, ADPS2);
        sbi(ADCSRA, ADPS1);
        cbi(ADCSRA, ADPS0);
        break;
      case 128:
        sbi(ADCSRA, ADPS2);
        sbi(ADCSRA, ADPS1);
        sbi(ADCSRA, ADPS0);
        break;
    }
  }
  t0 = micros();
  // Construct the array
  for (int i=0; i < numReadings ; i++)
  {
    analogVals[i] = analogRead(A15);
  }
  t = micros()-t0;  // calculate elapsed time
  
  // Send to computer
  for (int i=0; i < numReadings ; i++)
  {
    Serial.print(analogVals[i]);
    Serial.print(',');
  }
  Serial.print(t);
  Serial.println(',');
  Serial.flush();
  delay(10);
  
}
