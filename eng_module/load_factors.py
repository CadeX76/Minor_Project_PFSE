AREMA_COMBINATIONS = {
    'SLD_G1': {'D': 1., 'L': 1., 'I': 1., 'CF': 1., 'E': 1., 'B': 1., 'SF': 1.},
    'SLD_G2': {'D': 1., 'E': 1., 'B': 1., 'SF': 1., 'W': 1.},
    'SLD_G3': {'D': 1., 'L': 1., 'I': 1., 'CF': 1., 'E': 1., 'B': 1., 'SF': 1.,'W': 0.5, 'WL': 1., 'LF': 1., 'F': 1.},
    'LFD_G1': {'D': 1.4, 'L': 1.4 * 5 / 3, 'I': 1.4 * 5 / 3, 'CF': 1.4, 'E': 1.4, 'B': 1.4, 'SF': 1.4},
    'LFD_G2': {'D': 1.8, 'L': 1.8, 'I': 1.8, 'CF': 1.8, 'E': 1.8, 'B': 1.8, 'SF': 1.8}
}

EC_COMBINATIONS = {
    'ULS_01': {'D_factor': 1.35, 'L_factor': 1.5},
    'ULS_02': {'D_factor': 1.0, 'L_factor':1.5},
    'ULS_03': {'D_factor': 1.35, 'L_factor': 0.}
}

def factor_load(
    D_factor: float = 0.,
    D: float = 0.,
    L_factor: float = 0.,
    L: float = 0.,
)-> float:
    '''
    Returns the factored load for the given load factors and loads
    '''
    factored_load = (
        D_factor * D
        + L_factor * L
    )

    return factored_load