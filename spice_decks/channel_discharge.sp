* 2.a: descarga NMOS y carga dual PMOS, ambos de W=0.36um L=0.18um.
* El capacitor PMOS se carga: VSD cae de VDD a VDD/2.
.include 'characterization_common.inc'
.param CTEST=1p

VG gn 0 DC 'SUPPLY'
VSN sn 0 DC 0
VSP sp 0 DC 'SUPPLY'
XN dn gn sn sn ne w=4 l=2
+ as=20 ad=20 ps=18 pd=18
XP dp 0 sp sp pe w=4 l=2
+ as=20 ad=20 ps=18 pd=18
CN dn 0 'CTEST' IC='SUPPLY'
CP dp 0 'CTEST' IC=0

.data cap_values CTEST
1p
2p
.enddata
.tran 10ps 50ns UIC SWEEP DATA=cap_values
.measure tran cap_used PARAM='CTEST'
.measure tran tn_half WHEN v(dn)='SUPPLY/2' FALL=1
.measure tran tp_half WHEN v(dp)='SUPPLY/2' RISE=1
* Estas resistencias RC no sustituyen el promedio de VDS/IDS solicitado.
.measure tran rn_rc PARAM='tn_half/(0.69314718056*CTEST)'
.measure tran rp_rc PARAM='tp_half/(0.69314718056*CTEST)'
.probe tran v(dn) v(dp) I(VSN) I(VSP)
.print tran v(dn) v(dp) I(VSN) I(VSP)
.end
