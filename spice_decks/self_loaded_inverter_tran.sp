* Respuesta transitoria del inversor cargado por otro inversor identico.
* WN=4*90nm=0.36um, WP=13.5*90nm=1.215um.

.option post
.option scale=90n
.temp 70
.param SUPPLY=1.8
.param N=4
.param P=13.5

.lib '/mnt/vol_NFS_rh003/estudiantes/dmedina_cadence/vlsi/Hspice/lp5mos/xt018.lib' tm
.lib '/mnt/vol_NFS_rh003/estudiantes/dmedina_cadence/vlsi/Hspice/lp5mos/param.lib' 3s
.lib '/mnt/vol_NFS_rh003/estudiantes/dmedina_cadence/vlsi/Hspice/lp5mos/config.lib' default

.global vdd! gnd!
.include 'min_inverter.sp'

VDD vdd! gnd! DC 'SUPPLY'
VIN in gnd! PULSE 0 'SUPPLY' 0ps 10ps 10ps 500ps 1ns

* Etapa bajo prueba y una etapa identica como carga capacitiva.
XDRV in out inv N='N' P='P'
XLOAD out load_out inv N='N' P='P'

.tran 0.1ps 2ns
.measure tran tphl TRIG v(in) VAL='SUPPLY/2' RISE=1
+ TARG v(out) VAL='SUPPLY/2' FALL=1
.measure tran tplh TRIG v(in) VAL='SUPPLY/2' FALL=1
+ TARG v(out) VAL='SUPPLY/2' RISE=1
.measure tran tpd PARAM='(tphl+tplh)/2'
.measure tran tfall TRIG v(out) VAL='0.8*SUPPLY' FALL=1
+ TARG v(out) VAL='0.2*SUPPLY' FALL=1
.measure tran trise TRIG v(out) VAL='0.2*SUPPLY' RISE=1
+ TARG v(out) VAL='0.8*SUPPLY' RISE=1

.probe tran v(in) v(out) v(load_out)
.end
