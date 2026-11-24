"""Editable diagram sources. Run: python diagrams.py (requires reportlab and Arial)."""
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Line, Polygon, String
from reportlab.graphics import renderSVG
from reportlab.lib import colors
import math

pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
INK=colors.HexColor('#172C40'); BLUE=colors.HexColor('#527796'); GREEN=colors.HexColor('#2F7664')
def txt(d,x,y,s,size=11,bold=False,color=INK,anchor='start'):
    s=s.replace('—','-').replace('–','-').replace('\u2011','-')
    d.add(String(x,y,s,fontName='Arial-Bold' if bold else 'Arial',fontSize=size,fillColor=color,textAnchor=anchor))
def wrap(s,width,size):
    rows=[]
    for para in s.split('\n'):
        line=''
        for word in para.split():
            trial=(line+' '+word).strip()
            if pdfmetrics.stringWidth(trial,'Arial',size)>width and line: rows.append(line);line=word
            else: line=trial
        rows.append(line)
    return rows
def box(d,x,y,w,h,title,body='',state='plan',fs=11):
    color=GREEN if state=='local' else BLUE if state=='plan' else colors.HexColor('#74828E')
    fill='#ECF6F0' if state=='local' else '#EFF4FA' if state=='plan' else '#F3F4F5'
    d.add(Rect(x,y,w,h,rx=9,ry=9,fillColor=colors.HexColor(fill),strokeColor=color,strokeWidth=1.3,strokeDashArray=[5,3] if state=='plan' else None))
    txt(d,x+12,y+h-22,title,12,True,color)
    lines=wrap(body,w-24,fs) if body else []
    assert 37+len(lines)*14<=h+8, (title,lines,h)
    for i,line in enumerate(lines): txt(d,x+12,y+h-40-14*i,line,fs)
def arrow(d,x1,y1,x2,y2,label='',ly=None,dash=False):
    d.add(Line(x1,y1,x2,y2,strokeColor=BLUE,strokeWidth=1.2,strokeDashArray=[4,3] if dash else None))
    a=math.atan2(y2-y1,x2-x1); z=7
    p=[x2,y2,x2-z*math.cos(a-.45),y2-z*math.sin(a-.45),x2-z*math.cos(a+.45),y2-z*math.sin(a+.45)]
    d.add(Polygon(p,fillColor=BLUE,strokeColor=BLUE))
    if label:
        cx=(x1+x2)/2; cy=(y1+y2)/2+8 if ly is None else ly
        width=pdfmetrics.stringWidth(label,'Arial',10)
        d.add(Rect(cx-width/2-3,cy-2,width+6,13,fillColor=colors.white,strokeColor=None))
        txt(d,cx,cy,label,10,anchor='middle')
def frame(d,x,y,w,h,label):
    d.add(Rect(x,y,w,h,fillColor=None,strokeColor=colors.HexColor('#B1BFCA'),strokeDashArray=[3,3],strokeWidth=.8))
    txt(d,x+8,y+h-15,label,10,color=BLUE)
def begin(code,title):
    d=Drawing(760,430); txt(d,12,410,code+'  '+title,17,True)
    txt(d,12,391,'24.11.2026 · cp2-docs-draft · целевая архитектура, сервер ещё не реализован',10,color=BLUE)
    txt(d,12,14,'Пунктир — план; зелёный — существующий Core; серый — внешний участник/инструмент.',9,color=BLUE)
    return d
