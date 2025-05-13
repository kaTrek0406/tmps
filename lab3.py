import pygame
import random

# Инициализация Pygame
pygame.init()

# Размеры экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Частота кадров
FPS = 60

# Цвета (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


# --- Порождающие и структурные паттерны ---

# Паттерн Одиночка + Легковес: ResourceManager хранит единственный экземпляр и кеширует ресурсы (изображения) для повторного использования
class ResourceManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            # Инициализируем словарь для кеширования изображений
            cls._instance._images = {}
        return cls._instance

    def get_image(self, name):
        """Получить изображение по имени, загрузив (или сгенерировав) его один раз и сохранив в кеше (паттерн Легковес)."""
        if name in self._images:
            return self._images[name]
        # Здесь мы симулируем загрузку изображения. В реальной игре стоило бы загрузить файл с диска.
        # Для демонстрации создаём простые цветные фигуры в Surface.
        if name == "player":
            # Создаём треугольник (корабль игрока)
            surface = pygame.Surface((40, 30), pygame.SRCALPHA)
            pygame.draw.polygon(surface, GREEN, [(0, 30), (20, 0), (40, 30)])
        elif name == "enemy1":
            # Красный круг для врага типа 1
            surface = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(surface, RED, (15, 15), 15)
        elif name == "enemy2":
            # Синий круг для врага типа 2
            surface = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(surface, BLUE, (15, 15), 15)
        elif name == "bullet":
            # Жёлтый прямоугольник для пули
            surface = pygame.Surface((5, 10), pygame.SRCALPHA)
            pygame.draw.rect(surface, YELLOW, (0, 0, 5, 10))
        else:
            # По умолчанию - белый квадрат 20x20
            surface = pygame.Surface((20, 20))
            surface.fill(WHITE)
        self._images[name] = surface
        return surface


# Паттерн Прототип: базовый класс для объектов, умеющих клонировать сами себя
class Prototype:
    def clone(self):
        raise NotImplementedError


# Паттерн Стратегия: определяем интерфейс стратегии движения
class MovementStrategy:
    def move(self, enemy, dt):
        """Абстрактное движение врага."""
        raise NotImplementedError


# Конкретная стратегия: движение врага прямо вниз
class StraightDownStrategy(MovementStrategy):
    def move(self, enemy, dt):
        # Враг движется вниз с постоянной скоростью
        enemy.rect.y += int(enemy.speed * dt)
        # Без изменения по горизонтали


# Конкретная стратегия: движение врага зигзагом
class ZigZagStrategy(MovementStrategy):
    def __init__(self):
        self.direction = 1  # 1 - вправо, -1 - влево
        self.switch_time = 0

    def move(self, enemy, dt):
        # Двигается вниз
        enemy.rect.y += int(enemy.speed * dt)
        # Смещается по горизонтали
        enemy.rect.x += self.direction * 2  # сдвиг на 2 пикселя вбок каждый кадр
        # Периодическая смена направления или при столкновении с границей
        self.switch_time += dt
        if self.switch_time > 0.5:  # менять направление каждые 0.5 секунды
            self.switch_time = 0
            self.direction *= -1
        # Не выходить за пределы экрана по горизонтали
        if enemy.rect.left < 0:
            enemy.rect.left = 0
            self.direction = 1
        elif enemy.rect.right > SCREEN_WIDTH:
            enemy.rect.right = SCREEN_WIDTH
            self.direction = -1


# Паттерн Наблюдатель: определяем абстрактного наблюдателя
class Observer:
    def update(self, event_type, data):
        raise NotImplementedError


# Паттерн Одиночка + Наблюдатель: EventManager управляет подпиской и рассылкой событий
class EventManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
            cls._instance._subscribers = {}  # словарь: событие -> список наблюдателей
        return cls._instance

    def subscribe(self, event_type, observer):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if observer not in self._subscribers[event_type]:
            self._subscribers[event_type].append(observer)

    def unsubscribe(self, event_type, observer):
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(observer)
            except ValueError:
                pass

    def notify(self, event_type, data=None):
        if event_type in self._subscribers:
            for observer in list(self._subscribers[event_type]):
                observer.update(event_type, data)


