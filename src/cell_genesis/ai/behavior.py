
import arcade
import random

COIN_COUNT = 50
class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(width=800, height=600, title="Мир еды и клеток", resizable=True)
        arcade.set_background_color(arcade.color.BLUE)
        self.player_speed = 300
        self.x = 400
        self.y = 300
        self.list_player = []
        self.coins = []
        for _ in range(COIN_COUNT):
            coin = {
                'x': random.randint(50, 800 - 50),
                'y': random.randint(50, 600 - 50),
                'radius': random.randint(10, 20),
                'collected': False
            }
            self.coins.append(coin)
        self.score = 10

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def on_draw(self):
        """Отрисовка кадра. Вызывается автоматически ~60 раз в секунду."""
        self.clear()
        self.list_player.append(arcade.draw_circle_filled(self.x, self.y, radius=10, color=arcade.color.GREEN))
        for coin in self.coins:
            if not coin['collected']:
                arcade.draw_circle_outline(
                    coin['x'], coin['y'],
                    coin['radius'],
                    arcade.color.RED, 20)
        arcade.draw_text(
            f"Собрано: {self.score}/{COIN_COUNT+self.score}",
            10, 600 - 30,
            arcade.color.WHITE, 24)

    def on_update(self, delta_time):
        if self.left_pressed and not self.right_pressed:
            self.x -= 1
        if self.right_pressed and not self.left_pressed:
            self.x += 1
        if self.up_pressed and not self.down_pressed:
            self.y += 1
        if self.down_pressed and not self.up_pressed:
            self.y -= 1
        for coin in self.coins:
            if not coin['collected']:
                # Простая проверка расстояния между центрами
                distance = ((self.x - coin['x']) ** 2 +
                            (self.y - coin['y']) ** 2) ** 0.5

                if distance < 10 + coin['radius']:
                    coin['collected'] = True
                    self.score += 1


    def on_key_press(self, key, modifiers):
        """Клавиша нажата"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True


    def on_key_release(self, key, modifiers):
        """Клавиша отпущена"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
if __name__ == "__main__":
    window = MyGame()
    arcade.run()