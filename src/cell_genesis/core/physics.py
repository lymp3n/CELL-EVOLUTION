import arcade
import math
import random

SCREEN_WIDTH = 1000  # Ширина игрового окна
SCREEN_HEIGHT = 700  # Высота игрового окна
PLAYER_RADIUS = 20  # Радиус игрока
SLOW_ZONE_COUNT = 15  # Количество замедляющих зон
SLOW_ZONE_RADIUS = 60  # Радиус замедляющей зоны


# Класс игрока
class Player:
    def __init__(self):  # Конструктор класса
        # Позиция игрока в мировых координатах
        self.center_x = 0  # Координата X центра игрока
        self.center_y = 0  # Координата Y центра игрока
        self.radius = PLAYER_RADIUS  # Радиус для отрисовки и коллизий
        self.color = arcade.color.RED  # Цвет игрока

        # Физические параметры движения
        self.velocity_x = 0.0  # Текущая скорость по оси X
        self.velocity_y = 0.0  # Текущая скорость по оси Y
        self.friction = 0.92  # Коэффициент трения (0.92 = 8% замедления)

        # Параметры для плавного движения
        self.target_velocity_x = 0.0  # Целевая скорость по X (от ввода)
        self.target_velocity_y = 0.0  # Целевая скорость по Y (от ввода)
        self.acceleration_rate = 0.2  # Скорость разгона к целевой скорости
        self.deceleration_rate = 0.3  # Скорость замедления при отпускании клавиш
        self.current_max_speed = 0.0  # Текущий лимит скорости (меняется плавно)

        # Система энергии
        self.energy = 100.0  # Текущий запас энергии
        self.max_energy = 100.0  # Максимальный запас энергии
        self.in_slow_zone = False  # Флаг нахождения в замедляющей зоне
        self.energy_consumption = 0.005  # Расход энергии за единицу скорости

        # Уровни скорости в зависимости от энергии
        # Формат: (минимальная энергия, максимальная энергия, скорость)
        self.energy_speed_levels = [
            (80, 100, 10),  # 80-100% энергии = скорость 10
            (60, 80, 8),  # 60-80% энергии = скорость 8
            (40, 60, 6),  # 40-60% энергии = скорость 6
            (20, 40, 4),  # 20-40% энергии = скорость 4
            (1, 20, 2),  # 1-20% энергии = скорость 2
            (0, 1, 1)  # 0-1% энергии = скорость 1
        ]

        self.update_speed()  # Инициализация скорости на основе стартовой энергии

    def update_speed(self):
        """Обновляет максимальную скорость в зависимости от энергии"""
        # Перебираем все уровни энергии
        for min_e, max_e, speed in self.energy_speed_levels:
            # Если текущая энергия попадает в диапазон
            if min_e <= self.energy < max_e:
                self.base_speed = speed  # Устанавливаем базовую скорость
                break  # Выходим из цикла при первом совпадении
        else:  # Выполняется, если цикл завершился без break
            self.base_speed = 1  # Значение по умолчанию

        # Учитываем замедление от зоны
        # Если в зоне - уменьшаем скорость на 2, но не меньше 1
        self.target_max_speed = max(self.base_speed - (2 if self.in_slow_zone else 0), 1)

    def handle_input(self, pressed_keys):
        """Обработка ввода с клавиатуры"""
        # Словарь сопоставления клавиш и направлений движения
        # Ключ: код клавиши, Значение: (изменение по X, изменение по Y)
        direction_map = {
            arcade.key.W: (0, 1),  # W - движение вверх
            arcade.key.S: (0, -1),  # S - движение вниз
            arcade.key.A: (-1, 0),  # A - движение влево
            arcade.key.D: (1, 0),  # D - движение вправо
            arcade.key.UP: (0, 1),  # Стрелка вверх
            arcade.key.DOWN: (0, -1),  # Стрелка вниз
            arcade.key.LEFT: (-1, 0),  # Стрелка влево
            arcade.key.RIGHT: (1, 0)  # Стрелка вправо
        }

        # Сбрасываем целевые скорости перед расчетом
        self.target_velocity_x = 0.0
        self.target_velocity_y = 0.0

        # Для каждой нажатой клавиши из множества pressed_keys
        for key in pressed_keys:
            if key in direction_map:  # Если клавиша есть в нашем словаре
                dx, dy = direction_map[key]  # Получаем направление движения
                # Добавляем компоненты скорости с учетом текущего максимума
                self.target_velocity_x += dx * self.current_max_speed
                self.target_velocity_y += dy * self.current_max_speed

    def update(self):
        """Обновление физики движения (вызывается каждый кадр)"""
        # 1. Обновляем максимальную скорость на основе энергии
        self.update_speed()

        # 2. Плавно меняем текущий максимум скорости к целевому
        if self.current_max_speed < self.target_max_speed:
            # Увеличиваем скорость до целевой с учетом ускорения
            self.current_max_speed = min(self.current_max_speed + self.acceleration_rate, self.target_max_speed)
        elif self.current_max_speed > self.target_max_speed:
            # Уменьшаем скорость до целевой с учетом замедления
            self.current_max_speed = max(self.current_max_speed - self.deceleration_rate, self.target_max_speed)

        # 3. Обновление скоростей по осям X и Y
        for axis in ('x', 'y'):  # Обрабатываем обе оси в цикле
            current = getattr(self, f'velocity_{axis}')  # Текущая скорость по оси
            target = getattr(self, f'target_velocity_{axis}')  # Целевая скорость по оси
            # Выбираем коэффициент: ускорение или замедление
            rate = self.acceleration_rate if target != 0 else self.deceleration_rate

            # Если разница значительная, плавно меняем скорость
            if abs(current - target) > 0.1:
                # Линейная интерполяция к целевой скорости
                new_speed = current + (target - current) * rate
                setattr(self, f'velocity_{axis}', new_speed)

        # 4. Применяем трение, если нет активного ввода
        if self.target_velocity_x == 0 and self.target_velocity_y == 0:
            self.velocity_x *= self.friction  # Замедляем по X
            self.velocity_y *= self.friction  # Замедляем по Y

        # 5. Ограничиваем общую скорость текущим максимумом
        # Вычисляем фактическую скорость (теорема Пифагора)
        speed = math.hypot(self.velocity_x, self.velocity_y)
        if speed > self.current_max_speed:  # Если превысили лимит
            scale = self.current_max_speed / speed  # Коэффициент масштабирования
            self.velocity_x *= scale  # Уменьшаем X компоненту
            self.velocity_y *= scale  # Уменьшаем Y компоненту

        # 6. Система энергии
        if speed > 0.1:  # Если двигаемся со значительной скоростью
            # Расходуем энергию пропорционально скорости
            self.energy = max(0, self.energy - speed * self.energy_consumption)
        elif self.energy < self.max_energy:  # Если стоим и энергия не полная
            # Пассивное восстановление энергии
            '''это заглушка по востановлению энергии надо будет тут или где то написать условие что бы при 
            поглощении еды к self.energy прибовлялось n кол-во очков '''
            self.energy = min(self.max_energy, self.energy + 0.2)

        # 7. Обновление позиции на основе скорости
        self.center_x += self.velocity_x
        self.center_y += self.velocity_y

    def draw(self):
        """Отрисовка игрока (всегда в центре экрана)"""
        arcade.draw_circle_filled(
            SCREEN_WIDTH // 2,  # Центр экрана по X
            SCREEN_HEIGHT // 2,  # Центр экрана по Y
            self.radius,  # Размер игрока
            self.color  # Цвет игрока
        )


