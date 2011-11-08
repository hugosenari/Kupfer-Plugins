from functools import wraps

def test(f, *args, **kw):
    f.n = f.n + 1 if hasattr(f, 'n') else 1
    print f.n
    @wraps(f)
    def te(*args, **kw):
        if len(args):
            if hasattr(args[0], f.func_name) and id(f) == id(getattr(args[0], f.func_name)):
                print 'objecto', `args[0]`
        return f(*args, **kw)
    return te

@test
def tes(bla=0, ble=None):
    print "tes"
    print bla, ble
    

tes()
#tes(1,2)

class Clas (object):
    @test
    def __init__(self=None, val=None):
        print "init clas"
        print self

#cl = Clas()
#cll = Clas(1)
#print id(cl.__init__)

@player
class Player(object):
    pass

ps = Player.players(match="gmusicbrowser")
p = Player.first_player("gmusicbrowser")

p.play() | p > 0
p.play(music) | p > music | p >= music #music qualquer coisa com metodo .uri()

p.pause() | p == 0
p.pause_play() | p >= 0
#n = qualquer inteiro
p.position(n) | p > n
p.position(-n)| p < n

p.seek(n) #| p >= n
p.seek(-n)#| p <= n

p.next()  | p >> 1
p.next(n) | p >> n #[p.next() for x in range(n)]
p.prev()  | p << 1
p.prev(n) | p << n #[p.prev() for p in range(n)]

pl = p.playlist()
pl.length() | len(pl)
