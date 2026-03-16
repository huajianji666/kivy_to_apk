# MyPlan - Fixed Data Persistence Version
# Fixed: KeyError 'start' by ensuring consistent data structure

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.config import Config
from datetime import datetime, date, timedelta
import json
import os

Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', '0')

Window.clearcolor = (0.98, 0.98, 0.98, 1)
Window.size = (400, 800)

PRIMARY_COLOR = (0.2, 0.6, 0.86, 1)
ACCENT_COLOR = (0.3, 0.7, 0.4, 1)
WARNING_COLOR = (0.9, 0.6, 0.2, 1)
TEXT_COLOR = (0.2, 0.2, 0.2, 1)
WHITE = (1, 1, 1, 1)

DATA_FILE = 'myplan_data.json'


class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = PRIMARY_COLOR
        self.color = WHITE
        self.font_size = '18sp'
        self.size_hint_y = None
        self.height = 55


class AnimatedDateDisplay(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 100
        self.padding = 15

        with self.canvas.before:
            Color(*PRIMARY_COLOR)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.date_label = Label(text='', font_size='28sp', bold=True, color=WHITE)
        self.weekday_label = Label(text='', font_size='14sp', color=(0.9, 0.95, 1, 1))

        self.add_widget(self.date_label)
        self.add_widget(self.weekday_label)
        self.opacity = 0

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def animate_in(self, direction='right'):
        offset = Window.width if direction == 'left' else -Window.width
        self.x = (Window.width - self.width) / 2 + offset * 0.3
        anim = Animation(opacity=1, x=(Window.width - self.width) / 2, duration=0.25, t='out_quad')
        anim.start(self)

    def animate_out(self, direction='left', callback=None):
        target_x = -Window.width if direction == 'left' else Window.width
        anim = Animation(opacity=0, x=target_x, duration=0.2, t='in_quad')
        if callback:
            anim.bind(on_complete=lambda *args: callback())
        anim.start(self)

    def set_date(self, date_obj):
        self.date_label.text = date_obj.strftime('%B %d, %Y')
        self.weekday_label.text = date_obj.strftime('%A')


class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=30)

        layout.add_widget(Label(text='MyPlan', font_size='48sp', size_hint=(1, 0.25), color=PRIMARY_COLOR, bold=True))
        layout.add_widget(
            Label(text='Made by Hua', font_size='16sp', size_hint=(1, 0.1), color=(0.5, 0.5, 0.5, 1)))

        btn_new = StyledButton(text='New Plan', size_hint=(1, 0.15))
        btn_new.bind(on_release=self.goto_new_plan)
        layout.add_widget(btn_new)

        btn_my = StyledButton(text='My Plans', size_hint=(1, 0.15), background_color=(0.4, 0.7, 0.9, 1))
        btn_my.bind(on_release=self.goto_my_plans)
        layout.add_widget(btn_my)

        btn_exit = StyledButton(text='Exit', size_hint=(1, 0.15), background_color=(0.8, 0.3, 0.3, 1))
        btn_exit.bind(on_release=self.exit_app)
        layout.add_widget(btn_exit)

        layout.add_widget(Label(size_hint=(1, 0.2)))

        self.add_widget(layout)

    def goto_new_plan(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'new_plan'

    def goto_my_plans(self, instance):
        my_plans_screen = self.manager.get_screen('my_plans')
        my_plans_screen.refresh_list()
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'my_plans'

    def exit_app(self, instance):
        App.get_running_app().stop()


class NewPlanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=15, padding=25)
        layout.add_widget(
            Label(text='Create New Plan', font_size='28sp', size_hint=(1, 0.12), color=PRIMARY_COLOR, bold=True))

        layout.add_widget(Label(text='Plan Name:', halign='left', font_size='16sp', size_hint=(1, 0.08)))
        self.name_input = TextInput(multiline=False, font_size='16sp', height=45, size_hint=(1, None))
        layout.add_widget(self.name_input)

        layout.add_widget(Label(text='Start Date (YYYY-MM-DD):', halign='left', font_size='16sp', size_hint=(1, 0.08)))
        self.start_input = TextInput(multiline=False, text=date.today().strftime('%Y-%m-%d'), font_size='16sp',
                                     height=45, size_hint=(1, None))
        layout.add_widget(self.start_input)

        layout.add_widget(Label(text='End Date (YYYY-MM-DD):', halign='left', font_size='16sp', size_hint=(1, 0.08)))
        self.end_input = TextInput(multiline=False, text=(date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
                                   font_size='16sp', height=45, size_hint=(1, None))
        layout.add_widget(self.end_input)

        layout.add_widget(Label(size_hint=(1, 0.1)))

        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        btn_create = StyledButton(text='Create Plan')
        btn_create.bind(on_release=self.create_plan)
        btn_back = StyledButton(text='Back', background_color=(0.5, 0.5, 0.5, 1))
        btn_back.bind(on_release=self.back_to_main)
        btn_layout.add_widget(btn_create)
        btn_layout.add_widget(btn_back)

        layout.add_widget(btn_layout)
        self.add_widget(layout)

    def create_plan(self, instance):
        name = self.name_input.text.strip()
        start_str = self.start_input.text.strip()
        end_str = self.end_input.text.strip()

        if not name or not start_str or not end_str:
            self.show_error('Please fill all fields')
            return

        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            self.show_error('Invalid date format. Use YYYY-MM-DD')
            return

        if start_date > end_date:
            self.show_error('Start date must be before end date')
            return

        app = App.get_running_app()

        # CRITICAL FIX: Store dates as ISO strings immediately for consistency
        new_plan = {
            'name': name,
            'start': start_date.isoformat(),  # Always store as string
            'end': end_date.isoformat(),  # Always store as string
            'notes': {}
        }
        app.plans.append(new_plan)
        app.save_plans()

        self.name_input.text = ''
        self.start_input.text = date.today().strftime('%Y-%m-%d')
        self.end_input.text = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')

        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

    def back_to_main(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

    def show_error(self, msg):
        popup = Popup(title='Error', content=Label(text=msg, font_size='16sp'), size_hint=(0.8, 0.3))
        popup.open()


class MyPlansScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text='My Plans', font_size='28sp', size_hint=(1, 0.1), color=PRIMARY_COLOR, bold=True))

        self.list_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        scroll_view = ScrollView(size_hint=(1, 0.75))
        scroll_view.add_widget(self.list_layout)
        layout.add_widget(scroll_view)

        btn_back = StyledButton(text='Back', size_hint=(1, 0.1), background_color=(0.5, 0.5, 0.5, 1))
        btn_back.bind(on_release=self.back_to_main)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def refresh_list(self):
        self.list_layout.clear_widgets()
        app = App.get_running_app()

        # Reload from file to ensure fresh data
        app.load_plans()

        if not app.plans:
            self.list_layout.add_widget(
                Label(text='No plans yet.\nCreate one!', size_hint_y=None, height=100, font_size='16sp',
                      color=(0.5, 0.5, 0.5, 1)))
            return

        for idx, plan in enumerate(app.plans):
            # CRITICAL FIX: Safely get values with defaults
            name = plan.get('name', 'Unnamed Plan')
            start = plan.get('start', '')
            end = plan.get('end', '')

            # Format display string
            display_text = f"[b]{name}[/b]\n[size=12sp]{start} to {end}[/size]"

            btn = Button(
                text=display_text,
                size_hint_y=None,
                height=80,
                halign='center',
                valign='middle',
                background_color=(0.95, 0.95, 0.95, 1),
                color=TEXT_COLOR,
                font_size='16sp',
                markup=True
            )
            btn.plan_index = idx
            btn.bind(on_release=self.open_plan_calendar)
            self.list_layout.add_widget(btn)

    def open_plan_calendar(self, instance):
        cal_screen = self.manager.get_screen('plan_calendar')
        cal_screen.set_plan(instance.plan_index, date.today())
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'plan_calendar'

    def back_to_main(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'


class PlanCalendarScreen(Screen):
    plan_index = ObjectProperty(None)
    current_date = ObjectProperty(None)
    start_date = ObjectProperty(None)
    end_date = ObjectProperty(None)
    is_animating = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_date = date.today()
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        header = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.plan_name_label = Label(text='', font_size='18sp', bold=True, color=PRIMARY_COLOR, halign='left')

        btn_back = Button(
            text='Back',
            size_hint_x=None,
            width=70,
            background_color=(0.5, 0.5, 0.5, 1),
            color=WHITE,
            background_normal='',
            font_size='14sp',
            on_release=self.back_to_plans
        )

        header.add_widget(btn_back)
        header.add_widget(self.plan_name_label)

        self.date_display = AnimatedDateDisplay()

        self.range_label = Label(
            text='',
            font_size='11sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=20
        )

        nav_box = BoxLayout(size_hint_y=None, height=35, spacing=10)
        self.left_arrow = Label(text='◀ Prev', font_size='13sp', color=PRIMARY_COLOR)
        self.right_arrow = Label(text='Next ▶', font_size='13sp', color=PRIMARY_COLOR)
        nav_box.add_widget(self.left_arrow)
        nav_box.add_widget(self.right_arrow)

        note_container = BoxLayout(orientation='vertical', padding=15, size_hint_y=0.5)
        with note_container.canvas.before:
            Color(1, 1, 1, 1)
            self.note_bg = RoundedRectangle(pos=note_container.pos, size=note_container.size, radius=[12])
            Color(*PRIMARY_COLOR[:3], 0.3)
            self.note_border = Line(
                rounded_rectangle=(note_container.x, note_container.y, note_container.width, note_container.height, 12),
                width=1)
        note_container.bind(pos=self.update_note_bg, size=self.update_note_bg)

        note_header = BoxLayout(size_hint_y=None, height=35, spacing=10)
        note_title = Label(text="Today's Mark:", font_size='16sp', bold=True, color=PRIMARY_COLOR, halign='left')

        note_header.add_widget(note_title)

        self.note_button = Button(
            text='Tap to add note',
            font_size='16sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='center',
            valign='middle',
            background_color=(0.98, 0.98, 0.98, 1),
            background_normal='',
            size_hint_y=1,
            on_release=self.edit_note_popup
        )

        note_container.add_widget(note_header)
        note_container.add_widget(self.note_button)

        edit_btn_main = StyledButton(
            text='Edit Mark',
            on_release=self.edit_note_popup,
            size_hint_y=None,
            height=50,
            background_color=ACCENT_COLOR
        )

        swipe_hint = Label(
            text='← swipe to change day →',
            font_size='12sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=25
        )

        main_layout.add_widget(header)
        main_layout.add_widget(self.date_display)
        main_layout.add_widget(self.range_label)
        main_layout.add_widget(nav_box)
        main_layout.add_widget(note_container)
        main_layout.add_widget(edit_btn_main)
        main_layout.add_widget(swipe_hint)

        self.touch_layer = FloatLayout()
        self.touch_layer.add_widget(main_layout)
        self.add_widget(self.touch_layer)

        self.touch_start_x = None
        self.touch_start_y = None

    def update_note_bg(self, instance, value):
        self.note_bg.pos = instance.pos
        self.note_bg.size = instance.size
        self.note_border.rounded_rectangle = (instance.x, instance.y, instance.width, instance.height, 12)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True

        for child in self.walk():
            if isinstance(child, Button) and child.collide_point(*touch.pos):
                return False

        self.touch_start_x = touch.x
        self.touch_start_y = touch.y
        return False

    def on_touch_up(self, touch):
        if super().on_touch_up(touch):
            return True

        if self.is_animating or self.touch_start_x is None:
            return False

        for child in self.walk():
            if isinstance(child, Button) and child.collide_point(*touch.pos):
                self.touch_start_x = None
                return False

        diff_x = touch.x - self.touch_start_x
        diff_y = abs(touch.y - self.touch_start_y)

        if abs(diff_x) > 60 and diff_y < 100:
            if diff_x > 0:
                self.animate_transition('right', self.previous_day)
            else:
                self.animate_transition('left', self.next_day)
            self.touch_start_x = None
            return True

        self.touch_start_x = None
        return False

    def animate_transition(self, direction, callback):
        if self.is_animating:
            return
        self.is_animating = True

        exit_dir = direction

        self.date_display.animate_out(exit_dir, lambda: self.finish_transition(direction, callback))
        anim = Animation(opacity=0, duration=0.15)
        anim.start(self.note_button)

    def finish_transition(self, direction, callback):
        callback()
        enter_dir = 'right' if direction == 'left' else 'left'
        self.date_display.animate_in(enter_dir)
        self.note_button.opacity = 0
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self.note_button)
        Clock.schedule_once(lambda dt: setattr(self, 'is_animating', False), 0.3)

    def set_plan(self, plan_index, initial_date):
        self.plan_index = plan_index
        app = App.get_running_app()

        # CRITICAL FIX: Check bounds and data validity
        if self.plan_index is None or self.plan_index >= len(app.plans):
            print(f"Error: Invalid plan index {self.plan_index}")
            return

        plan = app.plans[self.plan_index]
        print(f"Loading plan: {plan}")  # Debug output

        # Safely get start and end dates
        start_val = plan.get('start', '')
        end_val = plan.get('end', '')

        if not start_val or not end_val:
            print(f"Error: Plan missing dates - start:{start_val}, end:{end_val}")
            return

        # Parse dates from string
        try:
            if isinstance(start_val, str):
                self.start_date = date.fromisoformat(start_val)
                self.end_date = date.fromisoformat(end_val)
            else:
                self.start_date = start_val
                self.end_date = end_val
        except Exception as e:
            print(f"Error parsing dates: {e}")
            return

        if self.start_date <= initial_date <= self.end_date:
            self.current_date = initial_date
        else:
            self.current_date = self.start_date

        self.plan_name_label.text = plan.get('name', 'Unnamed')
        self.update_display()
        Clock.schedule_once(lambda dt: self.date_display.animate_in('right'), 0)

    def update_display(self):
        self.date_display.set_date(self.current_date)
        self.range_label.text = f"{self.start_date} to {self.end_date}"
        self.update_navigation_arrows()

        date_str = self.current_date.strftime('%Y-%m-%d')
        app = App.get_running_app()

        # CRITICAL FIX: Check plan exists
        if self.plan_index >= len(app.plans):
            return

        plan = app.plans[self.plan_index]
        notes = plan.get('notes', {})
        note = notes.get(date_str, '')

        if note:
            self.note_button.text = note
            self.note_button.color = TEXT_COLOR
        else:
            self.note_button.text = 'Tap to add note'
            self.note_button.color = (0.5, 0.5, 0.5, 1)

    def update_navigation_arrows(self):
        prev_date = self.current_date - timedelta(days=1)
        if prev_date >= self.start_date:
            self.left_arrow.opacity = 1
            self.left_arrow.color = PRIMARY_COLOR
        else:
            self.left_arrow.opacity = 0.3
            self.left_arrow.color = (0.5, 0.5, 0.5, 1)

        next_date = self.current_date + timedelta(days=1)
        if next_date <= self.end_date:
            self.right_arrow.opacity = 1
            self.right_arrow.color = PRIMARY_COLOR
        else:
            self.right_arrow.opacity = 0.3
            self.right_arrow.color = (0.5, 0.5, 0.5, 1)

    def next_day(self):
        next_date = self.current_date + timedelta(days=1)
        if next_date <= self.end_date:
            self.current_date = next_date
            self.update_display()
        else:
            self.show_boundary_warning('End of plan reached!')

    def previous_day(self):
        prev_date = self.current_date - timedelta(days=1)
        if prev_date >= self.start_date:
            self.current_date = prev_date
            self.update_display()
        else:
            self.show_boundary_warning('Start of plan reached!')

    def show_boundary_warning(self, message):
        popup = Popup(
            title='',
            size_hint=(0.8, 0.18),
            background_color=WHITE,
            separator_color=(0, 0, 0, 0)
        )
        content = BoxLayout(orientation='vertical', padding=15)
        content.add_widget(Label(text=message, color=WARNING_COLOR, font_size='15sp', bold=True))
        popup.content = content
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.2)

    def edit_note_popup(self, instance=None):
        if self.plan_index is None:
            return

        app = App.get_running_app()
        if self.plan_index >= len(app.plans):
            return

        plan = app.plans[self.plan_index]
        date_str = self.current_date.strftime('%Y-%m-%d')
        notes = plan.get('notes', {})
        current_note = notes.get(date_str, '')

        content = BoxLayout(orientation='vertical', spacing=10, padding=15)

        header = Label(
            text=f'Edit: {date_str}',
            font_size='18sp',
            bold=True,
            color=PRIMARY_COLOR,
            size_hint_y=None,
            height=30
        )

        text_input = TextInput(
            text=current_note,
            hint_text='Enter your daily mark...',
            multiline=True,
            font_size='16sp',
            background_color=WHITE,
            foreground_color=TEXT_COLOR,
            padding=[10, 10],
            size_hint_y=0.7
        )

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.5),
            background_color=WHITE,
            separator_color=(0, 0, 0, 0)
        )

        def save_note(instance):
            new_note = text_input.text.strip()

            # Get or create notes dict
            if 'notes' not in plan:
                plan['notes'] = {}

            if new_note:
                plan['notes'][date_str] = new_note
            else:
                if date_str in plan['notes']:
                    del plan['notes'][date_str]

            app.save_plans()
            self.update_display()
            popup.dismiss()

        btn_save = StyledButton(text='Save', on_release=save_note)
        btn_cancel = StyledButton(text='Cancel', on_release=popup.dismiss, background_color=(0.5, 0.5, 0.5, 1))

        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_cancel)

        content.add_widget(header)
        content.add_widget(text_input)
        content.add_widget(btn_layout)

        popup.open()
        Clock.schedule_once(lambda dt: setattr(text_input, 'focus', True), 0.1)

    def back_to_plans(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'my_plans'


class MyPlanApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plans = []

    def build(self):
        self.load_plans()

        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main'))
        sm.add_widget(NewPlanScreen(name='new_plan'))
        sm.add_widget(MyPlansScreen(name='my_plans'))
        sm.add_widget(PlanCalendarScreen(name='plan_calendar'))
        return sm

    def load_plans(self):
        """Load plans from JSON file with error handling"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)

                # CRITICAL FIX: Validate loaded data structure
                valid_plans = []
                for item in loaded_data:
                    if isinstance(item, dict) and 'name' in item and 'start' in item and 'end' in item:
                        # Ensure notes exists
                        if 'notes' not in item:
                            item['notes'] = {}
                        valid_plans.append(item)
                    else:
                        print(f"Skipping invalid plan data: {item}")

                self.plans = valid_plans
                print(f"Successfully loaded {len(self.plans)} plans from {DATA_FILE}")

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                self.plans = []
            except Exception as e:
                print(f"Error loading plans: {e}")
                self.plans = []
        else:
            self.plans = []
            print("No existing data file found, starting fresh")

    def save_plans(self):
        """Save plans to JSON file immediately"""
        try:
            # CRITICAL FIX: Ensure all plans have required fields before saving
            valid_plans = []
            for plan in self.plans:
                if isinstance(plan, dict) and 'name' in plan:
                    # Ensure all required keys exist
                    valid_plan = {
                        'name': plan.get('name', 'Unnamed'),
                        'start': plan.get('start', date.today().isoformat()),
                        'end': plan.get('end', date.today().isoformat()),
                        'notes': plan.get('notes', {})
                    }
                    valid_plans.append(valid_plan)

            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(valid_plans, f, indent=2, ensure_ascii=False)

            self.plans = valid_plans  # Update with cleaned data
            print(f"Saved {len(valid_plans)} plans to {DATA_FILE}")

        except Exception as e:
            print(f"Error saving plans: {e}")


if __name__ == '__main__':
    MyPlanApp().run()