class SlowZone:
    __slots__ = ('center_x', 'center_y', 'radius', 'color')  # Оптимизация памяти

    def __init__(self, x, y):  # Конструктор зоны
        self.center_x = x  # Мировая координата X центра зоны
        self.center_y = y  # Мировая координата Y центра зоны
        self.radius = SLOW_ZONE_RADIUS  # Радиус зоны
        self.color = arcade.color.BLUE  # Цвет зоны

    def draw(self, camera_x, camera_y):
        """Отрисовка зоны с учетом позиции камеры"""
        arcade.draw_circle_filled(
            self.center_x - camera_x,  # Переводим мировые координаты в экранные
            self.center_y - camera_y,  # Вычитаем смещение камеры
            self.radius,  # Радиус зоны
            self.color  # Цвет зоны
        )

    def check_collision(self, player_x, player_y, player_radius):
        """Проверка столкновения игрока с зоной"""
        # Вычисляем расстояние между центрами
        distance = math.hypot(player_x - self.center_x, player_y - self.center_y)
        # Столкновение, если расстояние меньше суммы радиусов
        return distance < (player_radius + self.radius)


class MyGame(arcade.Window):  # Основной класс игры
    def __init__(self):
        # Создаем окно с заданными параметрами
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Игра с физикой и энергией")
        arcade.set_background_color(arcade.color.DARK_GREEN)  # Цвет фона

        # Инициализация игровых объектов
        self.player = None  # Игрок (создадим в setup)
        self.slow_zones = []  # Список замедляющих зон
        self.pressed_keys = set()  # Множество нажатых клавиш
        self.camera_x = 0  # Смещение камеры по X
        self.camera_y = 0  # Смещение камеры по Y

    def setup(self):
        """Настройка игры (вызывается один раз при старте)"""
        self.player = Player()  # Создаем игрока

        # Генерация замедляющих зон
        zone_area = 2000  # Размер области для генерации зон
        self.slow_zones = [  # Генератор списка зон
            SlowZone(
                random.randint(-zone_area // 2, zone_area // 2),  # Случайный X
                random.randint(-zone_area // 2, zone_area // 2)  # Случайный Y
            )
            for _ in range(SLOW_ZONE_COUNT)  # Создаем заданное количество зон
        ]

        # Инициализация камеры - центрируем на игроке
        self.camera_x = self.player.center_x - SCREEN_WIDTH // 2
        self.camera_y = self.player.center_y - SCREEN_HEIGHT // 2

    def on_draw(self):
        """Отрисовка игры (вызывается каждый кадр)"""
        self.clear()  # Очистка экрана

        # 1. Отрисовка всех замедляющих зон
        for zone in self.slow_zones:
            # Передаем позицию камеры для правильного отображения
            zone.draw(self.camera_x, self.camera_y)

        # 2. Отрисовка игрока (всегда в центре экрана)
        self.player.draw()

        # 3. Отображение статистики
        # Подготовка данных для отображения
        stats = [
            (f"Энергия: {int(self.player.energy)}", 30),  # Уровень энергии
            (f"Макс. скорость: {self.player.target_max_speed}", 60),  # Лимит скорости
            (f"Текущая скорость: {math.hypot(self.player.velocity_x, self.player.velocity_y):.1f}", 90),
            # Фактическая скорость
            ("В замедляющей зоне" if self.player.in_slow_zone else "В обычной зоне", 120),  # Статус зоны
            (f"Координаты: ({int(self.player.center_x)}, {int(self.player.center_y)})", 150)  # Позиция в мире
        ]

        # Цвета для разных строк статистики
        colors = [arcade.color.WHITE, arcade.color.WHITE, arcade.color.LIGHT_GREEN,
                  arcade.color.YELLOW, arcade.color.LIGHT_BLUE]

        # Отрисовка всех строк статистики
        for i, (text, y_offset) in enumerate(stats):
            arcade.draw_text(
                text,  # Текст для отображения
                10,  # Отступ слева
                SCREEN_HEIGHT - y_offset,  # Позиция по Y (сверху вниз)
                colors[i],  # Цвет текста
                20 if i < 2 else 16  # Размер шрифта (первые две строки крупнее)
            )

    def update_camera(self):
        """Плавное слежение камеры за игроком"""
        # Вычисляем целевую позицию камеры (центрируем на игроке)
        target_x = self.player.center_x - SCREEN_WIDTH // 2
        target_y = self.player.center_y - SCREEN_HEIGHT // 2
        # Плавная интерполяция текущей позиции камеры к целевой
        self.camera_x += (target_x - self.camera_x) * 0.1  # 10% шаг к цели
        self.camera_y += (target_y - self.camera_y) * 0.1

    def check_slow_zones(self):
        """Проверка нахождения игрока в замедляющих зонах"""
        px, py, pr = self.player.center_x, self.player.center_y, self.player.radius
        # Проверяем столкновение с любой из зон
        # any() возвращает True если хотя бы одна проверка вернула True
        self.player.in_slow_zone = any(
            zone.check_collision(px, py, pr) for zone in self.slow_zones
        )

    def on_update(self, delta_time):
        """Главный игровой цикл (вызывается 60 раз в секунду)"""
        # 1. Обработка ввода и обновление игрока
        self.player.handle_input(self.pressed_keys)  # Передаем нажатые клавиши
        self.player.update()  # Обновляем физику игрока

        # 2. Проверка коллизий с замедляющими зонами
        self.check_slow_zones()

        # 3. Обновление позиции камеры
        self.update_camera()

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиши"""
        self.pressed_keys.add(key)  # Добавляем клавишу в множество нажатых

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиши"""
        self.pressed_keys.discard(key)  # Удаляем клавишу из множества


def main():
    """Главная функция запуска игры"""
    window = MyGame()  # Создаем экземпляр игры
    window.setup()  # Настраиваем игру
    arcade.run()  # Запускаем игровой цикл


if __name__ == "__main__":  # Проверка, что файл запущен напрямую
    main()  # Запуск игры
