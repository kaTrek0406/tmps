import pygame
from abc import ABC, abstractmethod


# ============================
# Singleton: Глобальное состояние игры
# ============================
class GameStateSingleton:
    """Класс-синглтон для хранения глобального состояния игры и конфигурации."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameStateSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Инициализировать состояние только один раз
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.score = 0
            self.level = 1
            self.current_factory = None
            # Глобальные настройки (размеры экрана)
            self.screen_width = 800
            self.screen_height = 600


# ============================
# Абстрактные базовые классы для игровых объектов
# ============================
class Enemy(ABC):
    """Абстрактный класс для врагов."""

    def __init__(self, x, y, color=(255, 0, 0), size=40, speed=2):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed  # скорость движения по вертикали
        # Прямоугольник для позиции и коллизий
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    @abstractmethod
    def update(self):
        """Обновить позицию врага (определяется в подклассах)."""
        pass

    def draw(self, surface):
        """Отрисовать врага на заданной поверхности."""
        pygame.draw.rect(surface, self.color, self.rect)

    def is_off_screen(self, height):
        """Проверить, вышел ли враг за нижнюю границу экрана."""
        return self.rect.y > height


class Bullet(ABC):
    """Абстрактный класс для пуль/снарядов."""

    def __init__(self, x, y, color=(255, 255, 0), radius=5, speed=5):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.speed = speed  # скорость по вертикали (отрицательная для движения вверх)
        # Прямоугольник для коллизий (около центра)
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    @abstractmethod
    def update(self):
        """Обновить позицию пули (определяется в подклассах)."""
        pass

    def draw(self, surface):
        """Отрисовать пулю на заданной поверхности."""
        pygame.draw.circle(surface, self.color, (self.rect.centerx, self.rect.centery), self.radius)

    def is_off_screen(self, height):
        """Проверить, вышла ли пуля за границы экрана."""
        return self.rect.y < 0 or self.rect.y > height

    @abstractmethod
    def clone(self):
        """Создать копию этой пули (паттерн Prototype)."""
        pass


# ============================
# Конкретные классы врагов для разных тем
# ============================
class AlienEnemy(Enemy):
    """Враг в виде инопланетянина (космическая тема)."""

    def __init__(self, x, y):
        # Зеленый квадрат, движется быстрее вниз
        super().__init__(x, y, color=(0, 255, 0), size=40, speed=3)

    def update(self):
        self.rect.y += self.speed


class SoldierEnemy(Enemy):
    """Враг-воин (военная тема)."""

    def __init__(self, x, y):
        # Серый квадрат, движется чуть медленнее
        super().__init__(x, y, color=(128, 128, 128), size=40, speed=2)

    def update(self):
        self.rect.y += self.speed


# ============================
# Конкретные классы пуль для разных тем
# ============================
class LaserBullet(Bullet):
    """Лазерная пуля (космическая тема)."""

    def __init__(self, x, y):
        # Голубая пуля, движется быстро вверх
        super().__init__(x, y, color=(0, 255, 255), radius=5, speed=-7)

    def update(self):
        self.rect.y += self.speed

    def clone(self):
        # Создаем копию лазерной пули; позиция изначально не важна
        return LaserBullet(0, 0)


class NormalBullet(Bullet):
    """Обычная пуля (военная тема)."""

    def __init__(self, x, y):
        # Желтая пуля, движется вверх медленнее лазера
        super().__init__(x, y, color=(255, 255, 0), radius=5, speed=-5)

    def update(self):
        self.rect.y += self.speed

    def clone(self):
        return NormalBullet(0, 0)


# ============================
# Abstract Factory: Создание семейства объектов по теме
# ============================
class GameElementFactory(ABC):
    """Абстрактная фабрика для создания игровых элементов (врагов и пуль)."""

    @abstractmethod
    def create_enemy(self, x, y):
        pass

    @abstractmethod
    def create_bullet(self, x, y):
        pass


class SpaceFactory(GameElementFactory):
    """Фабрика для космической темы: создает инопланетных врагов и лазерные пули."""

    def __init__(self):
        # Прототип пули для клонирования (паттерн Prototype)
        self._bullet_prototype = LaserBullet(0, 0)

    def create_enemy(self, x, y):
        return AlienEnemy(x, y)

    def create_bullet(self, x, y):
        new_bullet = self._bullet_prototype.clone()  # клонирование прототипа
        new_bullet.rect.centerx = x
        new_bullet.rect.centery = y
        return new_bullet


class ArmyFactory(GameElementFactory):
    """Фабрика для военной темы: создает солдат-врагов и обычные пули."""

    def __init__(self):
        self._bullet_prototype = NormalBullet(0, 0)

    def create_enemy(self, x, y):
        return SoldierEnemy(x, y)

    def create_bullet(self, x, y):
        new_bullet = self._bullet_prototype.clone()
        new_bullet.rect.centerx = x
        new_bullet.rect.centery = y
        return new_bullet


# ============================
# Класс игрока
# ============================
class Player:
    """Игрок, которым управляет пользователь (стрелок)."""

    def __init__(self, x, y):
        self.width = 50
        self.height = 30
        self.color = (0, 0, 255)  # синий цвет игрока
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = 5  # скорость перемещения

    def move(self, dx, dy, screen_width, screen_height):
        """Двигаем игрока на dx и dy, не выходя за границы экрана."""
        self.rect.x += dx
        self.rect.y += dy
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x + self.width > screen_width:
            self.rect.x = screen_width - self.width
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y + self.height > screen_height:
            self.rect.y = screen_height - self.height

    def draw(self, surface):
        """Отрисовываем игрока на экране."""
        pygame.draw.rect(surface, self.color, self.rect)


# ============================
# Основной игровой цикл
# ============================
def main():
    pygame.init()
    state = GameStateSingleton()  # Получаем глобальное состояние через синглтон
    screen = pygame.display.set_mode((state.screen_width, state.screen_height))
    pygame.display.set_caption("Shooter Game с паттернами")
    clock = pygame.time.Clock()

    # Изначально выбираем космическую тему через фабрику
    state.current_factory = SpaceFactory()
    state.level = 1

    # Создаем игрока внизу по центру экрана
    player = Player(state.screen_width // 2 - 25, state.screen_height - 60)

    # Списки для хранения активных врагов и пуль
    bullets = []
    enemies = []

    # Событие таймера для появления врагов (каждые 1000 мс)
    SPAWN_ENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ENEMY, 1000)

    font = pygame.font.SysFont(None, 30)  # Шрифт для отображения счета и уровня
    running = True
    while running:
        dt = clock.tick(60)  # ограничиваем FPS до 60
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == SPAWN_ENEMY:
                # Создаем нового врага в случайной позиции по оси X
                import random
                x_pos = random.randint(0, state.screen_width - 40)
                new_enemy = state.current_factory.create_enemy(x_pos, 0)
                enemies.append(new_enemy)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Стрельба: создаем пулю в позиции игрока
                    bullet_x = player.rect.centerx
                    bullet_y = player.rect.y
                    new_bullet = state.current_factory.create_bullet(bullet_x, bullet_y)
                    bullets.append(new_bullet)
        # Обработка непрерывного нажатия клавиш для движения игрока
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx -= player.speed
        if keys[pygame.K_RIGHT]:
            dx += player.speed
        if keys[pygame.K_UP]:
            dy -= player.speed
        if keys[pygame.K_DOWN]:
            dy += player.speed
        player.move(dx, dy, state.screen_width, state.screen_height)

        # Обновляем врагов
        for enemy in enemies[:]:
            enemy.update()
            if enemy.is_off_screen(state.screen_height):
                enemies.remove(enemy)

        # Обновляем пули
        for bullet in bullets[:]:
            bullet.update()
            if bullet.is_off_screen(state.screen_height):
                bullets.remove(bullet)

        # Проверяем столкновения пуль с врагами
        for enemy in enemies[:]:
            for bullet in bullets[:]:
                if enemy.rect.colliderect(bullet.rect):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    state.score += 1
                    if state.level == 1 and state.score >= 5:
                        state.current_factory = ArmyFactory()
                        state.level = 2
                    break

        # Проверяем столкновения врагов с игроком
        for enemy in enemies[:]:
            if enemy.rect.colliderect(player.rect):
                running = False  # Завершаем игру, если враг столкнулся с игроком
                break

        # Отрисовка игрового экрана
        screen.fill((0, 0, 0))  # очищаем экран черным фоном
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        # Отображаем счет и уровень
        score_text = font.render(f"Score: {state.score}", True, (255, 255, 255))
        level_text = font.render(f"Level: {state.level}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 40))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
