import math
import struct


SUPPLY = 1.8
WN = 0.36
# (K'L in microampere/V^2, VT magnitude in V, ION/W in microampere/micrometer)
PARAMETERS = {"n": (256.0, 0.58, 475.0), "p": (52.0, 0.65, 170.0)}


def critical_voltage(kind):
    kp, threshold, ion = PARAMETERS[kind]
    gain = kp / 0.18
    overdrive = SUPPLY - threshold
    denominator = gain * overdrive**2 - 2 * ion
    if denominator <= 0:
        raise ValueError("ION calibration cannot produce a positive critical voltage")
    return 2 * ion * overdrive / denominator


def current_per_width(kind, gate, drain):
    """Weste 4th ed., Eqs. 2.26-2.28; microampere/micrometer, magnitudes."""
    kp, threshold, _ = PARAMETERS[kind]
    overdrive = max(gate - threshold, 0.0)
    critical = critical_voltage(kind)
    saturation = critical * overdrive / (critical + overdrive)
    voltage = min(max(drain, 0.0), saturation)
    return (kp / 0.18) * (overdrive * voltage - voltage * voltage / 2) / (
        1 + voltage / critical
    )


def vtc(vin, ratio):
    low, high = 0.0, SUPPLY
    for _ in range(70):
        out = (low + high) / 2
        balance = current_per_width("n", vin, out) - ratio * current_per_width(
            "p", SUPPLY - vin, SUPPLY - out
        )
        if balance > 0:
            high = out
        else:
            low = out
    return (low + high) / 2


def switching_voltage(ratio):
    low, high = 0.0, SUPPLY
    for _ in range(70):
        vin = (low + high) / 2
        balance = current_per_width("n", vin, vin) - ratio * current_per_width(
            "p", SUPPLY - vin, SUPPLY - vin
        )
        if balance > 0:
            high = vin
        else:
            low = vin
    return (low + high) / 2


def on_resistance(kind):
    """RC-equivalent resistance from integral over VDD down to VDD/2."""
    steps = 1000
    increment = 0.9 / steps
    total = 0.0
    for i in range(steps + 1):
        drain = 0.9 + increment * i
        current = WN * current_per_width(kind, SUPPLY, drain) * 1e-6
        weight = 1 if i in (0, steps) else (4 if i % 2 else 2)
        total += weight / current
    return total * increment / (3 * math.log(2))


def fo1_sizing(rn, rp, load_constant, load_slope):
    """Rabaey Sec. 5.4.3 with CL=A+B*r; resistances at equal reference width."""
    values = (rn, rp, load_constant, load_slope)
    if any(not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("FO1 sizing requires finite positive resistances and capacitances")
    symmetric_ratio = rp / rn
    return {
        "symmetric_ratio": symmetric_ratio,
        "free_ratio": math.sqrt(load_constant * rp / (load_slope * rn)),
        "symmetric_delay_s": math.log(2) * rn * (
            load_constant + load_slope * symmetric_ratio
        ),
    }


def read_hspice_2013_transient(path):
    """Read only the verified little-endian 2013 mixed-precision sweep format."""
    binary = path.read_bytes()
    offset = 0
    records = []
    while offset < len(binary):
        if offset + 20 > len(binary):
            raise ValueError("Truncated HSPICE record")
        first, count, third, size = struct.unpack_from("<4i", binary, offset)
        if first != 4 or third != 4 or count * (8 if not records else 4) != size:
            raise ValueError("Unsupported HSPICE record framing")
        end = offset + 16 + size
        if end + 4 > len(binary) or struct.unpack_from("<i", binary, end)[0] != size:
            raise ValueError("Invalid HSPICE record trailer")
        records.append(binary[offset + 16:end])
        offset = end + 4
    header = records[0].decode("ascii")
    if header[20:24] != "2013":
        raise ValueError("Only HSPICE 2013 time-double format is supported")
    fields = header[header.index("TIME"):].split()
    expected = ["TIME", "v(0", "v(in", "v(load_out", "v(out", "v(vdrv",
                "v(vload", "i(vdrv", "i(vin", "i(vload", "ratio", "$&%#"]
    if fields != expected:
        raise ValueError(f"Unsupported waveform columns: {fields}")
    payload = b"".join(records[1:])
    offset = 0
    sweeps = []
    while offset < len(payload):
        ratio = struct.unpack_from("<f", payload, offset)[0]
        offset += 4
        rows = []
        while True:
            if offset + 8 > len(payload):
                raise ValueError("Missing sweep terminator")
            time = struct.unpack_from("<d", payload, offset)[0]
            if math.isclose(time, 1e30, rel_tol=1e-12):
                offset += 8
                break
            if offset + 44 > len(payload):
                raise ValueError("Truncated mixed precision row")
            row = struct.unpack_from("<d9f", payload, offset)
            if not all(math.isfinite(x) for x in row) or (
                rows and row[0] <= rows[-1][0]
            ):
                raise ValueError("Invalid waveform row or non-increasing time")
            rows.append(row)
            offset += 44
        if not rows or rows[0][0] != 0:
            raise ValueError("Unexpected transient start")
        sweeps.append((ratio, rows))
    return sweeps


def crossings(rows, column, rising, threshold=0.9):
    times = []
    for a, b in zip(rows, rows[1:]):
        va, vb = a[column], b[column]
        crossed = va < threshold <= vb if rising else va > threshold >= vb
        if crossed:
            times.append(a[0] + (b[0] - a[0]) * (threshold - va) / (vb - va))
    return times


def waveform_window(rows, column, start, stop):
    if not rows[0][0] <= start < stop <= rows[-1][0]:
        raise ValueError("Waveform does not cover requested time window")

    def at(time):
        for a, b in zip(rows, rows[1:]):
            if a[0] <= time <= b[0]:
                return a[column] + (b[column] - a[column]) * (time - a[0]) / (b[0] - a[0])
        raise ValueError("Cannot interpolate waveform endpoint")

    return [(start * 1e12, at(start))] + [
        (row[0] * 1e12, row[column]) for row in rows if start < row[0] < stop
    ] + [(stop * 1e12, at(stop))]