# Паттерн Абстрактная фабрика: фабрика для создания игровых объектов (игрок, враги, пули)
class GameObjectFactory:
    def __init__(self):
        self.res = ResourceManager()  # используем менеджер ресурсов для изображений
        # Инициализируем прототипы (паттерн Прототип для пуль, возможно и для врагов)
        bullet_image = self.res.get_image("bullet")
        self.bullet_prototype = Bullet(bullet_image, speed=300)
        # Создадим по одному прототипу для каждого типа врагов
        enemy_image1 = self.res.get_image("enemy1")
        enemy_image2 = self.res.get_image("enemy2")
        self.enemy_prototype1 = Enemy(enemy_image1, speed=100, hp=1, strategy=StraightDownStrategy(), points=50)
        self.enemy_prototype2 = Enemy(enemy_image2, speed=80, hp=2, strategy=ZigZagStrategy(), points=100)

    def create_player(self):
        # Создаём игрока с нужными параметрами
        player_image = self.res.get_image("player")
        player = Player(player_image, speed=200, lives=3)
        # Оснащаем игрока "оружием" (паттерн Заместитель: ограничиваем скорость стрельбы)
        real_gun = Gun(self, player)  # реальный объект оружия, использует фабрику для пули
        player.gun = RateLimitedGun(real_gun, 0.3)  # прокси-оружие с перезарядкой 0.3 секунды между выстрелами
        return player

    def create_enemy(self):
        # Создаём врага, выбирая тип для разнообразия
        if random.random() < 0.5:
            # Клонируем прототип врага типа 1 (движется прямо)
            enemy = self.enemy_prototype1.clone()
        else:
            # Клонируем прототип врага типа 2 (движется зигзагом)
            enemy = self.enemy_prototype2.clone()
        # Расположим врага в случайной позиции сверху
        enemy.rect.x = random.randint(0, SCREEN_WIDTH - enemy.rect.width)
        enemy.rect.y = -enemy.rect.height
        return enemy

    def create_bullet(self, x, y):
        # Клонируем прототип пули и устанавливаем её позицию
        bullet = self.bullet_prototype.clone()
        bullet.rect.centerx = x
        bullet.rect.bottom = y
        return bullet


# Паттерн Заместитель (Proxy): Реальный объект оружия, создающий пули
class Gun:
    def __init__(self, factory, owner):
        self.factory = factory
        self.owner = owner  # владелец оружия (игрок или враг, здесь игрок)

    def shoot(self):
        # Создать пулю в позиции владельца
        x = self.owner.rect.centerx
        y = self.owner.rect.top
        bullet = self.factory.create_bullet(x, y)
        return bullet


# Паттерн Заместитель (Proxy): Оружие с ограниченной скорострельностью (контролирует вызовы Gun.shoot)
class RateLimitedGun:
    def __init__(self, real_gun, cooldown):
        self.real_gun = real_gun
        self.cooldown = cooldown  # задержка между выстрелами (секунд)
        self.last_shot_time = 0.0

    def shoot(self):
        current_time = pygame.time.get_ticks() / 1000.0  # текущее время в секундах
        if current_time - self.last_shot_time >= self.cooldown:
            # Достаточно времени прошло, можно стрелять
            self.last_shot_time = current_time
            return self.real_gun.shoot()
        else:
            # Ещё перезарядка не завершена, выстрел не производится
            return None


# Игровые объекты:

class Bullet(Prototype):
    def __init__(self, image, speed=300):
        self.image = image
        self.rect = image.get_rect()
        self.speed = speed
        self.damage = 1  # урон от пули

    # Паттерн Прототип: метод clone для создания новой пули с копированием свойств
    def clone(self):
        # Создаём новую пулю с теми же параметрами (изображение не копируем, оно разделяется как легковес)
        new_bullet = Bullet(self.image, self.speed)
        new_bullet.rect = self.image.get_rect()  # своя область rect
        new_bullet.damage = self.damage
        return new_bullet

    def update(self, dt):
        # Движение пули вверх (уменьшение координаты Y)
        self.rect.y -= int(self.speed * dt)


