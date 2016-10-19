import random
import math
from itertools import repeat


def gera_random(n):
    """ Funcao para gerar um inteiro randomico entre 0 e 9 """
    return random.randint(1,9)

def mod(dividendo,divisor):
    """ Funcao pra retornar o resto da divisao de dois numeros """
    x = dividendo - (math.floor(dividendo/divisor)*divisor)
    return round(x)

def cpf():
    """ Funcao pra gerar o bendito cpf """
    
    # Gera os numeros randonomicos ;)
    n = 9
    n1 = gera_random(n)
    n2 = gera_random(n)
    n3 = gera_random(n)
    n4 = gera_random(n)
    n5 = gera_random(n)
    n6 = gera_random(n)
    n7 = gera_random(n)
    n8 = gera_random(n)
    n9 = gera_random(n)
    
    # debugger purposes ;)
    #print n1,n2,n3,n4,n5,n6,n7,n8,n9
    
    # Contas e mais contas, dividir pra fica mais bonitinho
    a1 = n9 * 2
    a2 = n8 * 3
    a3 = n7 * 4
    a4 = n6 * 5 
    a5 = n5 * 6
    a6 = n4 * 7
    a7 = n3 * 8
    a8 = n2 * 9
    a9 = n1 * 10
    
    # Soma os resultados de todas as contas anteriores e faz 
    # outra continha.. tudo regra do cpf, para ele ser valido :P
    d1 = a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9
    d1 = 11 - (mod(d1,11))
    
    # Caso d1 for maior que 10, o que nao pode ele sera igualado a 0
    if d1>=10:
        d1 = 0

    # debugger purposes
    #print n1,n2,n3,n4,n5,n6,n7,n8,n9
    
    # Mesma coisa da de cima so que agora pra variavel d2
    a1 = d1 * 2
    a2 = n9 * 3
    a3 = n8 * 4
    a4 = n7 * 5
    a5 = n6 * 6
    a6 = n5 * 7
    a7 = n4 * 8
    a8 = n3 * 9
    a9 = n2 * 10
    a10 = n1 * 11
    
    # ... rola a barra de rolagem pra cima que tu vai entender :P
    d2 = a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9 + a10
    d2 = 11 - (mod(d2,11))
    
    # chega de repeticao de codigo :)
    if d2 >= 10:
        d2 = 0
    
    # debugger purposes
    #print n1,n2,n3,n4,n5,n6,n7,n8,n9
    return "%d%d%d%s%d%d%d%s%d%d%d%s%d%d" % (n1,n2,n3,'',n4,n5,n6,'',n7,n8,n9,'',d1,d2)
    
__kupfer_name__ = _("Gerador de CPF")
__kupfer_sources__ = ("GenCPFSource", )
__description__ = _("Gera uma lista de CPF")
__version__ = "0.1.0"
__author__ = "Hugo Ribeiro"

from kupfer.obj.objects import TextLeaf
from kupfer.obj.grouping import ToplevelGroupingSource


#the sources
class GenCPFSource (ToplevelGroupingSource):
    def __init__(self):
        ToplevelGroupingSource.__init__(self, _("CPFs"), "cpfs")
        self._version = 1
            
    def get_items(self):
        for get_cpf in repeat(cpf, 9):
            yield TextLeaf(get_cpf())
