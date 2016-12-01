import batinfo


def get_batteries():
    batteries = batinfo.batteries()

    if batteries:
        return batteries.stat

    else:
        return []
