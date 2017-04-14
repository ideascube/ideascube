import batinfo


class Lime2Battery(batinfo.Battery):
    @property
    def status(self):
        if self.charging == 0:
            return 'Discharging'

        elif self.capacity < 100:
            return 'Charging'

        else:
            return 'Full'


def get_batteries():
    batteries = batinfo.batteries()

    if batteries:
        return sorted(batteries.stat, key=lambda b: b.name.lower())

    try:
        # We might be running on a Lime2 Koombook
        # https://github.com/ideascube/ideascube/issues/446#issuecomment-244143565
        return [Lime2Battery(path='/sys/power/axp_pmu', name='battery')]

    except FileNotFoundError:
        return []
