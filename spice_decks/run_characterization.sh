#!/usr/bin/env bash
set -u
cd -- "$(dirname -- "${BASH_SOURCE[0]}")" || exit 1
command -v hspice >/dev/null 2>&1 || {
  printf 'ERROR: hspice no esta disponible en PATH.\n' >&2
  exit 1
}
out=$(mktemp -d "resultados_caracterizacion_$(date +%Y%m%d_%H%M%S)_XXXXXX") || exit 1
status=0
for deck in characterization_dc characterization_tran channel_discharge; do
  printf '\n=== %s ===\n' "$deck"
  if ! hspice -i "$deck.sp" -o "$out/$deck" >"$out/$deck.console.log" 2>&1; then
    printf 'ERROR: HSPICE fallo para %s\n' "$deck" >&2
    tail -n 20 "$out/$deck.console.log"
    status=1
  fi
  if [ ! -f "$out/$deck.lis" ]; then
    printf 'ERROR: falta %s.lis\n' "$deck" >&2
    status=1
    continue
  fi
  if grep -inE '\*\*error|job aborted|failed' "$out/$deck.lis"; then
    status=1
  fi
  grep -iE '\*\*warning|job concluded' "$out/$deck.lis" || true
  if ! grep -qi 'job concluded' "$out/$deck.lis"; then
    printf 'ERROR: no se confirma fin normal para %s\n' "$deck" >&2
    status=1
  fi
done
printf '\nConservar la carpeta completa: %s/%s\n' "$PWD" "$out"
exit "$status"
