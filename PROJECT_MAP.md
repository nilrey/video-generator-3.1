## make_map.py — 
- def is_excluded(name, patterns) 

## stage\__init__.py — Пакет stage: постановка сцен из объектов (движок, материалы, библиотека объектов).

## stage\core.py — Движок stage: реестр объектов, события по словам, состояние как функция времени, проверка, манифест.
- def P(kind, default=None, lo=None, hi=None, choices=None, anim=False, desc='') Описание параметра объекта: тип kind (num, str, choice, bool), границы, значение по умолчанию, можно ли менять событием.
- def obj(name, desc, tags, size, params=None, anchors=None, full=False) Регистрация объекта. draw(c, p, t): c - холст слоя, p - значения параметров, t - время в секундах.
- def _clamp(x) Ограничить x диапазоном 0..1.
- def _isnum(v) Число, но не bool.
- def _numlike(v) Число или непустой список чисел (такие значения меняются плавно).
- def mixval(a, b, k) Интерполяция значения a к b на долю k; числа и списки плавно, прочее переключается сразу.
- def value(init, evs, t, n=None) Значение параметра в момент t. evs: [(start, dur, target, ease)] по возрастанию start.
- def _norm(x) Строка в нижнем регистре без знаков препинания для сравнения слов.
- def find_word(words, query, nth=1) Индекс слова сцены, начинающегося с query (nth-е вхождение); ValueError, если слова нет.
- def event_time(ev, sc) Время события в секундах от начала сцены.
- def _defaults(typ) Значения по умолчанию общих и собственных параметров типа typ.
- class Stage: __init__, value_of, state, anchor_pos, render
- def _okval(pd, v) Допустимо ли значение v для описания параметра pd.
- def check_params(p, words=None, prev_objs=None) Проверка ill_params сцены stage. Возвращает список ошибок (пусто = все хорошо).
- def manifest() Список описаний зарегистрированных объектов в виде словарей.
- def manifest_text() Манифест для промпта LLM.

## stage\demo_cloud.py — Пилот: ролик "Что такое облако". Запуск из папки выше пакета: python3 -m stage.demo_cloud
- def load_timeline() Загрузить vg.timeline проекта или копию timeline.py рядом.
- def caption(im, sc, t_abs, k) Упрощенные субтитры для демо: произнесенные слова светлые.
- def main(name='cloud_pilot') Прогнать examples/<name>.json: проверка, замер скорости, контрольный лист PNG и видео MP4.

## stage\gate.py — Ворота для новых объектов от LLM: статическая проверка кода и стиля, контракт, тест-рендер, превью.
- def _const(e) Выражение состоит только из числовой константы (в том числе отрицательной).
- def style_check(tree) Правила стиля, из-за которых LLM чаще всего ошибается: альфа кортежем и рамки из выражений.
- def static_check(src, style=True) Статический анализ исходника объекта: запрещенные импорты, вызовы, атрибуты, символы и (при style) правила стиля.
- def contract_check(spec) Проверка контракта зарегистрированного объекта; возвращает список ошибок.
- def _variants(pd) Два заметно разных значения параметра для проверки его влияния на картинку.
- def layout_check(name) Рисунок должен лежать в допустимой области, быть заметным, а параметры должны менять картинку.
- def _extremes(spec) Наборы параметров для тест-рендера: по умолчанию, минимумы, максимумы, все варианты choice.
- def run(path, preview=None, legacy=False) Полная проверка файла объекта: код, стиль, контракт, тест-рендер, превью; возвращает отчет-словарь.

