A idéia deste sistema é ter uma versão mais power de N900 Notifier (http://sourceforge.net/projects/n900notifier/)
Claro que há muitas falhas de segurança ao se fazer isto... :P

device-> versão que deve ir no dispositivo controlado  (no fim deve funcionar como simples proxy dbus)
pc -> versão que deve ir no dispositivo controlador
maemo-controler-kupfer-client -> plugin para o kupfer que apresenta um interface amigável

Como deve funcionar:
1 opção:
    STRUPATOR MODE: captar todas as mensagens do device e mandar para o PC e vice versa.
    Vantagens:
        Flexibilidade
    Desvantagens:
        Possivel lentidão ou uso desnecessário de recursos (memoria, cpu)

2 opção:
    ESPECIFIC MODE: captar somente as mensagens que sejam de meu interesse e repassa-las
    Vantagens:
        Usa-se recursos de ambos os aparelhos somente para o que for necessário ou desejado
    Desvantagens:
        Inflexível, só será possível trabalhar com as mensagens pre definidas

Além deste ponto outro ponto:
1 criar um wrapper:
    vantagem:
        evitar conflitos
        permite criar uma interface própria independente do aparelho
    desvantagem:
        retrabalho
        curva de aprendizado

2 não criar um wrapper:
    inverso ao anterior