import random

class RouletteWheel(object):
    MULTIPLIER = 1000
    BIGNUM = 65535
    
    def __init__(self, genearray):
        self.rwheel = []
        total = 0.0
        random.seed(a=None, version=2)
        
        if genearray is not None:
            for item in genearray:
                total = total + item.fitness
            index = 0
            for gene in genearray:
                entries = int(self.MULTIPLIER * (gene.fitness) / total)
                print('{0} : {1} : {2}'.format(str(index),
                                               str(gene.fitness),
                                               str(entries)))
                for i in range(0, entries):
                    self.rwheel.append(index)
                index += 1
        print(len(self.rwheel))
        print(self.rwheel)
        self.__shuffle()
        print(self.rwheel)

    def __roll(self):
        return (random.randint(0, self.BIGNUM)) % len(self.rwheel)
    
    def __shuffle(self):
        extent = len(self.rwheel)
        if extent > 2:
            for i in range(0, extent):
                first = self.__roll()
                secnd = first
                while secnd == first:
                    secnd = self.__roll()
                temp = self.rwheel[first]
                self.rwheel[first] = self.rwheel[secnd]
                self.rwheel[secnd] = temp
                