class Enemy(Prototype):
    def __init__(self, image, speed, hp, strategy: MovementStrategy, points=100):
        self.image = image
        self.rect = image.get_rect()
        self.speed = speed
        self.hp = hp
        self.strategy = strategy  # Паттерн Стратегия: компоновка с объектом стратегии движения
        self.points = points

    # Паттерн Прототип: метод clone для дублирования врага
    def clone(self):
        # Создаём нового врага с теми же свойствами.
        # Обращаем внимание: даём новой копии свой собственный экземпляр стратегии (чтобы не разделять состояние стратегии между врагами).
        if isinstance(self.strategy, ZigZagStrategy):
            new_strategy = ZigZagStrategy()
        else:
            new_strategy = StraightDownStrategy()
        new_enemy = Enemy(self.image, self.speed, self.hp, new_strategy, self.points)
        return new_enemy

    def update(self, dt):
        # Двигаем врага, используя его стратегию движения
        self.strategy.move(self, dt)

    def is_off_screen(self):
        return self.rect.y > SCREEN_HEIGHT

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            # Враг погибает, уведомляем наблюдателей о событии "enemy_killed"
            EventManager().notify("enemy_killed", self.points)
            return True
        return False


class Player:
    def __init__(self, image, speed=200, lives=3):
        self.image = image
        self.rect = image.get_rect()
        # Начальная позиция игрока - внизу по центру экрана
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = speed
        self.lives = lives
        self.gun = None  # будет установлен фабрикой

    def move(self, dx, dt):
        # Перемещение по горизонтали (dx = -1 влево, 1 вправо)
        self.rect.x += int(dx * self.speed * dt)
        # Не выходить за границы экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def shoot(self):
        if self.gun:
            bullet = self.gun.shoot()
            return bullet
        return None


# Табло очков и жизней (паттерн Наблюдатель: подписывается на события игры, например уничтожение врага или попадание по игроку)
class Scoreboard(Observer):
    def __init__(self, initial_lives=3):
        self.score = 0
        self.lives = initial_lives
        # Шрифт для отображения текста
        self.font = pygame.font.Font(None, 36)
        self.color = WHITE

    def update(self, event_type, data):
        # Реакция на события (метод наблюдателя)
        if event_type == "enemy_killed":
            # Увеличиваем счёт (data передаёт количество очков за врага)
            if data is not None:
                self.score += data
            else:
                self.score += 100
        elif event_type == "player_hit":
            # Уменьшаем число жизней при попадании по игроку
            if data is not None:
                self.lives = data
            else:
                self.lives -= 1
        # Событие "player_died" здесь можно обработать при необходимости (например, остановить таймер и т.п.)

    def draw(self, surface):
        # Отображение счёта и количества жизней на экране
        text = self.font.render(f"Score: {self.score}   Lives: {self.lives}", True, self.color)
        surface.blit(text, (10, 10))

    def reset(self, lives):
        # Сброс счета и жизней (например, при перезапуске игры)
        self.score = 0
        self.lives = lives


# Паттерн Состояние: абстрактный класс состояния игры
class GameState:
    def __init__(self, game):
        self.game = game  # ссылка на контекст (игру)

    def handle_events(self):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError


# Конкретное состояние: игровой процесс (игра в активном режиме)
class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        # Создаём игрока и начальные игровые объекты через фабрику
        self.player = game.factory.create_player()
        self.bullets = []  # список пуль на экране
        self.enemies = []  # список врагов на экране
        self.spawn_timer = 0  # таймер для появления врагов
        # Сбросить счёт и жизни на начало игры
        game.scoreboard.reset(self.player.lives)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Выход из игры
                self.game.running = False

    def update(self, dt):
        # Появление новых врагов с течением времени
        self.spawn_timer += dt
        if self.spawn_timer > 1.0:  # раз в 1 секунду
            enemy = self.game.factory.create_enemy()
            self.enemies.append(enemy)
            self.spawn_timer = 0
        # Обработка ввода для движения и стрельбы
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move(-1, dt)
        if keys[pygame.K_RIGHT]:
            self.player.move(1, dt)
        if keys[pygame.K_SPACE]:
            bullet = self.player.shoot()
            if bullet:
                self.bullets.append(bullet)
        # Обновление позиций пуль
        for bullet in list(self.bullets):
            bullet.update(dt)
            # Удаляем пулю, если вышла за верхний край экрана
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)
        # Обновление позиций врагов
        for enemy in list(self.enemies):
            enemy.update(dt)
            # Если враг ушёл за нижний край экрана
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
                # Считаем, что игрок пропустил врага - потеря жизни
                EventManager().notify("player_hit", self.player.lives - 1)
                self.player.lives -= 1
                # Если жизни кончились - сообщаем о смерти игрока и выходим из состояния
                if self.player.lives <= 0:
                    EventManager().notify("player_died", None)
                    return
                continue
            # Проверка столкновения врага с игроком
            if enemy.rect.colliderect(self.player.rect):
                # Столкновение с игроком - враг уничтожается, игрок теряет жизнь
                self.enemies.remove(enemy)
                EventManager().notify("player_hit", self.player.lives - 1)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    EventManager().notify("player_died", None)
                    return
                continue
            # Проверка столкновения врага с пулями
            for bullet in list(self.bullets):
                if bullet.rect.colliderect(enemy.rect):
                    # Пуля попала во врага
                    self.bullets.remove(bullet)
                    died = enemy.take_damage(bullet.damage)
                    if died:
                        # Враг уничтожен (take_damage уже отправил событие enemy_killed)
                        self.enemies.remove(enemy)
                    break  # выходим из цикла по пулям, т.к. текущий враг уже получил повреждение

    def draw(self, surface):
        surface.fill(BLACK)
        # Отрисовка игрока, пуль, врагов и табло
        surface.blit(self.player.image, self.player.rect)
        for bullet in self.bullets:
            surface.blit(bullet.image, bullet.rect)
        for enemy in self.enemies:
            surface.blit(enemy.image, enemy.rect)
        self.game.scoreboard.draw(surface)


