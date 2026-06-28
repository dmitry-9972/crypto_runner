def slash_to_underscore_formatter(str):
    "BP/USDT" '->' 'BP_USDT'
    return str.replace('/', '_')

def remove_slash_and_add_m_formatter(str):
    "BP/USDT" '->' 'BPUSDTM'
    return str.replace('/', '')+'M'

def remove_slash_formatter(str):
    "BP/USDT" '->' 'BPUSDT'
    return str.replace('/', '')

def dash_formatter(str):
    "BP/USDT" '->' 'BPU-SDTM'
    return str.replace('/', '-')