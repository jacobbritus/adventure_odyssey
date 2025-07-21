import pytmx

from classes.camera import YSortCameraGroup
from classes.enemy import Enemy
from classes.player import Player, DustParticle
from classes.Tiles import StaticTile, AnimatedTile
from pytmx.util_pygame import load_pygame

from classes.states import BattleState, LevelState
from other.settings import *

class Level:
    """A class to manage the game level."""
    def __init__(self):
        self.display_surface: pygame.Surface = pygame.display.get_surface()
        self.tmx_data = load_pygame(FOREST_MAP)
        self.ground_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.obstacle_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.enemies: pygame.sprite.Group = pygame.sprite.Group()
        self.visible_sprites = YSortCameraGroup()
        self.action_sprites: pygame.sprite.Group = pygame.sprite.Group()

        self.player = None
        self.player_hp_bar = None
        self.create_map()

    def create_map(self):
        ground_sprites = self.tmx_data.get_layer_by_name("Ground")
        if isinstance(ground_sprites, pytmx.TiledTileLayer):
            for x, y, gid in ground_sprites:
                properties = self.tmx_data.get_tile_properties_by_gid(gid)

                # Check if the tile has animations.
                if properties and properties["frames"]:

                    frames = properties["frames"]

                    frame_surfaces = [self.tmx_data.get_tile_image_by_gid(frame.gid) for frame in frames]

                    position = (int(x * TILE_SIZE), int(y * TILE_SIZE))

                    AnimatedTile(pos=position, frames=frame_surfaces,
                                 group=(self.obstacle_sprites, self.visible_sprites), tile_type="water",
                                 animation_speed=0.1)

                else:
                    surface = self.tmx_data.get_tile_image_by_gid(gid)
                    position = (int(x * TILE_SIZE), int(y * TILE_SIZE))
                    StaticTile(pos=position, surf=surface, group=(self.ground_sprites, self.visible_sprites),
                               tile_type="ground")

        enemy_sprites = self.tmx_data.get_layer_by_name("Enemies")
        if isinstance(enemy_sprites, pytmx.TiledObjectGroup):
            for obj in enemy_sprites:
                pos = (obj.x, obj.y)
                if obj.name == "Skeleton":
                    Enemy(surf=obj.image, pos=pos, monster_name=obj.name, group=(self.enemies, self.visible_sprites),
                          obstacle_sprites=self.obstacle_sprites)

                if obj.name == "Slime":
                    Enemy(surf=obj.image, pos=pos, monster_name=obj.name, group=(self.enemies, self.visible_sprites),
                          obstacle_sprites=self.obstacle_sprites)

                if obj.name == "Goblin":
                    Enemy(surf=obj.image, pos=pos, monster_name=obj.name, group=(self.enemies, self.visible_sprites),
                          obstacle_sprites=self.obstacle_sprites)

        obstacle_sprites = self.tmx_data.get_layer_by_name("Obstacles")
        if isinstance(obstacle_sprites, pytmx.TiledObjectGroup):
            for obj in obstacle_sprites:
                pos = (obj.x, obj.y)
                properties = self.tmx_data.get_tile_properties_by_gid(obj.gid)

                if obj.image:
                    # Handle obstacles with animations.
                    if properties and properties["frames"]:
                        frames = properties["frames"]
                        frame_surfaces = [self.tmx_data.get_tile_image_by_gid(frame.gid) for frame in frames]

                        AnimatedTile(pos=pos, frames=frame_surfaces,
                                     group=(self.obstacle_sprites, self.visible_sprites), tile_type="tree",
                                     animation_speed=0.1)
                    else:

                        StaticTile(pos=pos, surf=obj.image, group=(self.obstacle_sprites, self.visible_sprites),
                                   tile_type="tree")

                # separate this
                if obj.name == "Spawn":
                    self.player = Player(
                        group=self.visible_sprites,
                        spawn_coordinates=pos,
                        direction="down",
                        obstacle_sprites=self.obstacle_sprites,
                        dust_particles=self.dust_particle,
                    )

                # enemy.name in the future

                # seperate this too


    def run(self) -> None:
        if self.visible_sprites.state == LevelState.OVERWORLD:
            self.visible_sprites.update_soundtrack()
            self.overworld()
        else:
            self.visible_sprites.update_soundtrack()
            self.battle()

    def battle_transition(self):
        if not self.visible_sprites.battle_participants:
            self.visible_sprites.enemy_collision(self.player)
        else:
            if not self.visible_sprites.delay or pygame.time.get_ticks() >= self.visible_sprites.delay:
                self.visible_sprites.start_battle()



    def overworld_transition(self):
        if self.visible_sprites.battle_loop.state == BattleState.END_BATTLE and not self.visible_sprites.delay:
            self.visible_sprites.delay = pygame.time.get_ticks() + self.visible_sprites.delay_time
            self.visible_sprites.transition_timer = pygame.time.get_ticks()

        if self.visible_sprites.delay and pygame.time.get_ticks() >= self.visible_sprites.delay:
            self.visible_sprites.end_battle()


    def overworld(self) -> None:
        self.battle_transition()

        self.visible_sprites.update()
        self.visible_sprites.draw_sprites()
        self.visible_sprites.update_camera(self.player)

        self.visible_sprites.update_enemies(self.player)
        self.visible_sprites.transition_screen()

    def battle(self):
        # Make camera follow the animation
        self.visible_sprites.animation_camera = self.visible_sprites.battle_loop.state

        # self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.draw_sprites()
        self.visible_sprites.update_camera(self.player)


        self.visible_sprites.update_enemies(self.player)
        self.visible_sprites.battle_loop.update()

        # end battle
        self.overworld_transition()
        self.visible_sprites.transition_screen()

    def dust_particle(self):
        DustParticle(self.player, self.visible_sprites)