## stage\mat.py — Материалы и холст для stage. Все координаты логические: 540x960, k = пикселей на единицу.
- def tc(name) 
- def lite(c, k) 
- def dark(c, k) 
- def set_font_loader(fn) В проекте: set_font_loader(lambda size: vg.fonts.font('xb', size)).
- def _project_font(size) 
- def fnt(size) Шрифт: загрузчик из set_font_loader, иначе шрифт проекта (vg.fonts), иначе системный.
- def _grad(w, h, stops, horizontal) 
- def _warn(msg) Запомнить замечание (без повторов), чтобы ворота показали его автору предмета.
- def rgba(c, a=255) Цвет RGBA из цвета c (первые три числа) и прозрачности a; старая прозрачность заменяется.
- def _col(c) Привести цвет к кортежу из 3 или 4 целых 0..255; лишние числа: первые три и последнее как прозрачность.
- def _box(b) Проверить рамку (x0, y0, x1, y1); ошибка при отрицательном размере (частая путаница с x, y, ширина, высота).
- def box(x0, y0, x1, y1) Рамка по углам: левый верхний (x0, y0) и правый нижний (x1, y1).
- def box_xywh(x, y, w, h) Рамка по левому верхнему углу (x, y) и размерам w, h.
- def box_c(cx, cy, w, h) Рамка по центру (cx, cy) и размерам w, h.
- class C: __init__, px, _trans, _shade, line, circle, rrect, poly, shade_circle, shade_rrect, shade_poly, text, fit_text, blit, glow
- def grad_rrect(c, box, r, stops, horizontal=False, alpha=255) 
- def metal(c, box, r=4) 
- def panel(c, box, col, r=16) 
- def plate(c, box, text, size=16, col=None) 
- def shadow(c, box, r=10, dy=10, rad=12, a=150) 
- def led(c, xy, r, col, on=True) 
- def file_card(c, cx, cy, w, h, col, kind='doc') 
- def fill_shape(c, box, fn, stops) Закрасить форму вертикальным градиентом. fn(sub) рисует форму любым непрозрачным цветом в координатах холста.
- def make_bg(theme, k, floor=FLOOR) 
- def floor(c, y=FLOOR, depth=100) 

## stage\objects\__init__.py — Библиотека объектов stage: импорт модулей регистрирует объекты.

## stage\objects\activation_curve.py — 
- def draw(c, p, t) 

## stage\objects\badge.py — Объект badge: темная плашка-подпись с цветной точкой.
- def draw(c, p, t) Нарисовать плашку с текстом label.

## stage\objects\cloud.py — Объект cloud: объемное облако с подписью.
- def _shape(s) Силуэт облака (белые круги и основание) для заливки градиентом.
- def draw(c, p, t) Нарисовать облако; pulse меняет яркость.

## stage\objects\device.py — Объект device: ноутбук или телефон с экраном (пусто, файл, галочка, крест).
- def _screen(c, box, mode, col, t) Экран устройства в режиме mode (blank, file, ok, cross).
- def draw(c, p, t) Нарисовать устройство kind (laptop или phone) по параметрам p.

## stage\objects\filecard.py — Объект file: карточка файла (документ, фото, данные) с подписью.
- def draw(c, p, t) Нарисовать карточку файла и подпись label.

## stage\objects\gauge.py — Объект gauge: полукруглый индикатор нагрузки со стрелкой и цветными зонами.
- def _zone(f) Цвет зоны шкалы от зеленого через желтый к красному по доле f.
- def draw(c, p, t) Нарисовать шкалу, стрелку по value и подпись.

## stage\objects\input_vector.py — 
- def draw(c, p, t) 

## stage\objects\link.py — Объект link: линия связи между точками привязки с бегущими пакетами данных.
- def bez(a, b, bend, u) Точка на квадратичной кривой Безье от a до b (изгиб bend) в доле u.
- def draw(c, p, t) Нарисовать линию до доли progress и пакеты с интенсивностью flow.

## stage\objects\lock.py — Объект lock: навесной замок, закрытый или открытый.
- def draw(c, p, t) Нарисовать замок; locked выбирает положение дужки.

## stage\objects\plug.py — Объект plug: вилка питания над розеткой, при выдергивании проскакивает искра.
- def draw(c, p, t) Нарисовать розетку, вилку, кабель и искру по параметру plugged.

