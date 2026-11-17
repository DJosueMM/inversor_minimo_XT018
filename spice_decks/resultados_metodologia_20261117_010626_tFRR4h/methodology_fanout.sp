* Weste 8.4.5: matched-input FO3/FO4 difference, minimum-width DUTs.
.include 'characterization_common.inc'
.include 'methodology_sizes.inc'
VDD vp 0 DC 'SUPPLY'
VIN a 0 PULSE(0 'SUPPLY' 100ps 1ps 1ps 499ps 1ns)
XPRE0 a b vp 0 inv_char WN=4 WP='4*RATIO'
XPRE1 b in vp 0 inv_char WN=4 WP='4*RATIO'
X3 in out3 vp 0 inv_char WN=4 WP='4*RATIO'
X4 in out4 vp 0 inv_char WN=4 WP='4*RATIO'
XDUMMY1 in dummy1 vp 0 inv_char WN=4 WP='4*RATIO'
XDUMMY2 in dummy2 vp 0 inv_char WN=4 WP='4*RATIO'
XLOAD3 out3 load3 vp 0 inv_char WN=12 WP='12*RATIO'
XLOAD4 out4 load4 vp 0 inv_char WN=16 WP='16*RATIO'
.tran 0.5ps 3ns
.measure tran ratio_used PARAM='RATIO'
.measure tran tphl3 TRIG v(in) VAL='SUPPLY/2' RISE=2
+ TARG v(out3) VAL='SUPPLY/2' FALL=2
.measure tran tphl4 TRIG v(in) VAL='SUPPLY/2' RISE=2
+ TARG v(out4) VAL='SUPPLY/2' FALL=2
.measure tran tplh3 TRIG v(in) VAL='SUPPLY/2' FALL=2
+ TARG v(out3) VAL='SUPPLY/2' RISE=2
.measure tran tplh4 TRIG v(in) VAL='SUPPLY/2' FALL=2
+ TARG v(out4) VAL='SUPPLY/2' RISE=2
.measure tran tin_r TRIG v(in) VAL='0.2*SUPPLY' RISE=2
+ TARG v(in) VAL='0.8*SUPPLY' RISE=2
.measure tran tin_f TRIG v(in) VAL='0.8*SUPPLY' FALL=2
+ TARG v(in) VAL='0.2*SUPPLY' FALL=2
.measure tran tr3 TRIG v(out3) VAL='0.2*SUPPLY' RISE=2
+ TARG v(out3) VAL='0.8*SUPPLY' RISE=2
.measure tran tf3 TRIG v(out3) VAL='0.8*SUPPLY' FALL=2
+ TARG v(out3) VAL='0.2*SUPPLY' FALL=2
.measure tran tr4 TRIG v(out4) VAL='0.2*SUPPLY' RISE=2
+ TARG v(out4) VAL='0.8*SUPPLY' RISE=2
.measure tran tf4 TRIG v(out4) VAL='0.8*SUPPLY' FALL=2
+ TARG v(out4) VAL='0.2*SUPPLY' FALL=2
.probe tran v(in) v(out3) v(out4)
.end
