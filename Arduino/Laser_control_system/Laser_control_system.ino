//Define output channels for TTL signals
int TTL_O_FL = 2;
int TTL_O_QS = 4;

//Define input channels for TTL signals (for a closed loop operation)
int TTL_I_FL = 7;
int TTL_I_QS = 8;

// Define pulse length in microsecs
int P_length = 10;

char no_Pulses;
boolean new_Data = false;
const char endMarker = '\r';
byte bytesRecvd = 0;

void setup() {
  pinMode(TTL_O_FL, OUTPUT);
  pinMode(TTL_O_QS, OUTPUT);
  pinMode(TTL_I_FL, INPUT);
  pinMode(TTL_I_QS, INPUT)
  
  digitalWrite(TTL_O_FL,LOW);
  digitalWrite(TTL_O_QS,LOW);
  digitalWrite(TTL_I_FL,LOW);
  digitalWrite(TTL_I_QS,LOW);

  Serial.begin(9600);
  Serial.println("<Arduino is ready>");
  Serial.println("Starting Laser_control_system.ino");
}


void loop() {
     
   askForUserInput();
   getUserResponse();

   fireLaser();
}

void askForUserInput() {
  if (waitForFiring == true){
    return;
  }
  if (
  const char question[] = "Please type how many pulses to fire (firing at 1Hz)and press ENTER";
  const byte buffSize = 3;
  char userResponse[buffSize];
 }
}
