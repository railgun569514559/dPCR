BASE(0,1) '0 ����X�� ��1����Y��
ATYPE = 1,1
UNITS = 1000,1000 '1MM
SPEED = 10,10 '
CREEP = 1,1
ACCEL = 50,50
DECEL = 50,50
FWD_IN = 13,10
REV_IN = 15,12
DATUM_IN = 14,11
DATUM(4)AXIS(0)
DATUM(4)AXIS(1)
WAIT UNTIL IDLE(0) AND IDLE(1)
MOVE(11)AXIS(1)

WAIT UNTIL IDLE(0) AND IDLE(1)
REV_IN = 1 
DPOS = 0,0





