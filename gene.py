import random
from bitstring import BitArray

DEBUG = True

def debug(stuff):
    if DEBUG is True:
        print(stuff)

        
class Gene(object):

    def __init__(self, word=16, count=0, randomise=True, mutator=0.1):
        # Representation values
        # Size of a data word
        self.__word = word
        # Number of data words in the chromosome
        self.__count = count
        # Resultant bit length
        self.__bits = self.__count * self.__word
        self.__chromosome = BitArray(self.__bits)

        # Derived constants
        # Scaling and masking value of the full bit field
        self.__mask = int(2 ** self.__word - 1)
        # For scaling signed ints
        self.__divisor = float((self.__mask + 1) / 2)
        # For scaling unsigned ints
        self.__unsigned_divisor = float(self.__mask + 1)

        # On to the business of reproduction
        # Probability of mutating a single bit
        self.__mutator = mutator
        # To be updated after testing
        self.__fitness = 0.0

        # Initialise randomness
        random.seed(a=None, version=2)
        if randomise is True:
            self.random_fill()

    def random_word(self):
        return random.randint(0, self.__mask)


    def random_fill(self):
        for i in range(0, self.__bits):
            self.__chromosome[i] = random.randint(0,1)

    @property
    def word(self):
        return self.__word

    @property
    def count(self):
        return self.__count

    @property
    def bits(self):
        return self.__bits

    @property
    def divisor(self):
        return self.__divisor

    @divisor.setter
    def divisor(self, value):
        self.__divisor = float(value)

    @property
    def fitness(self):
        return self.__fitness

    @fitness.setter
    def fitness(self, value):
        self.__fitness = float(value)

    @property
    def chromosome(self):
        return self.__chromosome

    def splice(self, mschrom, lschrom):
        debug('splicing')
        debug('{0} + {1}'.format(mschrom.bin, lschrom.bin))
        self.__chromosome = BitArray(mschrom)
        self.__chromosome += BitArray(lschrom)
        debug(self.__chromosome.bin)

    def chop(self, at):
        debug('chopping')
        debug(self.__chromosome.bin)
        sib01 = self.__chromosome[:at]
        sib02 = self.__chromosome[at:]
        debug('{0} + {1}'.format(sib01.bin, sib02.bin))
        return (sib01, sib02)

    def unscaled_signed_values(self):
        retval = []
        for value in self.__chromosome.cut(self.__word):
            retval.append(value.int)
        return retval

    def unscaled_unsigned_values(self):
        retval = []
        for value in self.__chromosome.cut(self.__word):
            retval.append(value.uint)
        return retval

    def scaled(self, value):
        return float(value / self.__divisor)

    def scaled_signed_values(self):
        retval = []
        for value in self.__chromosome.cut(self.__word):
            retval.append(float(value.int / self.__divisor))
        return retval

    def scaled_unsigned_values(self):
        retval = []
        for value in self.__chromosome.cut(self.__word):
            retval.append(float(value.uint / self.__unsigned_divisor))
        return retval

    def __str__(self):
        '''A nice formatted string representation of the Gene
        suitable for debugging and visual introspection purposes'''
        retvalbit = '\tWord       : {0}\n'.format(self.__word)
        retvalbit = '{0}\tCount      : {1}\n'.format(retvalbit, self.__count)
        retvalbit = '{0}\tBits       : {1}\n'.format(retvalbit, self.__bits)
        retvalbit = '{0}\tMask       : {1}\n'.format(retvalbit, bin(self.__mask))
        retvalbit = '{0}\tDivisor    : {1}\n'.format(retvalbit, self.__divisor)
        retvalbit = '{0}\tMutator    : {1}\n'.format(retvalbit, self.__mutator)
        retvalbit = '{0}\tFitness    : {1}\n'.format(retvalbit, self.__fitness)
        retvalbit = '{0}\tChromosome :\n'.format(retvalbit)
        
        for value in self.__chromosome.cut(self.__word):
            retvalbit = '{4}                     {0}\t{1}\t{2}\t{3}\n'.format(value.bin,
                                                                              value.hex,
                                                                              value.int,
                                                                              self.scaled(value.int),
                                                                              retvalbit)
        retval = '{0} : \n{1}'.format(self.__class__, retvalbit)
        return retval

    def __xover(self, coparent=None, at=0):
        '''Private cross-over implementation.

        If the cross-over point is supplied, it is forced to be
        within the correct range for the overall bitstring size
        of the chromosome.

        If the cross-over point is not supplied, a suitable one is
        randomly generated.

        The coparent must be of the same size as the parent,
        in this implementation.'''

        assert coparent is not None, 'No coparent presented'
        assert self.__bits == coparent.bits, 'Incompatible parent/coparent chromosome length'
        # Clean up any cheeky invalid target value
        xover_point = at % self.__bits
        # Oh dear, we need to set this ourselves
        while xover_point == 0:
            xover_point = random.randint(0, self.__bits)
        debug('Xover at bit : {0}'.format(xover_point))
        # Chop up the coparent chromosome at the cross-over point
        cosibs = coparent.chop(xover_point)
        # Chop up the our own chromosome at the cross-over point
        sibs = self.chop(xover_point)
        # Babies!
        sib01 = Gene(word=self.__word, count=self.__count, randomise=False)
        sib02 = Gene(word=self.__word, count=self.__count, randomise=False)
        # Distribute the genetic information, making sure that each
        # Sibling has exactly the correct length chromosome
        sib01.splice(sibs[0], cosibs[1])
        sib02.splice(cosibs[0], sibs[1])
        return (sib01, sib02)

    def mutate(self):
        '''The power of this technique is the fact that we can
        randomly mutate a bit in the chromosome.
        This is where the magic happens'''
        # This ensures we can set low probabilities without any
        # undue rounding error effects. Obviously, if you want to
        # set the Pratchett Probability ("It's a one in a million chance,
        # so it might just work!") this will need to be increased
        # commensurately
        MULTIPLIER = 10000
        chance = random.randint(0, MULTIPLIER)
        # Are we mutating here?
        if chance <= (int(MULTIPLIER * self.__mutator)):
            # Pick a bit
            target_bit = random.randint(0, self.__bits)
            debug('Mutated bit : {0}'.format(target_bit))
            debug(self.__chromosome.bin)
            # Flip it
            self.__chromosome.invert(target_bit)
            debug(self.__chromosome.bin)

    def reproduce_with(self, partner=None):
        # No self-reproduction
        assert partner is not None, 'No coparent presented'
        # I said, no self-reproduction
        assert partner != self, 'No self-reproduction.'
        # No cross-speciation
        assert self.__bits == partner.bits, 'Incompatible parent/coparent chromosome length'
        (sibA, sibB) = self.__xover(coparent=partner)
        sibA.mutate()
        sibB.mutate()
        return (sibA, sibB)
        
if __name__ == '__main__':
    TWORD = 32
    TCOUNT = 10
    CHROM01 = Gene(word=TWORD, count=TCOUNT)
    print(CHROM01)
    CHROM02 = Gene(word=TWORD, count=TCOUNT)
    print(CHROM02)
    (CHROM03, CHROM04) = CHROM01.reproduce_with(CHROM02)
    print(CHROM03)
    print(CHROM04)
    
