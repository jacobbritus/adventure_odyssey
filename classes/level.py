import random

import pygame.time
import pytmx

from classes.OverworldUI import OverworldUI
from classes.inventory import Item
from other.play_sound import play_sound
from other.settings import *
from datetime import datetime
from classes.camera import YSortCameraGroup
from classes.enemy import Enemy
from classes.player import Player, DustParticle
from classes.Tiles import StaticTile, AnimatedTile
from pytmx.util_pygame import load_pygame
from classes.states import BattleState, LevelState
from classes.UI import MenuBook, StatusBar


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

        self.overworld_ui = OverworldUI()

        self.player = None
        self.enemy_sprites = None
        self.open_menu = False
        self.menu = None
        self.current_music = None

        self.day_cycle_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
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


                Enemy(surf=obj.image, pos=pos, name=obj.name, group=(self.enemies, self.visible_sprites),
                      obstacle_sprites=self.obstacle_sprites)


        # === draw the ground items ===
        item_sprites = self.tmx_data.get_layer_by_name("Items")
        if isinstance(item_sprites, pytmx.TiledObjectGroup):
            for obj in item_sprites:
                pos = (obj.x, obj.y)

                Item(self.visible_sprites, obj.name, 1, pos)



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
                                     animation_speed=0.05)
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
                    self.menu = MenuBook(self.player)




                # enemy.name in the future

                # seperate this too

    def run(self) -> None:
        if self.visible_sprites.state == LevelState.OVERWORLD:
            self.update_soundtrack()
            self.overworld()
        else:
            self.update_soundtrack()
            self.battle()

    def battle_transition(self):
        if not self.visible_sprites.battle_participants:
            self.enemy_collision(self.player)
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

        # if not self.menu.running:

        self.visible_sprites.update()
        self.visible_sprites.draw_sprites()
        self.battle_transition()

        self.visible_sprites.update_camera(self.player)
        self.update_enemies(self.player)


        self.update_day_cycle()

        self.item_collision()

        for ally in self.player.current_allies:
            ally.hp_bar.draw(self.display_surface)
            self.player.hp_bar.draw(self.display_surface)

        self.visible_sprites.transition_screen()
        self.menu.draw(self.display_surface, )




    def update_day_cycle(self):
        day_phases = {
            5: {"color": (255,223,186), "opacity": 75},
            8: {"color": (255, 250, 240), "opacity": 75},
            12: {"color": (255, 255, 255), "opacity": 0},
            16: {"color": (255, 238, 131), "opacity": 75},
            18: {"color": (255, 174, 66), "opacity": 100},
            20: {"color": (34, 0, 51), "opacity": 150},
            22: {"color": (0, 0, 0), "opacity": 150},
            0: {"color": (0, 0, 0), "opacity": 150},

        }

        now = datetime.now().hour
        closest_time = 60
        for time in day_phases.keys():
            if abs(time - now) < abs(closest_time - now):
                closest_time = time

        current_phase = day_phases[16]
        self.day_cycle_overlay.set_alpha(current_phase["opacity"])

        self.day_cycle_overlay.fill(current_phase["color"])
        self.display_surface.blit(self.day_cycle_overlay, (0, 0))

    def battle(self):
        # Make camera follow the animation
        self.visible_sprites.animation_camera = self.visible_sprites.battle_loop.state

        # self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.draw_sprites()

        self.update_enemies(self.player)
        self.visible_sprites.update_camera(self.player)


        self.visible_sprites.battle_loop.run()
        self.visible_sprites.battle_loop.performer.spells.draw(self.display_surface)



        self.update_day_cycle()

        self.visible_sprites.battle_loop.draw_ui()
        self.visible_sprites.battle_loop.top_screen_description(self.display_surface)
        # use this smart ass
        # here to be drawn on top of the overlay

        # end battle
        self.overworld_transition()
        self.visible_sprites.transition_screen()

        if self.player.level_up_visual:
            self.player.level_up_visual.draw(self.display_surface)
            self.player.level_up_visual.update(self.player.hitbox.center - pygame.Vector2(int(self.visible_sprites.offset.x),
                                                       int(self.visible_sprites.offset.y)) - (0, 232))


    def item_collision(self):
        self.overworld_ui.item_message(self.display_surface)


        for item in self.visible_sprites.item_sprites:
            if self.player.hitbox.colliderect(item.rect):
                self.overworld_ui.show_pickup_prompt(self.display_surface, item)

                if self.overworld_ui.picked_up_item:
                    self.player.inventory.add(item)
                    item.fade_time = pygame.time.get_ticks() + 2000
                    self.player.item_sprites.add(item)
                    self.overworld_ui.picked_up_item = False
                    self.visible_sprites.remove(item)


    def update_enemies(self, player):
        """Updates all the enemy sprites based on the player's position."""
        for enemy in self.visible_sprites.enemy_sprites:
            enemy.update_enemy(player, self.display_surface, self.visible_sprites.offset)
            if not enemy.in_battle and enemy.death and pygame.time.get_ticks() >= enemy.respawn_time:
                enemy.hp = enemy.max_hp
                enemy.action = "idle"
                enemy.death = False
            if enemy.death and enemy.item_drop and not enemy.in_battle:
                item_pos = pygame.Vector2(enemy.hitbox.topleft) + (8, 0)
                Item(self.visible_sprites, enemy.item_drop, 1, item_pos)
                enemy.item_drop = None

            # test
            if not self.player.current_allies:
                self.player.current_allies.append(enemy.recruit())
                self.player.current_allies[0].hp_bar = StatusBar(self.player.current_allies[0], 28)





    def enemy_collision(self, player):
        self.enemy_sprites = [sprite for sprite in self.visible_sprites.get_visible_sprites() if sprite.type == "npc"]

        # checks all battle spots instead of just the visible ones
        for enemy in self.enemy_sprites:
            if player.hitbox.colliderect(enemy.hitbox) and pygame.time.get_ticks() >= player.post_battle_iframes:
                if enemy.occupation == "hero" or enemy.death:
                    continue

                else:
                    self.visible_sprites.battle_participants = {
                        "heroes": [player] + player.current_allies,
                        "enemies": [enemy]
                    }

                    # self.battle_participants = [player, enemy, enemy.clone((enemy.x, enemy.y))]
                    self.visible_sprites.transition_timer = pygame.time.get_ticks()
                    self.visible_sprites.delay = pygame.time.get_ticks() + self.visible_sprites.delay_time
                    for group in self.visible_sprites.battle_participants.values():
                        for participant in group:
                            participant.in_battle = True
                            participant.action = "idle"
                break




    def update_soundtrack(self):
        if not hasattr(self, 'current_music'):
            self.current_music = None

        if self.visible_sprites.state == LevelState.OVERWORLD and self.current_music != "forest":
            pygame.mixer.music.stop()
            pygame.mixer.music.load(FOREST_MUSIC)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)
            self.current_music = "forest"

        elif self.visible_sprites.state == LevelState.BATTLE:

            if not self.visible_sprites.battle_loop.state in [BattleState.END_MENU, BattleState.END_BATTLE]:
                if not self.current_music == "battle":
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(random.choice(BATTLE_MUSIC))
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
                    pygame.mixer.music.play(-1)
                    self.current_music = "battle"
            elif self.visible_sprites.battle_loop.winner and self.player in self.visible_sprites.battle_loop.winner:
                if not self.current_music == "victory":
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(random.choice(VICTORY_MUSIC))
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
                    pygame.mixer.music.play()
                    self.current_music = "victory"
            else:
                pygame.mixer.music.stop()

    def dust_particle(self):
        DustParticle(self.player, self.visible_sprites)


