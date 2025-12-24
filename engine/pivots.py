def pivot_levels(high, low, close):
    p = (high + low + close) / 3
    r1 = 2*p - low
    s1 = 2*p - high
    r2 = p + (high - low)
    s2 = p - (high - low)

    cpr_tc = (p + r1) / 2
    cpr_bc = (p + s1) / 2

    return {
        "P": p,
        "R1": r1, "R2": r2,
        "S1": s1, "S2": s2,
        "CPR_TC": cpr_tc,
        "CPR_BC": cpr_bc
    }
