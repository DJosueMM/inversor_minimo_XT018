* Barrido FO1; entrada casi ideal, medidas en el segundo ciclo.
.include 'characterization_common.inc'
.param RATIO=2

VDRV vdrv 0 DC 'SUPPLY'
VLOAD vload 0 DC 'SUPPLY'
VIN in 0 PULSE(0 'SUPPLY' 100ps 1ps 1ps 499ps 1ns)
XDRV in out vdrv 0 inv_char WN=4 WP='4*RATIO'
XLOAD out load_out vload 0 inv_char WN=4 WP='4*RATIO'

.tran 0.5ps 3ns SWEEP RATIO 1.5 4.0 0.025
.measure tran ratio_used PARAM='RATIO'
.measure tran tphl TRIG v(in) VAL='SUPPLY/2' RISE=2
+ TARG v(out) VAL='SUPPLY/2' FALL=2
.measure tran tplh TRIG v(in) VAL='SUPPLY/2' FALL=2
+ TARG v(out) VAL='SUPPLY/2' RISE=2
.measure tran tpd PARAM='(tphl+tplh)/2'
.measure tran diff PARAM='tplh-tphl'
.measure tran asym_pct PARAM='100*abs(tplh-tphl)/tpd'
.measure tran tfall TRIG v(out) VAL='0.8*SUPPLY' FALL=2
+ TARG v(out) VAL='0.2*SUPPLY' FALL=2
.measure tran trise TRIG v(out) VAL='0.2*SUPPLY' RISE=2
+ TARG v(out) VAL='0.8*SUPPLY' RISE=2
.probe tran v(in) v(out) v(load_out) I(VDRV) I(VLOAD)
.end
