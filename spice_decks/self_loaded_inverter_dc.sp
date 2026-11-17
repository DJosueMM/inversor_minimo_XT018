* Inversor CMOS con carga de entrada de otro inversor identico.
* VTC e Isc para el tamano analitico de primer orden:
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
VIN in gnd! DC 0

* Etapa bajo prueba y una etapa identica como carga capacitiva.
XDRV in out inv N='N' P='P'
XLOAD out load_out inv N='N' P='P'

.dc VIN 0 'SUPPLY' 0.005
.measure dc vm FIND V(in) WHEN V(out)='SUPPLY/2'
.measure dc isc FIND I(VDD) WHEN V(out)='SUPPLY/2'
.probe dc v(in) v(out)
.plot dc v(out)

.end