## stage\objects\prediction_card.py — 
- def draw(c, p, t) 

## stage\objects\rack.py — Объект rack: серверная стойка из пяти блоков с мигающими индикаторами.
- def draw(c, p, t) Нарисовать стойку; lights задает долю активных блоков.

## stage\objects\room.py — Объект room: комната офиса в разрезе (окно, лампа, дверь, табличка).
- def _mx(a, b, k) Смешать цвета a и b на долю k.
- def draw(c, p, t) Нарисовать комнату; lights задает свет, door состояние двери.

## stage\objects\sum_node.py — 
- def draw(c, p, t) 

## stage\objects\tool_kit.py — Металлический чемоданчик с инструментами для обслуживания сервера
- def draw(c, p, t) 

## stage\objects\weight_box.py — 
- def draw(c, p, t) 

## stage\objects\wifi_signal.py — Доступ к облаку через интернет и качество связи
- def draw(c, p, t) 

## vg\__init__.py — 

## vg\__main__.py — 

## vg\audio.py — 
- def decode(path, sr) 
- def bell(sig, at, sr, base=880.0, gain=0.55, dur=0.9) 
- def music(total, starts, sr) 
- def mix(scenes, total, vdir, vid, st, mus) 
- def write_wav(path, x, sr) 
- def measure(path, lufs, tp) 
- def normalize(src, dst, st) 

## vg\caption.py — Субтитры: раскладка слов по строкам и отрисовка с подсветкой текущего слова.
- def layout(sc, st) Раскладка слов сцены на куски по 1-2 строки; для сцен stage ниже (cap.base_y_stage).
- def draw(fr, sc, t, st) Нарисовать субтитры сцены sc на кадре fr в момент t.

## vg\check.py — Проверка документа сцен до озвучки и рендера: правила rules.py, схемы иллюстраций и сцены stage.
- def load_doc(path) Прочитать JSON документа сцен; ошибки файла и JSON превращает в понятные исключения.
- def scenes_of(doc) Сцены документа с нормализованным цветом (кортеж) и ill_params по умолчанию.
- def limits_of(cfg) Лимиты (сцены, title, tag, слова) из конфига серии с запасными значениями из rules.py.
- def prompt_vars(lim) Лимиты в виде переменных для шаблонов промптов.
- def check_doc(doc, lim=None) Главная проверка документа: (ошибки, предупреждения); для stage вызывает stage.check_params с учетом continue и слов текста.

## vg\cli.py — 
- def pick(a) 
- def c_new(a) 
- def c_prompt(a) 
- def c_check(a) 
- def c_voice(a) 
- def c_stills(a) 
- def c_render(a) 
- def c_qa(a) 
- def c_pack(a) 
- def c_status(a) 
- def c_all(a) 
- def main() 

## vg\encode.py — 
- def encode(rd, audio, total, out, st) 
- def stills(rd, outdir) 

## vg\fonts.py — 
- def resolve(key) 
- def font(key, size) 

## vg\frames.py — Сборка кадра: фон, заголовок, иллюстрация (Cv) или сцена stage, субтитры.
- def make_bg(color, st) Фон сцены цвета color: градиент, свечения и точечная сетка.
- def title_layer(sc, idx, total, st) Слой заголовка сцены: точки прогресса, title и tag.
- class Renderer: __init__, at, _stage, frame

## vg\gfx.py — 
- def clamp(x, a=0.0, b=1.0) 
- def ease_out(x) 
- def smooth(x) 
- def mix(a, b, k) 
- def _mask(w, h, r) 
- class Cv: __init__, line, circle, rrect, poly, text, photo, out
- def arrow(cv, a, b, col, w=4, head=14) 
- def glow(cv, c, r, col, k=1.0) 

## vg\paths.py — 

