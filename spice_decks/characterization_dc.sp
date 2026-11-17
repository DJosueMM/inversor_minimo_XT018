* VTC y corriente DC aislada de la etapa bajo prueba; carga FO1.
.include 'characterization_common.inc'
.param RATIO=2

VDRV vdrv 0 DC 'SUPPLY'
VLOAD vload 0 DC 'SUPPLY'
VIN in 0 DC 0
XDRV in out vdrv 0 inv_char WN=4 WP='4*RATIO'
XLOAD out load_out vload 0 inv_char WN=4 WP='4*RATIO'

.dc VIN 0 'SUPPLY' 0.002 SWEEP RATIO 1.5 4.0 0.025
.measure dc ratio_used PARAM='RATIO'
.measure dc vm WHEN v(out)=v(in)
.measure dc vin_at_half FIND v(in) WHEN v(out)='SUPPLY/2'
.measure dc idrv_at_half FIND I(VDRV) WHEN v(out)='SUPPLY/2'
.measure dc isc_peak MAX PAR('-I(VDRV)')
.probe dc v(in) v(out) I(VDRV) I(VLOAD)
.print dc v(in) v(out) I(VDRV)
.end