# Конкретное состояние: экран Game Over
class GameOverState(GameState):
    def __init__(self, game):
        super().__init__(game)
        # Подготавливаем текст "Game Over" и инструкцию по перезапуску
        self.font = pygame.font.Font(None, 72)
        self.subfont = pygame.font.Font(None, 36)
        self.text = self.font.render("GAME OVER", True, RED)
        self.subtext = self.subfont.render("Press R to Restart or Q to Quit", True, WHITE)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Перезапуск игры: смена состояния на PlayingState
                    self.game.change_state(PlayingState(self.game))
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    # Выход из игры при нажатии Q или Esc
                    self.game.running = False

    def update(self, dt):
        # На экране Game Over ничего не обновляется
        pass

    def draw(self, surface):
        surface.fill(BLACK)
        # Выводим сообщение "Game Over" и финальный счёт
        surface.blit(self.text, ((SCREEN_WIDTH - self.text.get_width()) // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(self.subtext, ((SCREEN_WIDTH - self.subtext.get_width()) // 2, SCREEN_HEIGHT // 2 + 10))
        score_text = self.subfont.render(f"Final Score: {self.game.scoreboard.score}", True, WHITE)
        surface.blit(score_text, ((SCREEN_WIDTH - score_text.get_width()) // 2, SCREEN_HEIGHT // 2 + 50))


# Паттерн Фасад: класс Game упрощает запуск игры и переключение состояний (выступает интерфейсом для управления игровым процессом)
class Game(Observer):
    def __init__(self):
        # Инициализация окна
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Shooter Game - Design Patterns Demo")
        self.clock = pygame.time.Clock()
        self.running = True
        # Создание основных компонентов
        self.factory = GameObjectFactory()
        self.scoreboard = Scoreboard(initial_lives=3)
        # Паттерн Наблюдатель: подписываем табло на игровые события, а Game на событие смены состояния (смерть игрока)
        em = EventManager()
        em.subscribe("enemy_killed", self.scoreboard)
        em.subscribe("player_hit", self.scoreboard)
        em.subscribe("player_died", self)  # Game будет следить за смертью игрока, чтобы переключить состояние
        # Начальное состояние игры - PlayingState
        self.current_state = PlayingState(self)

    # Реализация Observer: Game как наблюдатель получает событие player_died и переключает состояние
    def update(self, event_type, data):
        if event_type == "player_died":
            # Переключаем состояние на GameOver при смерти игрока
            self.change_state(GameOverState(self))

    def change_state(self, new_state):
        # Метод для смены текущего состояния (паттерн Состояние)
        self.current_state = new_state

    def run(self):
        # Основной игровой цикл
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # разница времени между кадрами в секундах
            # Делегируем обработку событий, обновление и отрисовку текущему состоянию
            self.current_state.handle_events()
            self.current_state.update(dt)
            # (если состояние сменилось в процессе обновления, получаем новое состояние перед отрисовкой)
            state = self.current_state
            state.draw(self.screen)
            pygame.display.flip()
        pygame.quit()


# Запуск игры, если модуль выполняется напрямую
if __name__ == "__main__":
    game = Game()
    game.run()