## vg\pipeline.py — 
- def style_of(s) 
- def srt_time(x) 
- def write_texts(scenes, total, out) 
- def check(s, ids) 
- def voice(s, ids, force=False, only=None) 
- def prepare(s, vid, need_voice) 
- def stills(s, ids) 
- def render(s, ids) 
- def qa_all(s, ids) 
- def status(s) 

## vg\prompt.py — Сборка промптов для внешней LLM: план серии и сцены (обычный режим и mode=stage).
- def visible() Имена иллюстраций, видимых LLM (без служебных, например stage).
- def table() Markdown-таблица иллюстраций для вставки в промпт.
- def fill(text, extra=None) Подставить переменные {{NAME}} в шаблон промпта.
- def plan_prompt(s) Промпт плана серии.
- def scenes_prompt(s, vid) Промпт сцен одного ролика; при series.json mode=stage берется stage_scenes.md с манифестом объектов.

## vg\publish.py — 
- def pack(s) 

## vg\qa.py — 
- def probe(path) 
- def check_video(path, st, max_dur) 

## vg\rules.py — 

## vg\series.py — 
- class Sr: __init__, scenes_path, ids, pick, plan, mp4
- def new(name, count, lang, brief) 

## vg\style.py — 
- def merge(base, over, path='') 
- def ns(d) 
- def load_style(name='default', over=None) 

## vg\timeline.py — 
- def wav_dur(path) 
- def words_of(text) 
- def build(scenes, durs, st) 

## vg\ills\__init__.py — 

## vg\ills\charts.py — 
- def chk_graph(p) 
- def graph(cv, t, col, p) 
- def donut(cv, col, s, prog) 
- def chk_flow(p) 
- def flow(cv, t, col, p) 
- def icon(cv, c, kind, col) 
- def chk_timeline(p) 
- def timeline(cv, t, col, p) 
- def chk_tree(p) 
- def tree(cv, t, col, p) 
- def node(cv, c, text, col, hl=False, a=1.0, small=False) 
- def chk_compare(p) 
- def compare(cv, t, col, p) 
- def side(cv, box, col, d, prog, hl) 

## vg\ills\cnn.py — 
- def chk_cnn(p) 
- def pre(rows) 
- def cnn(cv, t, col, p) 

## vg\ills\gen.py — 
- def target() 
- def gen(cv, t, col, p) 

## vg\ills\intro.py — 
- def intro(cv, t, col, p) 

## vg\ills\net.py — 
- def weights(layers) 
- def chk_mlp(p) 
- def mlp(cv, t, col, p) 
- def chk_rnn(p) 
- def rnn(cv, t, col, p) 
- def attn(tokens) 
- def chk_trf(p) 
- def trf(cv, t, col, p) 
- def heat(cv, t, col, tokens, aw) 

## vg\ills\outro.py — 
- def outro(cv, t, col, p) 

## vg\ills\reg.py — 
- def reg(name, hint, check=None) 
- def canon(name) 
- def find(name) 
- def names() 

## vg\ills\stage.py — Положить как vg/ills/stage.py и добавить в vg/ills/__init__.py строку: from . import stage
- def _draw(cv, t, col, p) Заглушка: stage не рисуется через Cv.

## vg\ills\util.py — 
- def pidx(t, seq) 
- def chk_pulse(name, seq, lo, hi) 
- def chk_tokens(p, lo, hi, maxlen, default) 

## vg\voice\__init__.py — 
- def get_tts(name, **kw) 

## vg\voice\base.py — 
- class TTS: synth

## vg\voice\build.py — 
- def sig(cfg, text) 
- def trim(x, sr) 
- def write(path, x, sr) 
- def load_idx(vdir) 
- def save_idx(vdir, idx) 
- def stale(vdir, vid, scenes, cfg) 
- def build(vdir, vid, scenes, cfg, only=None, force=False) 

## vg\voice\silero.py — 
- def rate_name(r) 
- class SileroTTS: __init__, synth
