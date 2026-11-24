from abc import ABC, abstractclassmethod


class Animal(ABC): 

    @abstractclassmethod
    def falar(self):
        pass
        #print("eita")

    def dormir(self):
        print("zzzzz")


class Cachorro(Animal):
    def falar(self):
        return "Auuu!"

class Gato(Animal):
    def falar(self):
        return "Miauuu!"


# animal = Animal() 
""" Error pois animal tem methodo abstrato n pode ser implementado"""

c = Cachorro()
g = Gato()

print(g.falar())
print(f"\n")
print(c.falar())

print(f"\n")
print("Gato: ")
g.dormir()
print(f"Cachorro: ")
c.dormir()

