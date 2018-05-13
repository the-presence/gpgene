from gene import Gene, debug
from roulettewheel import RouletteWheel

class Biquad(object):
    def __init__(self):
        self._z1 = 0.0
        self._z2 = 0.0
        self._a0 = 0.0
        self._a1 = 0.0
        self._a2 = 0.0
        self._b1 = 0.0
        self._b2 = 0.0

    def reset(self):
        self._z1 = 0.0
        self._z2 = 0.0
        self._a0 = 0.0
        self._a1 = 0.0
        self._a2 = 0.0
        self._b1 = 0.0
        self._b2 = 0.0

    @property
    def coeffs(self):
        retval = []
        retval.append(self._a0)
        retval.append(self._a1)
        retval.append(self._a2)
        retval.append(self._b1)
        retval.append(self._b2)
        return retval
        
    @coeffs.setter
    def coeffs(self, coeffs):
        self._a0 = coeffs[0]
        self._a1 = coeffs[1]
        self._a2 = coeffs[2]
        self._b1 = coeffs[3]
        self._b2 = coeffs[4]

    def score(self):
        retval = 0.0
        vals = self.scaled_signed_values()
        for val in vals:
            retval = retval + (0.5 - val)
        self.fitness = abs(1.0 - retval) / float(self.count)

    def process(self, inval):
        '''Transposed IIR Direct Form II'''
        outval = (self._a0 * inval) + self._z1
        self._z1 = (self._a1 * inval) + self._z2 - (self._b1 * outval)
        self._z2 = (self._a2 * inval) - (self._b2 * outval)
        return outval

class Cascade(object):
    def __init__(self, chromosome):
        self._stages = []
        if (chromosome.count() % 5) != 0:
            raise IndexError('Chromosome word count = {0} should be a multiple of 5'.format(str(chromosome.count())))
        all_coeffs = chromosome.scaled_signed_values()
        rows = chromosome.count() / 5
        for row in range(0, rows):
            coeffs = []
            for col in range(0,5):
                index = 5 * row + col
                coeffs.append(all_coeffs[index])
            stage = Biquad()
            stage.coeffs(coeffs)
            self._stages.append(stage)

    def process(self, inval):
        retval = inval
        for stage in self._stages:
            retval = stage.process(retval)
        return retval
            
if __name__ == '__main__':
    STAGES = []
    for i in range(0,10):
        STAGES.append(IIRSingleStage())
        STAGES[i].score()

    total = 0.0
    for i in range(0,10):
        print(STAGES[i])
        total = total + STAGES[i].fitness
    print(total)

    ourwheel = RouletteWheel(STAGES)
        
    
