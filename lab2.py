import pygame
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_SPACE, K_r
import random
from abc import ABC, abstractmethod

# ============================
# Singleton: метакласс для реализации одиночки (SingletonType)
# ============================
class SingletonType(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

# Глобальный менеджер игры, реализованный как Singleton.
# Хранит общее состояние игры: экран, размеры, игрока, списки врагов и пуль, фабрику объектов, счёт и уровень.
class GameManager(metaclass=SingletonType):
    def __init__(self):
        self.screen = None          # Экран Pygame
        self.width = 0              # Ширина экрана
        self.height = 0             # Высота экрана
        self.player = None          # Объект игрока
        self.enemies = []           # Список врагов
        self.bullets = []           # Список пуль
        self.factory = None         # Фабрика игровых объектов (Abstract Factory)
        self.score = 0              # Счёт игрока
        self.level = 1              # Уровень игры

# ============================
# Flyweight: Фабрика спрайтов для разделяемых ресурсов
# ============================
class SpriteFlyweightFactory:
    _sprites = {}  # Кеш созданных спрайтов: ключом является (name, color)

    @staticmethod
    def get_sprite(name, color=(255, 255, 255)):
        """
        Возвращает Surface для заданного типа объекта с указанным цветом.
        Если спрайт ещё не создан, создаёт новый и сохраняет его в кеше.
        """
        key = (name, color)
        if key not in SpriteFlyweightFactory._sprites:
            if name == 'enemy':
                # Простой квадрат 20x20 для врага
                surface = pygame.Surface((20, 20))
                surface.fill(color)
            elif name == 'bullet':
                # Прямоугольник 5x10 для пули
                surface = pygame.Surface((5, 10))
                surface.fill(color)
            elif name == 'player':
                # Прямоугольник 50x30 для игрока
                surface = pygame.Surface((50, 30))
                surface.fill(color)
            else:
                surface = pygame.Surface((20, 20))
                surface.fill(color)
            SpriteFlyweightFactory._sprites[key] = surface
        return SpriteFlyweightFactory._sprites[key]

# ============================
# Abstract Factory: Абстрактная фабрика для создания игровых объектов
# ============================
class GameObjectFactory(ABC):
    @abstractmethod
    def create_player(self, x, y):
        pass

    @abstractmethod
    def create_enemy(self):
        pass

    @abstractmethod
    def create_bullet(self, x, y):
        pass

# Конкретная фабрика игровых объектов.
# Использует паттерн Prototype для врагов и пуль: хранит прототипы и клонирует их при создании новых объектов.
class SimpleGameFactory(GameObjectFactory):
    def __init__(self):
        # Создаем прототипы врага и пули.
        # Здесь нельзя создать экземпляр абстрактного класса, поэтому вызываем конструкторы уже конкретных объектов.
        # В данном примере для врага используем класс Enemy, который реализует update() ниже.
        self.enemy_prototype = Enemy(0, 0)
        self.bullet_prototype = Bullet(0, 0)

    def create_player(self, x, y):
        return Player(x, y)

    def create_enemy(self):
        # Клонируем прототип врага.
        new_enemy = self.enemy_prototype.clone()
        return new_enemy

    def create_bullet(self, x, y):
        new_bullet = self.bullet_prototype.clone()
        new_bullet.rect.centerx = x
        new_bullet.rect.bottom = y
        return new_bullet

# ============================
# Proxy: Класс-заместитель для оружия, ограничивающий частоту выстрелов
# ============================
class Gun:
    def __init__(self, factory):
        self.factory = factory  # Фабрика для создания пуль

    def fire(self, x, y):
        """Создает пулю через фабрику и добавляет её в список пуль в GameManager."""
        bullet = self.factory.create_bullet(x, y)
        GameManager().bullets.append(bullet)
        # Здесь можно добавить звуковой эффект выстрела.

class GunProxy:
    def __init__(self, real_gun, cooldown_ms):
        self._real_gun = real_gun      # Реальное оружие
        self.cooldown = cooldown_ms    # Задержка между выстрелами (в мс)
        self.last_shot_time = -self.cooldown  # Время последнего выстрела

    def fire(self, x, y):
        """Вызывает реальный выстрел, если прошёл достаточный интервал с прошлого выстрела."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.cooldown:
            self._real_gun.fire(x, y)
            self.last_shot_time = current_time

# ============================
# Prototype: Абстрактные классы врагов и пуль с поддержкой клонирования
# ============================
class Enemy:
    """Класс врага."""
    def __init__(self, x, y):
        self.image = SpriteFlyweightFactory.get_sprite('enemy', (255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 2  # скорость движения вниз

    def update(self):
        """Обновляет позицию врага (движется вниз)."""
        self.rect.y += self.speed

    def clone(self):
        """Возвращает копию врага, используя его текущие параметры."""
        new_enemy = Enemy(self.rect.x, self.rect.y)
        new_enemy.speed = self.speed
        return new_enemy

class Bullet:
    """Класс пули."""
    def __init__(self, x, y):
        self.image = SpriteFlyweightFactory.get_sprite('bullet', (255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -5  # скорость движения вверх

    def update(self):
        """Обновляет позицию пули (движется вверх)."""
        self.rect.y += self.speed

    def clone(self):
        """Возвращает копию пули с текущими параметрами."""
        new_bullet = Bullet(self.rect.centerx, self.rect.bottom)
        new_bullet.speed = self.speed
        return new_bullet

# ============================
# Класс игрока
# ============================
class Player:
    def __init__(self, x, y):
        self.image = SpriteFlyweightFactory.get_sprite('player', (0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
        self.speed = 5
        # Создаем оружие: реальное оружие оборачиваем в Proxy для ограничения стрельбы.
        real_gun = Gun(GameManager().factory)
        self.gun = GunProxy(real_gun, cooldown_ms=300)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        gm = GameManager()
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > gm.width:
            self.rect.right = gm.width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > gm.height:
            self.rect.bottom = gm.height

    def shoot(self):
        self.gun.fire(self.rect.centerx, self.rect.top)

# ============================
# Facade: Фасад для управления игровым процессом
# ============================
class GameFacade:
    def __init__(self, width=800, height=600):
        pygame.init()
        # Инициализируем глобальное состояние игры
        self.manager = GameManager()
        self.manager.width = width
        self.manager.height = height
        self.manager.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Shooter Game with Patterns")
        # Устанавливаем фабрику игровых объектов
        self.manager.factory = SimpleGameFactory()
        # Создаем игрока через фабрику
        self.manager.player = self.manager.factory.create_player(width // 2, height)
        # Очищаем списки врагов и пуль, а также сбрасываем счёт и уровень
        self.manager.enemies = []
        self.manager.bullets = []
        self.manager.score = 0
        self.manager.level = 1
        # Устанавливаем событие таймера для генерации врагов
        self.ENEMY_SPAWN_EVENT = pygame.USEREVENT + 1
        # Изначальный интервал спавна врагов: 1000 мс
        pygame.time.set_timer(self.ENEMY_SPAWN_EVENT, 1000)
        # Шрифт для отрисовки счета и уровня на экране
        self.font = pygame.font.SysFont(None, 30)

    def reset_game(self):
        """Сбрасывает игру: очищает списки врагов и пуль, сбрасывает счёт, возвращает игрока в исходную позицию, устанавливает начальные параметры уровня."""
        self.manager.enemies.clear()
        self.manager.bullets.clear()
        self.manager.player.rect.midbottom = (self.manager.width // 2, self.manager.height)
        self.manager.score = 0
        self.manager.level = 1
        if isinstance(self.manager.player.gun, GunProxy):
            self.manager.player.gun.last_shot_time = -self.manager.player.gun.cooldown
        pygame.time.set_timer(self.ENEMY_SPAWN_EVENT, 1000)
        self.manager.player.gun.cooldown = 300

    def update_level(self):
        """
        Обновляет уровень: чем выше уровень, тем меньше пуль (больше задержка выстрела) и тем больше врагов (интервал спавна уменьшается).
        Новый уровень вычисляется по формуле: level = score // 10 + 1.
        """
        new_level = self.manager.score // 10 + 1
        if new_level != self.manager.level:
            self.manager.level = new_level
            # Уменьшаем интервал появления врагов: например, интервал = максимум(200, 1000 - 100*(level-1))
            new_interval = max(200, 1000 - (new_level - 1) * 100)
            pygame.time.set_timer(self.ENEMY_SPAWN_EVENT, new_interval)
            # Увеличиваем задержку оружия (GunProxy): чем выше уровень, тем меньше выпускаются пули
            self.manager.player.gun.cooldown = 300 + (new_level - 1) * 100

    def spawn_enemy(self):
        """Создает нового врага и добавляет его в список врагов."""
        enemy = self.manager.factory.create_enemy()
        enemy.rect.x = random.randint(0, self.manager.width - enemy.rect.width)
        enemy.rect.y = 0
        self.manager.enemies.append(enemy)

    def run_game(self):
        """Запускает основной игровой цикл."""
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_r:
                        self.reset_game()
                elif event.type == self.ENEMY_SPAWN_EVENT:
                    self.spawn_enemy()
            # Обработка ввода: движение игрока и стрельба
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[K_LEFT]:
                dx -= self.manager.player.speed
            if keys[K_RIGHT]:
                dx += self.manager.player.speed
            if keys[K_UP]:
                dy -= self.manager.player.speed
            if keys[K_DOWN]:
                dy += self.manager.player.speed
            self.manager.player.move(dx, dy)
            if keys[K_SPACE]:
                self.manager.player.shoot()

            # Обновление пуль
            for bullet in list(self.manager.bullets):
                bullet.update()
            # Обновление врагов
            for enemy in list(self.manager.enemies):
                enemy.update()

            # Проверка столкновений пуль с врагами
            for bullet in list(self.manager.bullets):
                for enemy in list(self.manager.enemies):
                    if bullet.rect.colliderect(enemy.rect):
                        if bullet in self.manager.bullets:
                            self.manager.bullets.remove(bullet)
                        if enemy in self.manager.enemies:
                            self.manager.enemies.remove(enemy)
                        self.manager.score += 1
                        break

            # Удаление пуль, вышедших за верхнюю границу экрана
            for bullet in list(self.manager.bullets):
                if bullet.rect.bottom < 0:
                    self.manager.bullets.remove(bullet)
            # Удаление врагов, вышедших за нижнюю границу
            for enemy in list(self.manager.enemies):
                if enemy.rect.top > self.manager.height:
                    self.manager.enemies.remove(enemy)
            # Проверка столкновений врагов с игроком (при столкновении игра сбрасывается)
            for enemy in list(self.manager.enemies):
                if enemy.rect.colliderect(self.manager.player.rect):
                    self.reset_game()
                    break

            # Обновляем уровень, если необходимо (изменения параметров в зависимости от счёта)
            self.update_level()

            # Отрисовка игровых объектов
            self.manager.screen.fill((0, 0, 0))
            self.manager.screen.blit(self.manager.player.image, self.manager.player.rect)
            for enemy in self.manager.enemies:
                self.manager.screen.blit(enemy.image, enemy.rect)
            for bullet in self.manager.bullets:
                self.manager.screen.blit(bullet.image, bullet.rect)
            # Отображаем счёт и уровень на экране
            score_text = self.font.render(f"Score: {self.manager.score}", True, (255, 255, 255))
            level_text = self.font.render(f"Level: {self.manager.level}", True, (255, 255, 255))
            self.manager.screen.blit(score_text, (10, 10))
            self.manager.screen.blit(level_text, (10, 40))

            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = GameFacade()
    game.run_game()
