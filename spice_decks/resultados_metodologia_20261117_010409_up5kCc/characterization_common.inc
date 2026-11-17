* Modelos institucionales y celda con alimentaciones explicitas.
.option post
.option scale=90n
.option measform=3 measdgt=10 numdgt=10 ingold=2
.temp 70
.param SUPPLY=1.8
.lib '/mnt/vol_NFS_rh003/estudiantes/dmedina_cadence/vlsi/Hspice/lp5mos/xt018.lib' tm
.lib '/mnt/vol_NFS_rh003/estudiantes/dmedina_cadence/vlsi/Hspice/lp5mos/param.lib' 3s
.lib '/mnt/vol_NFS_rh003/estudiantes/dmedina_cadence/vlsi/Hspice/lp5mos/config.lib' default

.subckt inv_char in out vp vn WN=4 WP=8
xn out in vn vn ne w='WN' l=2
+ as='WN*5' ad='WN*5' ps='2*WN+10' pd='2*WN+10'
xp out in vp vp pe w='WP' l=2
+ as='WP*5' ad='WP*5' ps='2*WP+10' pd='2*WP+10'
.ends inv_char
