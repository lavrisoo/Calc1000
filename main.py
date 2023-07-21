import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang import Builder
import csv
import datetime
from collections import Counter

Window.size = (375, 667)
Config.set('kivy', 'keybord_mode', 'systemanddock')

Builder.load_string(
"""
<BoxLayout>:
    canvas:
        Color:
            rgba: [255, 255, 255, 1]
        Rectangle:
            pos: self.pos
            size: self.size
<TextInput>:
    font_size: 25
    color: [0.2, 0.2, 0.2, 1]
<Label>:
    font_size: 18
    color: [0.2, 0.2, 0.2, 1]
    canvas:
        Color:
            rgba: [0.6, 0.6, 0.6, 0.1]
        Rectangle:
            pos: self.pos
            size: self.size
<Button>:
    canvas:
        Color: 
            rgba: [0.6, 0.6, 0.6, 0.3]
    color: [1, 1, 1, 1]
<ScrollView>:
    bar_color: [.7, .7, .7, .9]
    bar_width: 12        
""")

class Gaming:
    data = [[0], [0], [0]]
    id = datetime.datetime.now()
    g = ['player1', 'player2', 'player3']
    round = 0
    bolt = [0, 0, 0]
    bochka_count = [0, [0, 0, 0]]
    end_game = 0

    def __init__(self):
        self.data_old = None

    def old_game(self):
        with open('game.csv', 'r', encoding='utf-8', newline='') as file:
            f = csv.reader(file, delimiter=';')
            self.data_old = [i for i in f]
            file.close()
            return [self.data_old[i] for i in range(0, len(self.data_old)) if i % 4 == 0]

    def save(self):
        data_buf = [datetime.datetime.now(), '^'.join(self.g), self.round, '^'.join([str(i) for i in self.bolt]),
                    '^'.join([str(self.bochka_count[0]), '^'.join([str(i) for i in self.bochka_count[1]])]), self.end_game]

        with open('game.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(data_buf)
            for i in range(0, 3):
                writer.writerow(self.data[i])
            file.close()

    def autosave(self):
        with open('game.csv', 'r', encoding='utf-8', newline='') as file:
            f = csv.reader(file, delimiter=';')
            f = list(f)[:-4]
            file.close()
        with open('game.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for i in range(0, int(len(f) / 4), 4):
                writer.writerow(f[i])
                for j in range(1, 4):
                    writer.writerow(f[i+j])
            file.close()
        self.save()


game = Gaming()

class StartForm(BoxLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(text='1000', font_size=25)
        self.player1 = TextInput(hint_text='player1', multiline=False)
        self.player2 = TextInput(hint_text='player2', multiline=False)
        self.player3 = TextInput(hint_text='player3', multiline=False)
        self.but_new = Button(text='Новая игра', on_release=self.new_game)
        self.but_old = Button(text='Архив', on_release=self.old_game)

        box = BoxLayout(orientation='vertical', padding=30, spacing=30)
        box.add_widget(self.label)
        box.add_widget(self.player1)
        box.add_widget(self.player2)
        box.add_widget(self.player3)
        box.add_widget(self.but_new)
        box.add_widget(self.but_old)

        self.add_widget(box)

    def build(self, **kwargs):
        pass

    def new_game(self, *args):
        self.manager.transition.direction = 'left'
        self.manager.current = 'gameform'
        self.manager.get_screen('gameform').update_label(self.player1.text, self.player2.text, self.player3.text)

    def old_game(self, *args):
        self.manager.transition.direction = 'left'
        self.manager.current = 'oldgamesform'
        self.manager.get_screen('oldgamesform').reset_list()


def valid(n):
    n = 0 if n == '' else int(n)
    n = 300 if n > 300 else n
    if n % 5 != 0:
        n = (n // 5) * 5 + 5 if n % 5 >= 3 else (n // 5) * 5
    return n

def bochka(i):
    count_b = Counter(game.data[i])[880]
    if count_b == 1:
        return 760
    elif count_b == 2:
        return 500
    else:
        return 0

def normal_game(i, n):
    if n == 0:
        game.bolt[i] += 1
        if game.bolt[i] % 3 == 0:
            game.data[i].append(int(game.data[i][-1]) - 120)
        else:
            game.data[i].append(n + int(game.data[i][-1]))
    else:
        if n + int(game.data[i][-1]) >= 880:
            game.data[i].append(880)
            game.bochka_count[0] = game.round
            game.bochka_count[1][i] = 1
        else:
            game.data[i].append(n + int(game.data[i][-1]))

def bochka_game(txt):
        b = game.bochka_count[1].index(1)
        if valid(txt[b].text) == 0:
            game.data[b].append(bochka(b))
            for i in range(0, 3):
                if i != b:
                    game.data[i].append(int(game.data[i][-1]))
        elif valid(txt[b].text) < 120:
            game.data[b].append(bochka(b))
            for i in range(0, 3):
                if i != b:
                    normal_game(i, valid(txt[i].text))
        else:
            game.data[b].append(1000)
            for i in range(0, 3):
                if i != b:
                    normal_game(i, valid(txt[i].text))
            game.end_game = 1


class GameForm(BoxLayout, Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.scroll = ScrollView(size_hint=[1, 0.8])
        self.boxlayout = BoxLayout(orientation="vertical", spacing=15, padding=[20])
        self.gr_title = GridLayout(cols=3, size_hint=[1, 0.1])
        self.gr = GridLayout(cols=3, spacing=10, size_hint_y=None, height=self.minimum_height)
        self.gr.bind(minimum_height=self.gr.setter('height'))
        self.gr_but = GridLayout(cols=3, size_hint=[1, 0.1])
        self.gr_input = GridLayout(cols=3, size_hint=[1, 0.15])
        self.lb = []

        self.popup_del = Popup(title='Отменить последний ход?', size_hint=(None, None), size=(300, 200))
        self.popup_del.add_widget(Button(text='Да', padding=[40], on_press=self._del_round))

        self.popup_save = Popup(title='Игра сохранена!', size_hint=(None, None), size=(200, 100))

        self.popup_new = Popup(title='Не забыли сохраниться?', size_hint=(None, None), size=(300, 200))
        self.popup_new.add_widget(Button(text='Да', padding=[40], on_press=self._return_main))

        self.gr_but.add_widget(Button(text='Отменить', size_hint=[1, 1], on_press=self.popup_del.open))
        self.gr_but.add_widget(Button(text='Сохранить', size_hint=[1, 1], on_press=self._save))
        self.gr_but.add_widget(Button(text='На главный', size_hint=[1, 1], on_press=self.popup_new.open))

        for i in range(0, 3):
            self.lb.append(Label(text=str(game.g[i]), size_hint_y=0.15, font_size=20, padding=[0, 0, 0, 5]))
            self.gr_title.add_widget(self.lb[i])
        for i in range(3, 6):
            self.lb.append(Label(text=str(game.bolt[i-3]), size_hint_y=0.15, font_size=15, padding=[0, 15, 0, 5]))
            self.gr_title.add_widget(self.lb[i])
        self.lb[game.round % 3].color = 'darkgreen'

        self.txt = [TextInput(), TextInput(), TextInput()]
        for i in range(0, 3):
            self.txt[i] = TextInput(multiline=False, hint_text='0', input_type='number', input_filter='int')
            self.gr_input.add_widget(self.txt[i])

        self.boxlayout.add_widget(self.gr_but)
        self.boxlayout.add_widget(self.gr_title)
        self.scroll.add_widget(self.gr)
        self.boxlayout.add_widget(self.scroll)
        self.boxlayout.add_widget(self.gr_input)
        self.but_add = Button(text='Добавить', size_hint=[1, .15], on_press=self._new_round)
        self.boxlayout.add_widget(self.but_add)
        self.add_widget(self.boxlayout)

    def update_label(self, n1, n2, n3):
        n1, n2, n3 = str(n1 if n1 != '' else 'player1'), str(n2 if n2 != '' else 'player2'), str(n3 if n3 != '' else 'player3')
        game.g[0], game.g[1], game.g[2] = n1, n2, n3
        self.lb[0].text, self.lb[1].text, self.lb[2].text = n1, n2, n3

    def _del_round(self, *args):
        try:
            game.round -= 1
            for i in range(0, 3):
                if game.data[i][-1] == game.data[i][-2]:
                    game.bolt[i] -= 1
                    self.lb[3 + i].text = str(game.bolt[i])
                if game.data[i][-1] == 1000:
                    game.end_game = 0
                    game.bochka_count[0] = 1
                    game.bochka_count[1][i] = 1
                    self.but_disabled()
                game.data[i].pop(-1)
                self.gr.remove_widget(self.gr.children[0])
                self.lb[i].color = 'darkgreen' if game.round % 3 - i % 3 == 0 else [0.2, 0.2, 0.2, 1]
        except: pass
        self.popup_del.dismiss()

    def but_disabled(self):
            self.but_add.disabled = True if game.end_game == 1 else False

    def _return_main(self, *args):
        self.manager.transition.direction = 'right'
        game.data = [[0], [0], [0]]
        game.id = datetime.datetime.now()
        game.g = ['player1', 'player2', 'player3']
        game.round = 0
        game.bolt = [0, 0, 0]
        game.bochka_count = [0, [0, 0, 0]]
        game.end_game = 0
        self.gr.clear_widgets()
        self.manager.get_screen('gameform').old_game()
        self.manager.current = 'startform'
        self.popup_new.dismiss()

    def _new_round(self, instance, *args):
        game.round += 1

        if (sum(game.bochka_count[1]) > 0 and game.bochka_count[0] == game.round) or sum(game.bochka_count[1]) == 0:
            for i in range(0, 3):
                n = valid(self.txt[i].text)
                normal_game(i, n)
        elif sum(game.bochka_count[1]) == 1 and game.bochka_count[0] != game.round:
            bochka_game(self.txt)
            game.bochka_count = [0, [0, 0, 0]]

        for i in range(0, 3):
            if game.data[i][-1] == 880:
                l = Label(text=str(game.data[i][-1]), color='darkred', size_hint_y=None)
            else:
                l = Label(text=str(game.data[i][-1]), size_hint_y=None)
            l.bind(texture_size=l.setter('size'))
            self.gr.add_widget(l)
            self.lb[3 + i].text = str(game.bolt[i])
            self.txt[i].hint_text = '0'
            self.txt[i].text = ''
            self.lb[i].color = 'darkgreen' if game.round % 3 - i % 3 == 0 else [0.2, 0.2, 0.2, 1]

        if sum(game.bochka_count[1]) > 1:
            game.bochka_count = [0, [0, 0, 0]]
            for i in range(0, 3):
                if game.data[i][-1] == 880:
                    game.data[i].append(bochka(i))
                else:
                    game.data[i].append(game.data[i][-1])
                l = Label(text=str(game.data[i][-1]), height=10, size_hint_y=None)
                l.bind(texture_size=l.setter('size'))
                self.gr.add_widget(l)

        self.but_disabled()

    def old_game(self, *args):
        self.lb[0].text, self.lb[1].text, self.lb[2].text = game.g[0], game.g[1], game.g[2]
        self.lb[3].text, self.lb[4].text, self.lb[5].text = str(game.bolt[0]), str(game.bolt[1]), str(game.bolt[2])
        for i in range(0, len(game.data[0])):
            for j in range(0, 3):
                if game.data[j][i] == 880:
                    l = Label(text=str(game.data[j][i]), color='darkred', size_hint_y=None)
                else:
                    l = Label(text=str(game.data[j][i]), size_hint_y=None)
                l.bind(texture_size=l.setter('size'))
                self.gr.add_widget(l)
        self.but_disabled()

    def _save(self, *args):
        game.save()
        self.popup_save.open()

gameform = GameForm()

class OldGamesForm(BoxLayout, Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        data = game.old_game()

        self.boxlayout = BoxLayout(orientation="vertical", spacing=10, padding=[20])
        self.scroll = ScrollView(size_hint=[1, 0.9])
        self.gr = GridLayout(cols=1, size_hint_y=None, height=self.minimum_height, row_default_height=50)
        self.gr.bind(minimum_height=self.gr.setter('height'))

        for i in data[::-1]:
            self.gr.add_widget(Button(text=str(i[0]), on_press=self._return_old_game))

        self.popup_del = Popup(title='Удалить историю?', size_hint=(None, None), size=(300, 200))
        self.popup_del.add_widget(Button(text='Да', padding=[40], on_press=self._del_history))

        self.scroll.add_widget(self.gr)
        self.boxlayout.add_widget(self.scroll)
        self.boxlayout.add_widget(Button(text='Удалить историю', size_hint=[1, 0.1], on_press=self.popup_del.open))
        self.boxlayout.add_widget(Button(text='На главный', size_hint=[1, 0.1], on_press=self._return_main2))
        self.add_widget(self.boxlayout)

    def reset_list(self):
        self.gr.clear_widgets()
        data = game.old_game()
        for i in data[::-1]:
            self.gr.add_widget(Button(text=str(i[0]), on_press=self._return_old_game))

    def _del_history(self, *args):
        with open('game.csv', 'w', encoding='utf-8', newline='') as file:
            file.close()
        self.reset_list()
        self.popup_del.dismiss()

    def _return_old_game(self, instance, *args):
        t = instance.text
        with open('game.csv', 'r', encoding='utf-8', newline='') as file:
            f = list(csv.reader(file, delimiter=';'))
            for i in range(len(f)):
                if f[i][0] == t:
                    game.id = f[i][0]
                    game.g = f[i][1].split('^')
                    game.round = int(f[i][2])
                    game.bolt = [int(j) for j in f[i][3].split('^')]
                    game.bochka_count = [int(f[i][4].split('^')[0]), [int(j) for j in f[i][4].split('^')[1:]]]
                    game.end_game = int(f[i][5])
                    game.data = [[int(i) for i in f[i+1]], [int(i) for i in f[i+2]], [int(i) for i in f[i+3]]]
                    break

        self.manager.transition.direction = 'right'
        self.manager.get_screen('gameform').old_game()
        self.manager.current = 'gameform'

    def _return_main2(self, *args):
        self.manager.transition.direction = 'right'
        self.manager.current = 'startform'


class ScreenManagement(ScreenManager):
    pass
form = ScreenManagement()


class MyApp(App):
    def build(self):
        form.add_widget(StartForm(name='startform'))
        form.add_widget(GameForm(name='gameform'))
        form.add_widget(OldGamesForm(name='oldgamesform'))
        return form


if __name__ == '__main__':
    MyApp().run()





















