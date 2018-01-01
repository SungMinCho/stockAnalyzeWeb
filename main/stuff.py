def human_readable_float(f):
    save_f = f
    if f < 0:
        f = -f
    s = ""
    q = f // 100000000
    if q > 0:
        s += str(int(q)) + '억'

    f = f % 100000000
    q = f // 10000
    if q > 0:
        s += str(int(q)) + '만'

    f = f % 10000
    f = int(f)
    s += str(f) + '원'
    if save_f < 0:
        s = '-' + s
    return s


