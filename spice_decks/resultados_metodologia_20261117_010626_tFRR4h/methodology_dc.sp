* Direct DC verification of analytical sizing and current iteration.
.include 'characterization_common.inc'
.include 'methodology_sizes.inc'
VDRV vdrv 0 DC 'SUPPLY'
VLOAD vload 0 DC 'SUPPLY'
VIN in 0 DC 0
XDRV in out vdrv 0 inv_char WN=4 WP='4*RATIO'
XLOAD out load_out vload 0 inv_char WN=4 WP='4*RATIO'
.dc VIN 0 'SUPPLY' 0.002 SWEEP DATA=dc_ratios
.measure dc ratio_used PARAM='RATIO'
.measure dc vm WHEN v(out)=v(in)
.measure dc isc_peak MAX PAR('-I(VDRV)')
.print dc v(in) v(out) I(VDRV)
.end