def make_all():
    out=[]
    d=begin('D-01','Контекст системы · C4, уровень 1')
    box(d,20,245,190,92,'Игроки 2–4','Знакомые участники\nСоздатель начинает партию','actor')
    box(d,290,205,300,142,'Самый крутой орк','Программная система\nКомнаты, очередь, правила и очки\nВсе руки открыты внутри партии\nNFR-001/002/004/013')
    arrow(d,210,283,290,283,'Игра',ly=295)
    box(d,20,65,190,102,'Автор / проверяющий','Запуск, проверка и сопровождение учебного стенда','actor')
    arrow(d,210,115,440,115,'Проверки и обслуживание',ly=135); arrow(d,440,115,440,205)
    txt(d,290,78,'Граница системы включает Unity, API и хранение.',11)
    txt(d,290,58,'Внешние платные API для игры не нужны. ADR-001.',11)
    out.append(('D-01',d))

    d=begin('D-02','Контейнеры · C4, уровень 2')
    frame(d,10,185,740,180,'Граница программной системы')
    box(d,25,220,205,110,'Unity / Android','C# + UI Toolkit\nПоказ поля, команды, токен\nNFR-002/013')
    box(d,280,220,205,110,'Game API','ASP.NET Core 10\nКомнаты и подтверждение ходов\nNFR-001/004/006/007')
    box(d,535,220,195,110,'PostgreSQL 17','Участники, архивы, квитанции\nNFR-003/009')
    arrow(d,230,272,280,272,'HTTPS / JSON',ly=201)
    arrow(d,485,272,535,272,'SQL / TLS',ly=201)
    box(d,25,52,340,96,'Локальный режим уже написан','LocalMatchSession → Core → MatchSaveStore\nUnity UI ещё не проверен в редакторе.','local')
    box(d,400,52,330,96,'Две зоны доверия','Телефон не получает SQL и seed.\nAPI проверяет токен и сам определяет PlayerId.')
    out.append(('D-02',d))

    d=begin('D-02b','Компоненты API · C4, уровень 3')
    frame(d,12,42,735,327,'Один серверный процесс · ADR-001/002/003')
    box(d,27,238,200,100,'HTTP endpoints','DTO, лимит 16 КиБ, request ID\nNFR-001/007/011')
    box(d,282,238,200,100,'Room / MatchService','Транзакция, версия, повтор\nNFR-003/006')
    box(d,537,238,195,100,'Repository','PostgreSQL: архив и receipts\nNFR-003/009')
    arrow(d,227,284,282,284,'Команда',ly=296);arrow(d,482,284,537,284,'Данные',ly=296)
    box(d,27,70,200,105,'Auth + RateLimit','Токен → участник, host\nЛимит входа по коду\nNFR-004/005')
    box(d,282,70,200,105,'Core / GameEngine','Restore → Play → MatchView\nОбщие правила C#\nЛокально проверен; NFR-008','local')
    box(d,537,70,195,105,'ViewMapper','Открытые руки, поле и очки\nБез seed и чужих токенов\nNFR-004')
    arrow(d,127,238,127,175,'Доступ',ly=202)
    arrow(d,382,238,382,175,'Правила',ly=202)
    d.add(Line(460,238,460,206,strokeColor=BLUE,strokeWidth=1.2))
    arrow(d,460,206,635,206,'Ответ DTO',ly=216);arrow(d,635,206,635,175)
    out.append(('D-02b',d))

    d=begin('D-03','Развёртывание учебного стенда')
    box(d,17,245,140,90,'Клиент','Телефон / HTTP-клиент','actor')
    frame(d,190,50,555,317,'Учебный Linux-хост · 2 vCPU / 4 ГБ · ADR-002/003')
    box(d,207,242,190,100,'Reverse proxy','HTTPS :443\n≤128 МиБ, TLS-секрет')
    box(d,489,242,238,100,'Контейнер API','Внутренний :8080; ≤768 МиБ\n/health и /ready\nNFR-010/011/012')
    arrow(d,157,285,207,285,'HTTPS',ly=298);arrow(d,397,285,489,285,'HTTP',ly=298)
    box(d,489,77,238,110,'Контейнер PostgreSQL','Внутренний :5432; ≤1024 МиБ\nИменованный том данных\nПароль из среды; NFR-003/009')
    box(d,207,77,190,110,'Резервная копия','Отдельно от тома БД\nКаждые 15 мин\nRTO ≤5 мин; RPO ≤15 мин')
    arrow(d,609,242,609,187,'SQL',ly=211);arrow(d,489,130,397,130,'Backup',ly=144)
    out.append(('D-03',d))

    d=begin('D-04','План CI/CD · выполнение пока отсутствует')
    box(d,23,243,210,102,'PR / push','Чистый checkout\nSDK + lock-файл\nNFR-010/012','actor')
    box(d,276,243,210,102,'КТ-2: статический контроль','Формат, OpenAPI, компиляция\nПоиск секретов\nNFR-008/012')
    box(d,529,243,210,102,'КТ-2: тесты и сборка','Unit + integration, образ\nЛоги, исходное покрытие\nЛюбая ошибка → failed')
    arrow(d,233,292,276,292,'Код',ly=304);arrow(d,486,292,529,292,'Gate',ly=304)
    box(d,529,77,210,108,'КТ-3: registry','Проверенный образ\nНеизменяемый SHA / digest\nСохранить предыдущую версию')
    box(d,276,77,210,108,'КТ-3: deploy + smoke','Учебная VM, миграция\nReadiness + создать / сыграть\nРучное approval допустимо')
    box(d,23,77,210,108,'КТ-4: откат','Предыдущий digest + smoke\nСовместимая схема / restore\nNFR-009/010')
    arrow(d,635,243,635,185,'Только зелёный CI',ly=211)
    arrow(d,529,130,486,130,'Deploy',ly=143);arrow(d,276,130,233,130,'Отказ',ly=143)
    out.append(('D-04',d))

    d=begin('D-05','Схема хранения · PostgreSQL, проект')
    box(d,20,231,330,125,'rooms','PK room_id; UNIQUE code\nhost_member_id; status; version\nСостав 1–4, старт 2–4; host из своей комнаты')
    box(d,410,231,330,125,'members','PK member_id; FK room_id\nseat; name; token_hash UNIQUE\nUNIQUE(room_id, seat), seat 0–3')
    arrow(d,350,286,410,286,'1 : 1..4',ly=299)
    box(d,20,56,330,125,'matches','PK match_id; FK room_id UNIQUE\nversion; rules_version; status\narchive JSONB: initialDeal, names, commands ≤90')
    box(d,410,56,330,125,'receipts','PK(scope_key, command_id)\nrequest_hash; response_status\nresponse_encrypted; created_at')
    arrow(d,185,231,185,181,'1 : 0..1',ly=204)
    arrow(d,350,114,410,114,'Квитанции',ly=127,dash=True)
    txt(d,410,205,'Scope: операция + владелец + агрегат.',10)
    txt(d,20,35,'ADR-002 · NFR-003/004/006/009 · JSONB не выдаётся клиенту; миграции ещё не написаны.',10)
    out.append(('D-05',d))

    def sequence(code,title,names,positions,events):
        d=begin(code,title)
        for name,x in zip(names,positions):
            box(d,x-70,340,140,36,name,fs=10)
            d.add(Line(x,337,x,48,strokeColor=colors.HexColor('#CCD5DD'),strokeDashArray=[3,3]))
        for y,a,b,label,dash in events:
            arrow(d,positions[a],y,positions[b],y,label,ly=y+7,dash=dash)
        return d
    d=sequence('D-06','Принять ход: запрос → правила → БД → ответ',
        ['Клиент','MatchService','Core','PostgreSQL'],[84,283,480,677],[
        (306,0,1,'POST /moves: ID + версия',False),
        (260,1,3,'BEGIN; lock; проверить квитанцию / версию',False),
        (215,1,2,'Restore + Play',False),
        (175,2,1,'Архив и MatchView',False),
        (130,1,3,'UPDATE архив + INSERT receipt; COMMIT',False),
        (78,1,0,'200: новая версия поля',False)])
    txt(d,20,33,'До применения: токен → участник; ошибки не меняют состояние. ADR-001/002 · NFR-003/004/006.',10)
    out.append(('D-06',d))
    d=sequence('D-07','Ответ потерян: повтор не выполняет ход снова',
        ['Клиент','MatchService','PostgreSQL'],[85,380,675],[
        (307,1,2,'Архив + квитанция; COMMIT',False),
        (269,2,1,'COMMIT подтверждён',False),
        (231,1,0,'200 потерян в сети',True),
        (191,0,1,'Повтор: тот же ID, тело и токен',False),
        (153,1,2,'Найти receipt; сверить hash',False),
        (115,2,1,'Ранее записанный ответ',False),
        (72,1,0,'200 + Idempotency-Replayed',False)])
    txt(d,20,34,'Затем GET актуального поля. Другой hash → 409; Core не вызывается повторно. NFR-002/003/006.',10)
    out.append(('D-07',d))
    return out

if __name__=='__main__':
    for code,d in make_all(): renderSVG.drawToFile(d,str(Path(__file__).parent/(code+'.svg')))
