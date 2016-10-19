"""
gencc: A simple program to generate credit card numbers that pass the MOD 10 check
(Luhn formula).
Usefull for testing e-commerce sites during development.

Copyright 2003 Graham King

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from random import Random
import copy

visaPrefixList = [     ['4', '5', '3', '9'], 
                    ['4', '5', '5', '6'], 
                       ['4', '9', '1', '6'],
            ['4', '5', '3', '2'], 
            ['4', '9', '2', '9'],
            ['4', '0', '2', '4', '0', '0', '7', '1'],
            ['4', '4', '8', '6'],
            ['4', '7', '1', '6'],
            ['4'] ]

mastercardPrefixList = [    ['5', '1'],
                            ['5', '2'],
                            ['5', '3'],
                            ['5', '4'],
                            ['5', '5'] ]

amexPrefixList = [  ['3', '4'],
                    ['3', '7'] ]

discoverPrefixList = [ ['6', '0', '1', '1'] ]

dinersPrefixList = [    ['3', '0', '0'],
                        ['3', '0', '1'],
                        ['3', '0', '2'],
                        ['3', '0', '3'],
                        ['3', '6'],
                        ['3', '8'] ]

enRoutePrefixList = [   ['2', '0', '1', '4'],
                        ['2', '1', '4', '9'] ]

jcbPrefixList16 = [   ['3', '0', '8', '8'],
                    ['3', '0', '9', '6'],
                    ['3', '1', '1', '2'],
                    ['3', '1', '5', '8'],
                    ['3', '3', '3', '7'],
                    ['3', '5', '2', '8'] ]

jcbPrefixList15 = [ ['2', '1', '0', '0'],
                    ['1', '8', '0', '0'] ]

voyagerPrefixList = [ ['8', '6', '9', '9'] ]                    
                    

"""
'prefix' is the start of the CC number as a string, any number of digits.
'length' is the length of the CC number to generate. Typically 13 or 16
"""
def completed_number(generator, prefix, length):
    ccnumber = prefix

    # generate digits
    while len(ccnumber) < (length - 1):
        digit = generator.choice(['0',  '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        ccnumber.append(digit)

    # Calculate _sum 

    _sum = 0
    pos = 0

    reversedCCnumber = []
    reversedCCnumber.extend(ccnumber)
    reversedCCnumber.reverse()

    while pos < length - 1:
        odd = int( reversedCCnumber[pos] ) * 2
        if odd > 9:
            odd -= 9
        _sum += odd
        if pos != (length - 2):
            _sum += int( reversedCCnumber[pos+1] )
        pos += 2

    # Calculate check digit

    checkdigit = ((_sum / 10 + 1) * 10 - _sum) % 10

    ccnumber.append( str(checkdigit) )
    
    return ''.join(ccnumber)

def credit_card_number(generator, prefixList, length, howMany):

    result = []

    for __ in range(howMany):
   
        ccnumber = copy.copy( generator.choice(prefixList) )

        result.append( completed_number(generator, ccnumber, length) )

    return result

def output(title, numbers):

    result = []
    result.append(title)
    result.append( '-' * len(title) )
    result.append( '\n'.join(numbers) )
    result.append( '' )

    return '\n'.join(result)

#
# Main
#

#generator = Random()
#generator.seed()        # Seed from current time

#print "darkcoding credit card generator "
#print

#mastercard = credit_card_number(generator, mastercardPrefixList, 16, 10)
#print output("Mastercard", mastercard)

#visa16 = credit_card_number(generator, visaPrefixList, 16, 1)
#print output("VISA 16 digit", visa16)
#print visa16[0]

#visa13 = credit_card_number(generator, visaPrefixList, 13, 5)
#print output("VISA 13 digit", visa13)

#amex = credit_card_number(generator, amexPrefixList, 15, 5)
#print output("American Express", amex)

# Minor cards

#discover = credit_card_number(generator, discoverPrefixList, 16, 3)
#print output("Discover", discover)

#diners = credit_card_number(generator, dinersPrefixList, 14, 3)
#print output("Diners Club / Carte Blanche", diners)

#enRoute = credit_card_number(generator, enRoutePrefixList, 15, 3)
#print output("enRoute", enRoute)

#jcb15 = credit_card_number(generator, jcbPrefixList15, 15, 3)
#print output("JCB 15 digit", jcb15)

#jcb16 = credit_card_number(generator, jcbPrefixList16, 16, 3)
#print output("JCB 16 digit", jcb16)

#voyager = credit_card_number(generator, voyagerPrefixList, 15, 3)
#print output("Voyager", voyager)

__kupfer_name__ = _("Credit Card Generator")
__kupfer_sources__ = ("GenCCSource", )
__description__ = _("Create Random Credit Card Numbers")
__version__ = "0.1.0"
__author__ = "Hugo Ribeiro"

from kupfer.obj.objects import TextLeaf
from kupfer.obj.grouping import ToplevelGroupingSource

#the sources
class GenCCSource (ToplevelGroupingSource):
    CARD_TYPES = {
        'mastercard': (mastercardPrefixList, 16, 3),
        'visa16': (visaPrefixList, 16, 3),
        'visa13': (visaPrefixList, 13, 1),
        'amex': (amexPrefixList, 15, 3),
        'discover': (discoverPrefixList, 16, 1),
        'diners': (dinersPrefixList, 14, 1),
        'enRoute': (enRoutePrefixList, 15, 1),
        'jcb15': (jcbPrefixList15, 15, 1),
        'jcb16': (jcbPrefixList16, 16, 1),
        'voyager': (voyagerPrefixList, 15, 1)
    }
    
    def __init__(self):
        ToplevelGroupingSource.__init__(self, _("CreditCards"), "creditcards")
        self._version = 1
            
    def get_items(self):
        generator = Random()
        generator.seed()
        
        for name, params in GenCCSource.CARD_TYPES.items():
            cards = credit_card_number(generator, *params)
            for card in cards:
                yield TextLeaf(card, name)
