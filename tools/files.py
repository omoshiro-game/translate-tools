from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union
from math import floor, ceil
from binary_file import ActedBinaryFile

@dataclass
class AnimationFrame:
    header: int = 0
    frame_index: int = 0
    display_time: int = 0
    exec_commands: int = 0
    unknown2: int = 0

@dataclass
class Animation:
    header: int = 0
    sample_list_index: int = 0
    sample_type: int = 0
    frame_start: int = 0
    strings_count: int = 0
    name: str = ""
    frames: List[AnimationFrame] = field(default_factory=list)

@dataclass
class AnimeSetElement:
    header: int = 0
    flying_offset: int = 0
    block_offset: int = 8
    invincibility_offset: int = 4
    unknown: int = 0
    name: str = ""
    animations: List[Animation] = field(default_factory=list)

@dataclass
class BmpCharaExcElement:
    header: int = 0
    is_name_same_path: int = 0
    is_giant: int = 0
    scale_mode: int = 1
    unknown: int = 2 # always 2 ??
    name: str = ""
    path: str = ""

@dataclass
class AnimeSetData:
    elements: List[AnimeSetElement] = field(default_factory=list)

@dataclass
class AnimeData:
    elements: List[Animation] = field(default_factory=list)


@dataclass
class BmpCharaExcData:
    elements: List[BmpCharaExcElement] = field(default_factory=list)

@dataclass
class PictureElement:
    header: int = 1 # always 1 ??
    is_name_same_path: int = 0
    unknown2: int = 2 # always 2 ??
    name: str = ""
    path: str = ""

@dataclass
class PictureData:
    elements: List[PictureElement] = field(default_factory=list)

@dataclass
class SoundElement:
    header: int = 1  # always 1 ??
    is_name_same_path: int = 0
    unknown2: int = 2  # always 2 ??
    name: str = ""
    path: str = ""

@dataclass
class SoundData:
    elements: List[SoundElement] = field(default_factory=list)

@dataclass
class CharaEffectElement:
    header: int = 0
    effect: int = 0
    param1: int = 0
    param2: int = 0
    param3: int = 0
    param4: int = 0
    param5: int = 0
    unknown: int = 1  # always 1?
    name: str = ""

@dataclass
class CharaEffectData:
    elements: List[CharaEffectElement] = field(default_factory=list)

@dataclass
class EffectAnimation:
    header: int = 2
    start: int = 0
    end: int = 0
    unknown: int = 0

@dataclass
class EffectElement:
    header: int = 0
    is_name_same_path: int = 0
    width: int = 0
    height: int = 0
    is_giant: int = 0
    unknown: int = 2  # always 2?
    name: str = ""
    path: str = ""
    animations: List[EffectAnimation] = field(default_factory=list)

@dataclass
class EffectData:
    elements: List[EffectElement] = field(default_factory=list)

@dataclass
class BgmElement:
    header: int = 2  # always 2?
    is_name_same_path: int = 0
    volume: int = 100
    unknown: int = 2  # always 2?
    name: str = ""
    path: str = ""

@dataclass
class BgmData:
    elements: List[BgmElement] = field(default_factory=list)

@dataclass
class SwordPosition:
    header: int = 2
    x: int = 0
    y: int = 0
    unknown1: int = 0
    unknown2: int = 0
    unknown3: int = 0
    unknown4: int = 0
    unknown5: int = 0
    width: int = 0
    height: int = 0
    index: int = 0
    unknown6: int = 0

@dataclass
class SwordTypeElement:
    header: int = 0
    is_name_same_path: int = 0
    unknown: int = 3  # always 3?
    name: str = ""
    path_left: str = ""
    path_right: str = ""
    positions: List[SwordPosition] = field(default_factory=list)

@dataclass
class SwordTypeData:
    elements: List[SwordTypeElement] = field(default_factory=list)

@dataclass
class ScreenEffectElement:
    header: int = 2
    effect: int = 0
    param1: int = 0
    param2: int = 0
    param3: int = 0
    param4: int = 0
    param5: int = 0
    unknown: int = 1  # always 1?
    name: str = ""

@dataclass
class ScreenEffectData:
    elements: List[ScreenEffectElement] = field(default_factory=list)

@dataclass
class WorldChip:
    header: int = 0
    tile_index: int = 0
    locked: int = 0
    graphic: int = 0
    strings_count: int = 2  # 2 - std::vector<std::string>
    name: str = ""
    unused_string: str = ""

@dataclass
class WorldEventPage:
    header: int = 0
    event_type: int = 0
    graphic: int = 0
    world_number: int = 0
    pass_without_clear: int = 0
    play_after_clear: int = 0
    on_game_clear: int = 0
    appearance_condition_world: int = 1  # 1
    appearance_condition_variable: int = 0  # dropdown
    appearance_condition_constant: int = 0  # spinner
    appearance_condition_comparison_content: int = 0  # small dropdown
    appearance_condition_total_score: int = 0
    variation_setting_present: int = 0
    variation_variable: int = 0
    variation_constant: int = 0
    strings_count: int = 2  # 2 - std::vector<std::string>
    world_name: str = ""  # std::string
    start_stage: str = ""  # std::string

@dataclass
class WorldEventBase:
    header: int = 0
    placement_x: int = 0
    placement_y: int = 0
    strings_count: int = 0  # 1 - std::vector<std::string>
    name: str = ""
    pages_count: int = 0
    pages: List[WorldEventPage] = field(default_factory=list)

@dataclass
class WorldMapData:
    width: int = 32
    height: int = 32
    init_x: int = 0
    init_y: int = 0
    background_index: int = 0
    use_background: int = 0
    chunk_width: int = 32  # 32, 64, 128 ...
    chunk_pow: int = 5   # 32:5, 64:6, 128:7 ... power of 2 ?
    strings_count: int = 2   # always 2?
    name: str = ""
    bg_path: str = ""
    tiles_types: List[WorldChip] = field(default_factory=list)
    tiles: List[int] = field(default_factory=list)
    events: List[WorldEventBase] = field(default_factory=list)
    events_pal: List[WorldEventBase] = field(default_factory=list)

class AnimeSet(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = AnimeSetData()
        
    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            anim_set_count = self.read_u32()
            
            for _ in range(anim_set_count):
                element = AnimeSetElement()
                element.header = self.read_u32()
                element.invincibility_offset = self.read_u32()
                element.block_offset = self.read_u32()
                element.flying_offset = self.read_u32()
                element.unknown = self.read_u32()
                
                name_length = self.read_u32()
                element.name = self.read_str(name_length)
                
                animation_count = self.read_u32()
                for _ in range(animation_count):
                    anim = Animation()
                    anim.header = self.read_u32()
                    anim.sample_list_index = self.read_u16()
                    anim.sample_type = self.read_u8()
                    anim.frame_start = self.read_u16()
                    anim.strings_count = self.read_u32()
                    
                    name_length = self.read_u32()
                    anim.name = self.read_str(name_length)
                    
                    frame_count = self.read_u32()
                    for _ in range(frame_count):
                        frame = AnimationFrame()
                        frame.header = self.read_u32()
                        frame.frame_index = self.read_u32()
                        frame.display_time = self.read_u32()
                        frame.exec_commands = self.read_u32()
                        frame.unknown2 = self.read_u32()
                        anim.frames.append(frame)
                        
                    element.animations.append(anim)
                    
                self.data.elements.append(element)
                
            return True
            
        except Exception as e:
            print(f"Error parsing AnimeSet: {e}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        self.write_u32(self.version)
        self.write_u32(len(self.data.elements))

        for element in self.data.elements:
            self.write_u32(element.header)
            self.write_u32(element.invincibility_offset)
            self.write_u32(element.block_offset)
            self.write_u32(element.flying_offset)
            self.write_u32(1)

            self.write_std_string(element.name)

            self.write_u32(len(element.animations))
            for anim in element.animations:
                self.write_u32(anim.header)
                self.write_u16(anim.sample_list_index)
                self.write_u8(anim.sample_type)
                self.write_u16(anim.frame_start)
                self.write_u32(1) # anim.strings_count

                self.write_std_string(anim.name)
                
                self.write_u32(len(anim.frames))
                for frame in anim.frames:
                    self.write_u32(frame.header)
                    self.write_u32(frame.frame_index)
                    self.write_u32(frame.display_time)
                    self.write_u32(frame.exec_commands)
                    self.write_u32(frame.unknown2)
        
        return self._data


SYSTEM_TARGET_KEYS = [
    "target_graphic",
    "target_base_anim_set",
    "target_z_coordinate",
    "target_transparency",
    "target_character_fx",
    "target_direction_fix",
    "target_flight",
    "target_invincibility",
    "target_giant_form",
    "target_sync_autoscroll",
    "target_fow",
    "target_remain_hp",
    "target_remain_sp",
    "target_max_hp",
    "target_max_sp",
    "target_col_hitbox",
    "target_col_power",
    "target_col_shock",
    "target_defense",
    "target_shock_resist",
    "target_inertia",
    "target_action",
    "target_remain_time",
    "target_player_count",
    "target_bgm",
]

SYSTEM_TARGET_RESET_KEYS = [
    "target_graphic_reseted",
    "target_base_anim_set_reseted",
    "target_z_coordinate_reseted",
    "target_transparency_reseted",
    "target_character_fx_reseted",
    "target_direction_fix_reseted",
    "target_flight_reseted",
    "target_invincibility_reseted",
    "target_giant_form_reseted",
    "target_sync_autoscroll_reseted",
    "target_fow_reseted",
    "target_remain_hp_reseted",
    "target_remain_sp_reseted",
    "target_max_hp_reseted",
    "target_max_sp_reseted",
    "target_col_hitbox_reseted",
    "target_col_power_reseted",
    "target_col_shock_reseted",
    "target_defense_reseted",
    "target_shock_resist_reseted",
    "target_inertia_reseted",
    "target_action_reseted",
    "target_remain_time_reseted",
    "target_player_count_reseted",
    "target_bgm_reseted",
]

@dataclass
class StatusWindowData:
    header: int = 0
    is_visible: int = 0
    show_symbol: int = 0
    max: int = 0
    unk1: int = 0
    color_change_condition: int = 0
    change_operator: int = 0
    strings_count: int = 0
    text: str = ""


@dataclass
class RankingData:
    first_unk: int = 0
    ranking_on: int = 0
    second_unk: int = 0
    ranking_count: int = 0
    ranking_criterias: List[int] = field(default_factory=list)


@dataclass
class MenuTextData:
    unk1: int = 0
    enabled: int = 0
    unk2: int = 0
    text: str = ""


@dataclass
class IniConfData:
    unk1: int = 0
    unk2: int = 0
    default_value: int = 0
    string_count: int = 0
    id_string: str = ""
    default_str: str = ""


@dataclass
class SystemTargets:
    count: int = 0
    target_graphic: int = 0
    target_base_anim_set: int = 0
    target_z_coordinate: int = 0
    target_transparency: int = 0
    target_character_fx: int = 0
    target_direction_fix: int = 0
    target_flight: int = 0
    target_invincibility: int = 0
    target_giant_form: int = 0
    target_sync_autoscroll: int = 0
    target_fow: int = 0
    target_remain_hp: int = 0
    target_remain_sp: int = 0
    target_max_hp: int = 0
    target_max_sp: int = 0
    target_col_hitbox: int = 0
    target_col_power: int = 0
    target_col_shock: int = 0
    target_defense: int = 0
    target_shock_resist: int = 0
    target_inertia: int = 0
    target_action: int = 0
    target_remain_time: int = 0
    target_player_count: int = 0
    target_bgm: int = 0


@dataclass
class SystemTargetsReset:
    count: int = 0
    target_graphic_reseted: int = 0
    target_base_anim_set_reseted: int = 0
    target_z_coordinate_reseted: int = 0
    target_transparency_reseted: int = 0
    target_character_fx_reseted: int = 0
    target_direction_fix_reseted: int = 0
    target_flight_reseted: int = 0
    target_invincibility_reseted: int = 0
    target_giant_form_reseted: int = 0
    target_sync_autoscroll_reseted: int = 0
    target_fow_reseted: int = 0
    target_remain_hp_reseted: int = 0
    target_remain_sp_reseted: int = 0
    target_max_hp_reseted: int = 0
    target_max_sp_reseted: int = 0
    target_col_hitbox_reseted: int = 0
    target_col_power_reseted: int = 0
    target_col_shock_reseted: int = 0
    target_defense_reseted: int = 0
    target_shock_resist_reseted: int = 0
    target_inertia_reseted: int = 0
    target_action_reseted: int = 0
    target_remain_time_reseted: int = 0
    target_player_count_reseted: int = 0
    target_bgm_reseted: int = 0

@dataclass
class SystemData:
    unk0: int = 0
    up_process_on_stage_clear: int = 0
    score_per_1up: int = 0
    space_pause: int = 0
    hide_obj_pause: int = 0
    show_symbol_image: int = 0
    font_index: int = 0
    decoration: int = 0
    monospace: int = 0
    min_damage_reduct_base: int = 0
    min_damage_reduct_percent: int = 0
    min_shock_reduct_base: int = 0
    min_shock_reduct_percent: int = 0
    enable_test_play_everywhere: int = 0
    character_draw: int = 0
    allow_replay_save: int = 0
    alow_manual_replay_save: int = 0
    replay_file_format: int = 0
    use_explorer_file_dialog_for_file_select: int = 0
    show_image_on_title_screen: int = 0
    auto_save_default: int = 0
    show_description: int = 0
    share_lives_across_story: int = 0
    return_worldmap_on_death: int = 0
    show_lives_on_worldmap: int = 0
    multistage_autosave_after_each_stage: int = 0
    challenge_mode_world: int = 0
    all_worlds_selectable_on_start: int = 0
    show_highscore: int = 0
    show_totalscore: int = 0
    always_reset_commonvar_on_worldmap: int = 0
    retry_pause_menu_option_in_cleared_worlds: int = 0
    challenge_show_highscore: int = 0
    challenge_show_totalscore: int = 0
    challenge_death_reset_commonvar: int = 0
    challenge_retry_pause_menu_option_in_cleared_worlds: int = 0
    freemode_death_reset_commonvar: int = 0
    testplay_death_reset_commonvar: int = 0
    bitmap_color_mode: int = 0
    transparent_color_r: int = 0
    transparent_color_g: int = 0
    transparent_color_b: int = 0
    compat_v2_12: int = 0
    compat_v2_60: int = 0
    play_death_for_stauts_and_code_exec: int = 0
    play_invincibility_effect: int = 0
    invincibility_effect_speed: int = 0
    enable_color_invincible_anim: int = 0
    return_to_map_pause_menu_option: int = 0
    compat_v5_23: int = 0
    compat_v5_54: int = 0
    compat_v6_16: int = 0
    compat_v6_68: int = 0
    compat_v6_76: int = 0
    compat_v6_94: int = 0
    unk_compat_alwayson: int = 0
    compat_v6_96: int = 0
    compat_v7_20: int = 0
    compat_v7_22: int = 0
    compat_v7_32: int = 0
    compat_v7_34: int = 0
    compat_v7_47: int = 0
    compat_v7_51: int = 0
    compat_v7_59: int = 0
    compat_v7_47_nofx: int = 0
    compat_v7_47_linfx: int = 0
    compat_v7_72: int = 0
    compat_v7_80: int = 0
    compat_v7_81: int = 0
    compat_v7_82: int = 0
    compat_v7_92: int = 0
    compat_v8_04: int = 0
    compat_v8_07: int = 0
    compat_v8_16: int = 0
    compat_v8_17: int = 0
    compat_v8_18: int = 0
    compat_v8_21: int = 0
    compat_v8_25: int = 0
    compat_v8_29: int = 0
    compat_v8_32: int = 0
    compat_v8_36: int = 0
    compat_v8_37: int = 0
    compat_v8_40: int = 0
    compat_v8_44_higherjump: int = 0
    compat_v8_44_delayedjump: int = 0
    compat_v8_44_lowerjump: int = 0
    compat_v8_44_detach_riders: int = 0
    compat_v8_60: int = 0
    compat_v8_73: int = 0
    compat_v8_90_wrap: int = 0
    compat_v8_90_statuscode: int = 0
    compat_v8_90_walkerY: int = 0
    compat_v8_96: int = 0
    compat_v9_03: int = 0
    compat_v9_11: int = 0
    compat_v9_12: int = 0
    compat_v9_80: int = 0
    compat_v9_85: int = 0
    direct3_color_depth: int = 0
    directdraw_color_depth: int = 0
    go_title_after_stage_clear: int = 0
    strings_count: int = 0
    game_title: str = ""
    description: str = ""
    targets: SystemTargets = field(default_factory=SystemTargets)
    targets_reseted: SystemTargetsReset = field(default_factory=SystemTargetsReset)
    status_window_count: int = 0
    status_windows: List[StatusWindowData] = field(default_factory=list)
    header_initial: int = 0
    story_mode_initial: int = 0
    challenge_mode_initial: int = 0
    free_mode_initial: int = 0
    free_mode_max: int = 0
    header_infinite: int = 0
    story_mode_infinite: int = 0
    challenge_mode_infinite: int = 0
    free_mode_infinite: int = 0
    free_mode_infini_max: int = 0
    rankings_count: int = 0
    rankings: List[RankingData] = field(default_factory=list)
    terms_strings_count: int = 0
    terms: List[str] = field(default_factory=list)
    sound_effect_count: int = 0
    sound_effect_paths: List[str] = field(default_factory=list)
    bgm_count: int = 0
    bgm_values: List[int] = field(default_factory=list)
    bgm_loop_play_count: int = 0
    bgm_loop_play: List[int] = field(default_factory=list)
    title_menu_texts_count: int = 0
    title_menu_texts: List[MenuTextData] = field(default_factory=list)
    worldmap_menu_count: int = 0
    worldmap_menu_texts: List[MenuTextData] = field(default_factory=list)
    option_menu_count: int = 0
    option_menu_texts: List[MenuTextData] = field(default_factory=list)
    ranking_entry_count: int = 0
    ranking_entry_texts: List[str] = field(default_factory=list)
    autoreplay_save_count: int = 0
    autoreplay_save_texts: List[str] = field(default_factory=list)
    replay_order_count: int = 0
    replay_order_texts: List[str] = field(default_factory=list)
    settings_ini_count: int = 0
    setting_init: List[IniConfData] = field(default_factory=list)

class System(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = SystemData()
        self.magic = 0
        
    def parse(self) -> bool:
        if not self.load():
            return False
        try:
            self.magic = self.read_u32()

            data = self.data
            data.unk0 = self.read_u32()
            data.up_process_on_stage_clear = self.read_u32()
            data.score_per_1up = self.read_u32()
            data.space_pause = self.read_u32()
            data.hide_obj_pause = self.read_u32()
            data.show_symbol_image = self.read_u32()
            data.font_index = self.read_u32()
            data.decoration = self.read_u32()
            data.monospace = self.read_u32()
            data.min_damage_reduct_base = self.read_u32()
            data.min_damage_reduct_percent = self.read_u32()
            data.min_shock_reduct_base = self.read_u32()
            data.min_shock_reduct_percent = self.read_u32()
            data.enable_test_play_everywhere = self.read_u32()
            data.character_draw = self.read_u32()
            data.allow_replay_save = self.read_u32()
            data.alow_manual_replay_save = self.read_u32()
            data.replay_file_format = self.read_u32()
            data.use_explorer_file_dialog_for_file_select = self.read_u32()
            data.show_image_on_title_screen = self.read_u32()
            data.auto_save_default = self.read_u32()
            data.show_description = self.read_u32()
            data.share_lives_across_story = self.read_u32()
            data.return_worldmap_on_death = self.read_u32()
            data.show_lives_on_worldmap = self.read_u32()
            data.multistage_autosave_after_each_stage = self.read_u32()
            data.challenge_mode_world = self.read_u32()
            data.all_worlds_selectable_on_start = self.read_u32()
            data.show_highscore = self.read_u32()
            data.show_totalscore = self.read_u32()
            data.always_reset_commonvar_on_worldmap = self.read_u32()
            data.retry_pause_menu_option_in_cleared_worlds = self.read_u32()
            data.challenge_show_highscore = self.read_u32()
            data.challenge_show_totalscore = self.read_u32()
            data.challenge_death_reset_commonvar = self.read_u32()
            data.challenge_retry_pause_menu_option_in_cleared_worlds = self.read_u32()
            data.freemode_death_reset_commonvar = self.read_u32()
            data.testplay_death_reset_commonvar = self.read_u32()
            data.bitmap_color_mode = self.read_u32()
            data.transparent_color_r = self.read_u8()
            data.transparent_color_g = self.read_u8()
            data.transparent_color_b = self.read_u8()
            data.compat_v2_12 = self.read_u32()
            data.compat_v2_60 = self.read_u32()
            data.play_death_for_stauts_and_code_exec = self.read_u32()
            data.play_invincibility_effect = self.read_u32()
            data.invincibility_effect_speed = self.read_u32()
            data.enable_color_invincible_anim = self.read_u32()
            data.return_to_map_pause_menu_option = self.read_u32()
            data.compat_v5_23 = self.read_u32()
            data.compat_v5_54 = self.read_u32()
            data.compat_v6_16 = self.read_u32()
            data.compat_v6_68 = self.read_u32()
            data.compat_v6_76 = self.read_u32()
            data.compat_v6_94 = self.read_u32()
            data.unk_compat_alwayson = self.read_u32()
            data.compat_v6_96 = self.read_u32()
            data.compat_v7_20 = self.read_u32()
            data.compat_v7_22 = self.read_u32()
            data.compat_v7_32 = self.read_u32()
            data.compat_v7_34 = self.read_u32()
            data.compat_v7_47 = self.read_u32()
            data.compat_v7_51 = self.read_u32()
            data.compat_v7_59 = self.read_u32()
            data.compat_v7_47_nofx = self.read_u32()
            data.compat_v7_47_linfx = self.read_u32()
            data.compat_v7_72 = self.read_u32()
            data.compat_v7_80 = self.read_u32()
            data.compat_v7_81 = self.read_u32()
            data.compat_v7_82 = self.read_u32()
            data.compat_v7_92 = self.read_u32()
            data.compat_v8_04 = self.read_u32()
            data.compat_v8_07 = self.read_u32()
            data.compat_v8_16 = self.read_u32()
            data.compat_v8_17 = self.read_u32()
            data.compat_v8_18 = self.read_u32()
            data.compat_v8_21 = self.read_u32()
            data.compat_v8_25 = self.read_u32()
            data.compat_v8_29 = self.read_u32()
            data.compat_v8_32 = self.read_u32()
            data.compat_v8_36 = self.read_u32()
            data.compat_v8_37 = self.read_u32()
            data.compat_v8_40 = self.read_u32()
            data.compat_v8_44_higherjump = self.read_u32()
            data.compat_v8_44_delayedjump = self.read_u32()
            data.compat_v8_44_lowerjump = self.read_u32()
            data.compat_v8_44_detach_riders = self.read_u32()
            data.compat_v8_60 = self.read_u32()
            data.compat_v8_73 = self.read_u32()
            data.compat_v8_90_wrap = self.read_u32()
            data.compat_v8_90_statuscode = self.read_u32()
            data.compat_v8_90_walkerY = self.read_u32()
            data.compat_v8_96 = self.read_u32()
            data.compat_v9_03 = self.read_u32()
            data.compat_v9_11 = self.read_u32()
            data.compat_v9_12 = self.read_u32()
            data.compat_v9_80 = self.read_u32()
            data.compat_v9_85 = self.read_u32()
            data.direct3_color_depth = self.read_u32()
            data.directdraw_color_depth = self.read_u32()
            data.go_title_after_stage_clear = self.read_u32()
            data.strings_count = self.read_u32()
            data.game_title = self.read_std_string()
            data.description = self.read_std_string()

            data.targets.count = self.read_u32()
            for key in SYSTEM_TARGET_KEYS:
                setattr(data.targets, key, self.read_u8())

            data.targets_reseted.count = self.read_u32()
            for key in SYSTEM_TARGET_RESET_KEYS:
                setattr(data.targets_reseted, key, self.read_u8())

            data.status_window_count = self.read_u32()
            data.status_windows = []
            for _ in range(data.status_window_count):
                window = StatusWindowData()
                window.header = self.read_u32()
                window.is_visible = self.read_u32()
                window.show_symbol = self.read_u32()
                window.max = self.read_u32()
                window.unk1 = self.read_u32()
                window.color_change_condition = self.read_u32()
                window.change_operator = self.read_u32()
                window.strings_count = self.read_u32()
                window.text = self.read_std_string()
                data.status_windows.append(window)

            data.header_initial = self.read_u32()
            data.story_mode_initial = self.read_u32()
            data.challenge_mode_initial = self.read_u32()
            data.free_mode_initial = self.read_u32()
            data.free_mode_max = self.read_u32()

            data.header_infinite = self.read_u32()
            data.story_mode_infinite = self.read_u32()
            data.challenge_mode_infinite = self.read_u32()
            data.free_mode_infinite = self.read_u32()
            data.free_mode_infini_max = self.read_u32()

            data.rankings_count = self.read_u32()
            data.rankings = []
            for _ in range(data.rankings_count):
                ranking = RankingData()
                ranking.first_unk = self.read_u32()
                ranking.ranking_on = self.read_u32()
                ranking.second_unk = self.read_u32()
                ranking.ranking_count = self.read_u32()
                ranking.ranking_criterias = [self.read_u8() for _ in range(ranking.ranking_count)]
                data.rankings.append(ranking)

            data.terms_strings_count = self.read_u32()
            data.terms = [self.read_std_string() for _ in range(data.terms_strings_count)]

            data.sound_effect_count = self.read_u32()
            data.sound_effect_paths = [self.read_std_string() for _ in range(data.sound_effect_count)]

            data.bgm_count = self.read_u32()
            data.bgm_values = [self.read_u32() for _ in range(data.bgm_count)]

            data.bgm_loop_play_count = self.read_u32()
            data.bgm_loop_play = [self.read_u8() for _ in range(data.bgm_loop_play_count)]

            data.title_menu_texts_count = self.read_u32()
            data.title_menu_texts = []
            for _ in range(data.title_menu_texts_count):
                menu_text = MenuTextData()
                menu_text.unk1 = self.read_u32()
                menu_text.enabled = self.read_u32()
                menu_text.unk2 = self.read_u32()
                menu_text.text = self.read_std_string()
                data.title_menu_texts.append(menu_text)

            data.worldmap_menu_count = self.read_u32()
            data.worldmap_menu_texts = []
            for _ in range(data.worldmap_menu_count):
                menu_text = MenuTextData()
                menu_text.unk1 = self.read_u32()
                menu_text.enabled = self.read_u32()
                menu_text.unk2 = self.read_u32()
                menu_text.text = self.read_std_string()
                data.worldmap_menu_texts.append(menu_text)

            data.option_menu_count = self.read_u32()
            data.option_menu_texts = []
            for _ in range(data.option_menu_count):
                menu_text = MenuTextData()
                menu_text.unk1 = self.read_u32()
                menu_text.enabled = self.read_u32()
                menu_text.unk2 = self.read_u32()
                menu_text.text = self.read_std_string()
                data.option_menu_texts.append(menu_text)

            data.ranking_entry_count = self.read_u32()
            data.ranking_entry_texts = [self.read_std_string() for _ in range(data.ranking_entry_count)]

            data.autoreplay_save_count = self.read_u32()
            data.autoreplay_save_texts = [self.read_std_string() for _ in range(data.autoreplay_save_count)]

            data.replay_order_count = self.read_u32()
            data.replay_order_texts = [self.read_std_string() for _ in range(data.replay_order_count)]

            data.settings_ini_count = self.read_u32()
            data.setting_init = []
            for _ in range(data.settings_ini_count):
                conf = IniConfData()
                conf.unk1 = self.read_u32()
                conf.unk2 = self.read_u32()
                conf.default_value = self.read_u32()
                conf.string_count = self.read_u32()
                conf.id_string = self.read_std_string()
                conf.default_str = self.read_std_string()
                data.setting_init.append(conf)

            return True

        except Exception as error:
            print(f"Error parsing System.dat: {error}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        data = self.data
        self.write_u32(self.magic)
        self.write_u32(data.unk0)
        self.write_u32(data.up_process_on_stage_clear)
        self.write_u32(data.score_per_1up)
        self.write_u32(data.space_pause)
        self.write_u32(data.hide_obj_pause)
        self.write_u32(data.show_symbol_image)
        self.write_u32(data.font_index)
        self.write_u32(data.decoration)
        self.write_u32(data.monospace)
        self.write_u32(data.min_damage_reduct_base)
        self.write_u32(data.min_damage_reduct_percent)
        self.write_u32(data.min_shock_reduct_base)
        self.write_u32(data.min_shock_reduct_percent)
        self.write_u32(data.enable_test_play_everywhere)
        self.write_u32(data.character_draw)
        self.write_u32(data.allow_replay_save)
        self.write_u32(data.alow_manual_replay_save)
        self.write_u32(data.replay_file_format)
        self.write_u32(data.use_explorer_file_dialog_for_file_select)
        self.write_u32(data.show_image_on_title_screen)
        self.write_u32(data.auto_save_default)
        self.write_u32(data.show_description)
        self.write_u32(data.share_lives_across_story)
        self.write_u32(data.return_worldmap_on_death)
        self.write_u32(data.show_lives_on_worldmap)
        self.write_u32(data.multistage_autosave_after_each_stage)
        self.write_u32(data.challenge_mode_world)
        self.write_u32(data.all_worlds_selectable_on_start)
        self.write_u32(data.show_highscore)
        self.write_u32(data.show_totalscore)
        self.write_u32(data.always_reset_commonvar_on_worldmap)
        self.write_u32(data.retry_pause_menu_option_in_cleared_worlds)
        self.write_u32(data.challenge_show_highscore)
        self.write_u32(data.challenge_show_totalscore)
        self.write_u32(data.challenge_death_reset_commonvar)
        self.write_u32(data.challenge_retry_pause_menu_option_in_cleared_worlds)
        self.write_u32(data.freemode_death_reset_commonvar)
        self.write_u32(data.testplay_death_reset_commonvar)
        self.write_u32(data.bitmap_color_mode)
        self.write_u8(data.transparent_color_r)
        self.write_u8(data.transparent_color_g)
        self.write_u8(data.transparent_color_b)
        self.write_u32(data.compat_v2_12)
        self.write_u32(data.compat_v2_60)
        self.write_u32(data.play_death_for_stauts_and_code_exec)
        self.write_u32(data.play_invincibility_effect)
        self.write_u32(data.invincibility_effect_speed)
        self.write_u32(data.enable_color_invincible_anim)
        self.write_u32(data.return_to_map_pause_menu_option)
        self.write_u32(data.compat_v5_23)
        self.write_u32(data.compat_v5_54)
        self.write_u32(data.compat_v6_16)
        self.write_u32(data.compat_v6_68)
        self.write_u32(data.compat_v6_76)
        self.write_u32(data.compat_v6_94)
        self.write_u32(data.unk_compat_alwayson)
        self.write_u32(data.compat_v6_96)
        self.write_u32(data.compat_v7_20)
        self.write_u32(data.compat_v7_22)
        self.write_u32(data.compat_v7_32)
        self.write_u32(data.compat_v7_34)
        self.write_u32(data.compat_v7_47)
        self.write_u32(data.compat_v7_51)
        self.write_u32(data.compat_v7_59)
        self.write_u32(data.compat_v7_47_nofx)
        self.write_u32(data.compat_v7_47_linfx)
        self.write_u32(data.compat_v7_72)
        self.write_u32(data.compat_v7_80)
        self.write_u32(data.compat_v7_81)
        self.write_u32(data.compat_v7_82)
        self.write_u32(data.compat_v7_92)
        self.write_u32(data.compat_v8_04)
        self.write_u32(data.compat_v8_07)
        self.write_u32(data.compat_v8_16)
        self.write_u32(data.compat_v8_17)
        self.write_u32(data.compat_v8_18)
        self.write_u32(data.compat_v8_21)
        self.write_u32(data.compat_v8_25)
        self.write_u32(data.compat_v8_29)
        self.write_u32(data.compat_v8_32)
        self.write_u32(data.compat_v8_36)
        self.write_u32(data.compat_v8_37)
        self.write_u32(data.compat_v8_40)
        self.write_u32(data.compat_v8_44_higherjump)
        self.write_u32(data.compat_v8_44_delayedjump)
        self.write_u32(data.compat_v8_44_lowerjump)
        self.write_u32(data.compat_v8_44_detach_riders)
        self.write_u32(data.compat_v8_60)
        self.write_u32(data.compat_v8_73)
        self.write_u32(data.compat_v8_90_wrap)
        self.write_u32(data.compat_v8_90_statuscode)
        self.write_u32(data.compat_v8_90_walkerY)
        self.write_u32(data.compat_v8_96)
        self.write_u32(data.compat_v9_03)
        self.write_u32(data.compat_v9_11)
        self.write_u32(data.compat_v9_12)
        self.write_u32(data.compat_v9_80)
        self.write_u32(data.compat_v9_85)
        self.write_u32(data.direct3_color_depth)
        self.write_u32(data.directdraw_color_depth)
        self.write_u32(data.go_title_after_stage_clear)
        self.write_u32(data.strings_count)
        self.write_std_string(data.game_title)
        self.write_std_string(data.description)

        self.write_u32(data.targets.count)
        for key in SYSTEM_TARGET_KEYS:
            self.write_u8(getattr(data.targets, key))

        self.write_u32(data.targets_reseted.count)
        for key in SYSTEM_TARGET_RESET_KEYS:
            self.write_u8(getattr(data.targets_reseted, key))

        self.write_u32(len(data.status_windows))
        for window in data.status_windows:
            self.write_u32(window.header)
            self.write_u32(window.is_visible)
            self.write_u32(window.show_symbol)
            self.write_u32(window.max)
            self.write_u32(window.unk1)
            self.write_u32(window.color_change_condition)
            self.write_u32(window.change_operator)
            self.write_u32(window.strings_count)
            self.write_std_string(window.text)

        self.write_u32(data.header_initial)
        self.write_u32(data.story_mode_initial)
        self.write_u32(data.challenge_mode_initial)
        self.write_u32(data.free_mode_initial)
        self.write_u32(data.free_mode_max)
        self.write_u32(data.header_infinite)
        self.write_u32(data.story_mode_infinite)
        self.write_u32(data.challenge_mode_infinite)
        self.write_u32(data.free_mode_infinite)
        self.write_u32(data.free_mode_infini_max)

        self.write_u32(len(data.rankings))
        for ranking in data.rankings:
            self.write_u32(ranking.first_unk)
            self.write_u32(ranking.ranking_on)
            self.write_u32(ranking.second_unk)
            self.write_u32(len(ranking.ranking_criterias))
            for criteria in ranking.ranking_criterias:
                self.write_u8(criteria)

        self.write_u32(len(data.terms))
        for term in data.terms:
            self.write_std_string(term)

        self.write_u32(len(data.sound_effect_paths))
        for path in data.sound_effect_paths:
            self.write_std_string(path)

        self.write_u32(len(data.bgm_values))
        for value in data.bgm_values:
            self.write_u32(value)

        self.write_u32(len(data.bgm_loop_play))
        for loop in data.bgm_loop_play:
            self.write_u8(loop)

        self.write_u32(len(data.title_menu_texts))
        for menu_text in data.title_menu_texts:
            self.write_u32(menu_text.unk1)
            self.write_u32(menu_text.enabled)
            self.write_u32(menu_text.unk2)
            self.write_std_string(menu_text.text)

        self.write_u32(len(data.worldmap_menu_texts))
        for menu_text in data.worldmap_menu_texts:
            self.write_u32(menu_text.unk1)
            self.write_u32(menu_text.enabled)
            self.write_u32(menu_text.unk2)
            self.write_std_string(menu_text.text)

        self.write_u32(len(data.option_menu_texts))
        for menu_text in data.option_menu_texts:
            self.write_u32(menu_text.unk1)
            self.write_u32(menu_text.enabled)
            self.write_u32(menu_text.unk2)
            self.write_std_string(menu_text.text)

        self.write_u32(len(data.ranking_entry_texts))
        for text in data.ranking_entry_texts:
            self.write_std_string(text)

        self.write_u32(len(data.autoreplay_save_texts))
        for text in data.autoreplay_save_texts:
            self.write_std_string(text)

        self.write_u32(len(data.replay_order_texts))
        for text in data.replay_order_texts:
            self.write_std_string(text)

        self.write_u32(len(data.setting_init))
        for conf in data.setting_init:
            self.write_u32(conf.unk1)
            self.write_u32(conf.unk2)
            self.write_u32(conf.default_value)
            self.write_u32(conf.string_count)
            self.write_std_string(conf.id_string)
            self.write_std_string(conf.default_str)

        return self._data

@dataclass
class GValInfoData:
    pass  # TODO: Add fields

class GValInfo(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = GValInfoData()
        
    def parse(self) -> bool:
        if not self.load():
            return False
        # TODO: Implement parsing
        return True

# Add more stub classes for other .dat files
class Anime(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = AnimeData()
    
    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            anim_count = self.read_u32()
            
            for _ in range(anim_count):
                anim = Animation()
                anim.header = self.read_u32()
                anim.sample_list_index = self.read_u16()
                anim.sample_type = self.read_u8()
                anim.frame_start = self.read_u16()
                anim.strings_count = self.read_u32()
                
                name_length = self.read_u32()
                anim.name = self.read_str(name_length)
                
                frame_count = self.read_u32()
                for _ in range(frame_count):
                    frame = AnimationFrame()
                    frame.header = self.read_u32()
                    frame.frame_index = self.read_u32()
                    frame.display_time = self.read_u32()
                    frame.exec_commands = self.read_u32()
                    frame.unknown2 = self.read_u32()
                    anim.frames.append(frame)
                    
                self.data.elements.append(anim)
                
            return True
            
        except Exception as e:
            print(f"Error parsing Anime: {e}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        self.write_u32(self.version)
        self.write_u32(len(self.data.elements))

        for anim in self.data.elements:
            self.write_u32(anim.header)
            self.write_u16(anim.sample_list_index)
            self.write_u8(anim.sample_type)
            self.write_u16(anim.frame_start)
            self.write_u32(1) # anim.strings_count)

            self.write_std_string(anim.name)
            
            self.write_u32(len(anim.frames))
            for frame in anim.frames:
                self.write_u32(frame.header)
                self.write_u32(frame.frame_index)
                self.write_u32(frame.display_time)
                self.write_u32(frame.exec_commands)
                self.write_u32(frame.unknown2)
        
        return self._data

class BmpCharaExc(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = BmpCharaExcData()
    
    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            bmp_set_count = self.read_u32()
            
            for _ in range(bmp_set_count):
                element = BmpCharaExcElement()
                element.header = self.read_u32() # should be 3
                element.is_name_same_path = self.read_u32()
                element.is_giant = self.read_u32()
                element.scale_mode = self.read_u32()
                element.unknown = self.read_u32()

                name_length = self.read_u32()
                if name_length > 1:
                    element.name = self.read_str(name_length)
                
                path_length = self.read_u32()
                if path_length > 1:
                    element.path = self.read_str(path_length)
                    
                self.data.elements.append(element)
                
            return True
            
        except Exception as e:
            print(f"Error parsing AnimeSet: {e}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        self.write_u32(self.version)
        self.write_u32(len(self.data.elements))

        for element in self.data.elements:
            self.write_u32(element.header)
            self.write_u32(element.is_name_same_path)
            self.write_u32(element.is_giant)
            self.write_u32(element.scale_mode)
            self.write_u32(2) # element.unknown)
            self.write_std_string(element.name)
            self.write_std_string(element.path)

        return self._data

class SwordType(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = SwordTypeData()
    
    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            element_count = self.read_u32()
            
            for _ in range(element_count):
                element = SwordTypeElement()
                element.header = self.read_u32()
                element.is_name_same_path = self.read_u32()
                element.unknown = self.read_u32()

                name_length = self.read_u32()
                if name_length > 1:
                    element.name = self.read_str(name_length)
                    
                path_left_length = self.read_u32()
                if path_left_length > 1:
                    element.path_left = self.read_str(path_left_length)
                    
                path_right_length = self.read_u32()
                if path_right_length > 1:
                    element.path_right = self.read_str(path_right_length)
                    
                pos_count = self.read_u32()
                for _ in range(pos_count):
                    pos = SwordPosition()
                    pos.header = self.read_u32()
                    pos.x = self.read_s32()
                    pos.y = self.read_s32()
                    pos.unknown1 = self.read_u32()
                    pos.unknown2 = self.read_u32()
                    pos.unknown3 = self.read_u32()
                    pos.unknown4 = self.read_u32()
                    pos.unknown5 = self.read_u32()
                    pos.width = self.read_u32()
                    pos.height = self.read_u32()
                    pos.index = self.read_u32()
                    pos.unknown6 = self.read_u32()
                    element.positions.append(pos)
                    
                self.data.elements.append(element)
                
            return True
            
        except Exception as e:
            print(f"Error parsing SwordType: {e}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        self.write_u32(self.version)
        self.write_u32(len(self.data.elements))

        for element in self.data.elements:
            self.write_u32(element.header)
            self.write_u32(element.is_name_same_path)
            self.write_u32(3) # element.unknown)
            self.write_std_string(element.name)
            self.write_std_string(element.path_left)
            self.write_std_string(element.path_right)

            self.write_u32(len(element.positions))
            for pos in element.positions:
                self.write_u32(pos.header)
                self.write_s32(pos.x)
                self.write_s32(pos.y)
                self.write_u32(pos.unknown1)
                self.write_u32(pos.unknown2)
                self.write_u32(pos.unknown3)
                self.write_u32(pos.unknown4)
                self.write_u32(pos.unknown5)
                self.write_u32(pos.width)
                self.write_u32(pos.height)
                self.write_u32(pos.index)
                self.write_u32(pos.unknown6)
        
        return self._data

class Effect(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = EffectData()
    
    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            anim_set_count = self.read_u32()
            
            for _ in range(anim_set_count):
                element = EffectElement()
                element.header = self.read_u32()
                element.is_name_same_path = self.read_u32()
                element.width = self.read_u32()
                element.height = self.read_u32()
                element.is_giant = self.read_u32()
                element.unknown = self.read_u32()

                name_length = self.read_u32()
                if name_length > 1:
                    element.name = self.read_str(name_length)
                
                path_length = self.read_u32()
                if path_length > 1:
                    element.path = self.read_str(path_length)
                    
                animation_count = self.read_u32()
                for _ in range(animation_count):
                    anim = EffectAnimation()
                    anim.header = self.read_u32()
                    anim.start = self.read_u32()
                    anim.end = self.read_u32()
                    anim.unknown = self.read_u32()
                    element.animations.append(anim)
                    
                self.data.elements.append(element)
                
            return True
            
        except Exception as e:
            print(f"Error parsing Effect: {e}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        self.write_u32(self.version)
        self.write_u32(len(self.data.elements))
        for element in self.data.elements:
            self.write_u32(element.header)
            self.write_u32(element.is_name_same_path)
            self.write_u32(element.width)
            self.write_u32(element.height)
            self.write_u32(element.is_giant)
            self.write_u32(2) # element.unknown)
            self.write_std_string(element.name)
            self.write_std_string(element.path)
            self.write_u32(len(element.animations))
            for anim in element.animations:
                self.write_u32(anim.header)
                self.write_u32(anim.start)
                self.write_u32(anim.end)
                self.write_u32(anim.unknown)
        return self._data

class CharaEffect(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = CharaEffectData()
    
    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            effect_set_count = self.read_u32()
            
            for _ in range(effect_set_count):
                element = CharaEffectElement()
                element.header = self.read_u32()
                element.effect = self.read_u32()
                element.param1 = self.read_u32()
                element.param2 = self.read_u32()
                element.param3 = self.read_u32()
                element.param4 = self.read_u32()
                element.param5 = self.read_u32()
                element.unknown = self.read_u32()

                name_length = self.read_u32()
                if name_length > 1:
                    element.name = self.read_str(name_length)
                    
                self.data.elements.append(element)
                
            return True
            
        except Exception as e:
            print(f"Error parsing CharaEffect: {e}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        self.write_u32(self.version)
        self.write_u32(len(self.data.elements))
        for element in self.data.elements:
            self.write_u32(element.header)
            self.write_u32(element.effect)
            self.write_u32(element.param1)
            self.write_u32(element.param2)
            self.write_u32(element.param3)
            self.write_u32(element.param4)
            self.write_u32(element.param5)
            self.write_u32(1) # element.unknown)
            self.write_std_string(element.name)
        return self._data

class ScrEffect(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = ScreenEffectData()
    
    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            scr_count = self.read_u32()
            
            for _ in range(scr_count):
                element = ScreenEffectElement()
                element.header = self.read_u32()
                element.effect = self.read_u32()
                element.param1 = self.read_u32()
                element.param2 = self.read_u32()
                element.param3 = self.read_u32()
                element.param4 = self.read_u32()
                element.param5 = self.read_u32()
                element.unknown = self.read_u32()

                name_length = self.read_u32()
                if name_length > 1:
                    element.name = self.read_str(name_length)
                    
                self.data.elements.append(element)
                
            return True
            
        except Exception as e:
            print(f"Error parsing ScreenEffect: {e}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        self.write_u32(self.version)
        self.write_u32(len(self.data.elements))
        for element in self.data.elements:
            self.write_u32(element.header)
            self.write_u32(element.effect)
            self.write_u32(element.param1)
            self.write_u32(element.param2)
            self.write_u32(element.param3)
            self.write_u32(element.param4)
            self.write_u32(element.param5)
            self.write_u32(1) # element.unknown)
            self.write_std_string(element.name)
        return self._data

class Picture(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = PictureData()
    
    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            element_count = self.read_u32()
            
            for _ in range(element_count):
                element = PictureElement()
                element.header = self.read_u32()
                element.is_name_same_path = self.read_u32()
                element.unknown2 = self.read_u32()

                name_length = self.read_u32()
                if name_length > 1:
                    element.name = self.read_str(name_length)
                
                path_length = self.read_u32()
                if path_length > 1:
                    element.path = self.read_str(path_length)
                    
                self.data.elements.append(element)
                
            return True
            
        except Exception as e:
            print(f"Error parsing Picture: {e}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        self.write_u32(self.version)
        self.write_u32(len(self.data.elements))
        for element in self.data.elements:
            self.write_u32(element.header)
            self.write_u32(element.is_name_same_path)
            self.write_u32(2) # element.unknown2)
            self.write_std_string(element.name)
            self.write_std_string(element.path)
        return self._data

class Sound(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = SoundData()
    
    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            element_count = self.read_u32()
            
            for _ in range(element_count):
                element = SoundElement()
                element.header = self.read_u32()
                element.is_name_same_path = self.read_u32()
                element.unknown2 = self.read_u32()

                name_length = self.read_u32()
                if name_length > 1:
                    element.name = self.read_str(name_length)
                
                path_length = self.read_u32()
                if path_length > 1:
                    element.path = self.read_str(path_length)
                    
                self.data.elements.append(element)
                
            return True
            
        except Exception as e:
            print(f"Error parsing Sound: {e}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        self.write_u32(self.version)
        self.write_u32(len(self.data.elements))
        for element in self.data.elements:
            self.write_u32(element.header)
            self.write_u32(element.is_name_same_path)
            self.write_u32(2) # element.unknown2)
            self.write_std_string(element.name)
            self.write_std_string(element.path)
        return self._data

class Bgm(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = BgmData()
    
    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            element_count = self.read_u32()
            
            for _ in range(element_count):
                element = BgmElement()
                element.header = self.read_u32()
                element.is_name_same_path = self.read_u32()
                element.volume = self.read_u32()
                element.unknown = self.read_u32()

                name_length = self.read_u32()
                if name_length > 1:
                    element.name = self.read_str(name_length)
                
                path_length = self.read_u32()
                if path_length > 1:
                    element.path = self.read_str(path_length)
                    
                self.data.elements.append(element)
                
            return True
            
        except Exception as e:
            print(f"Error parsing BGM: {e}")
            return False

    def serialize(self) -> bytes:
        self.start_writing()
        self.write_u32(self.version)
        self.write_u32(len(self.data.elements))
        for element in self.data.elements:
            self.write_u32(element.header)
            self.write_u32(element.is_name_same_path)
            self.write_u32(element.volume)
            self.write_u32(2) # element.unknown)
            self.write_std_string(element.name)
            self.write_std_string(element.path)
        return self._data

class CommonPalette(ActedBinaryFile): pass
class PrjOption(ActedBinaryFile): pass

class WorldMap(ActedBinaryFile):
    CHUNK_SIZE = 128  # Base chunk size in tiles

    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = WorldMapData()
    
    def _calculate_chunk_size(self, width: int) -> (int, int):
        """Calculate the chunk size needed for the given width"""
        # If width <= 32, use one chunk
        if width <= 32:
            return (5, self.CHUNK_SIZE)
        
        count = ceil(width / 32)
        
        multiplier = 1 << (count - 1).bit_length()
        return (multiplier, multiplier * self.CHUNK_SIZE)

    def parse(self) -> bool:
        if not self.load():
            return False
            
        try:
            self.data.tiles_types.clear()
            self.data.tiles.clear()
            self.data.events.clear()
            self.data.events_pal.clear()

            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print("Invalid magic number")
                return False
                
            self.version = magic
            self._settings_count = self.read_u32()

            self.data.width = self.read_u32()
            self.data.height = self.read_u32()
            
            self.data.chunk_width = self.read_u32()  # 32, 64, 128 ...
            self.data.chunk_pow = self.read_u32()  # 5, 6, 7 ...
            
            self.data.init_x = self.read_u32()
            self.data.init_y = self.read_u32()
            
            self.data.background_index = self.read_u32()
            self.data.use_background = self.read_u32()
            
            self.data.strings_count = self.read_u32()  # 2
            
            self.data.name = self.read_std_string()

            self.data.bg_path = self.read_std_string()
                
            # Read tile types (WorldChip)
            tiles_types_count = self.read_u32()
            for _ in range(tiles_types_count):
                self.data.tiles_types.append(self._read_world_chip())
                
                # tile = WorldChip()
                # tile.header = self.read_u32()
                # tile.tile_index = self.read_u32()
                # tile.locked = self.read_u32()
                # tile.graphic = self.read_u32()
                # tile.strings_count = self.read_u32()  # 2
                
                # # Read first string (name)
                # name_length = self.read_u32()
                # if name_length > 1:
                #     tile.name = self.read_str(name_length)
                
                # # Read second string (unused_string)
                # unused_string_length = self.read_u32()
                # if unused_string_length > 1:
                #     tile.unused_string = self.read_str(unused_string_length)
                    
                # self.data.tiles_types.append(tile)
                
            # Read tiles with proper chunking
            tiles_count = self.read_u32()
            # self.data.chunk_pow, self.data.chunk_width = self._calculate_chunk_size(self.data.width)
            # actual_tiles = self.data.width * self.data.height
            
            # Read all chunks
            for index in range(tiles_count):
                tile_value = self.read_u32()
                x = index % max(1, self.data.chunk_width)
                y = index // max(1, self.data.chunk_width)
                if x < self.data.width and y < self.data.height:
                    self.data.tiles.append(tile_value)
            # for i in range(tiles_count):
            #     tile = self.read_u32()
            #     if (i % self.data.chunk_width) < self.data.width:
            #         self.data.tiles.append(tile)
                
            # Read events
            events_count = self.read_u32()
            for _ in range(events_count):
                event = self._read_world_event()
                self.data.events.append(event)
                
            # Read event palette
            events_pal_count = self.read_u32()
            for _ in range(events_pal_count):
                event = self._read_world_event()
                self.data.events_pal.append(event)
                
            return True
            
        except Exception as e:
            print(f"Error parsing WorldMap: {e}")
            return False
            
    def serialize(self) -> bool:
        try:
            self.start_writing()

            self.write_u32(self.version)  # Write magic number
            self.write_u32(self._settings_count)  # Write settings count
            
            # Write map dimensions and chunk info
            self.write_u32(self.data.width)
            self.write_u32(self.data.height)
            
            # Calculate proper chunk size
            chunk_size = self._calculate_chunk_size(self.data.width)
            actual_tiles = self.data.width * self.data.height
            
            self.write_u32(self.data.chunk_width)
            self.write_u32(self.data.chunk_pow)
            
            # Write init position
            self.write_u32(self.data.init_x)
            self.write_u32(self.data.init_y)
            
            # Write background info
            self.write_u32(self.data.background_index)
            self.write_u32(self.data.use_background)
            
            # Write strings count and strings
            self.write_u32(self.data.strings_count)
            self.write_std_string(self.data.name)
            self.write_std_string(self.data.bg_path)
            
            # Write tile types count and tile types
            self.write_u32(len(self.data.tiles_types))
            for chip in self.data.tiles_types:
                self._write_world_chip(chip)
            
            # Write tiles count and tiles
            tiles_count = self.data.chunk_width * self.data.height
            tiles_count = max(tiles_count, (self.data.height - 1) * self.data.chunk_width + self.data.width)
            
            self.write_u32(tiles_count)

            tiles_to_write = [0] * tiles_count

            tile_idx = 0
            for y in range(self.data.height):
                for x in range(self.data.width):
                    index = y * self.data.chunk_width + x
                    if index < tiles_count and tile_idx < len(self.data.tiles):
                        tiles_to_write[index] = self.data.tiles[tile_idx]
                        tile_idx += 1
                        
            # self.write_u32(len(self.data.tiles))
            # for tile in self.data.tiles:
            #     self.write_u32(tile)

            # Write all tiles
            for tile_value in tiles_to_write:
                self.write_u32(tile_value)
            
            # Write events
            self.write_u32(len(self.data.events))
            for event in self.data.events:
                self._write_world_event(event)
            
            # Write event palette
            self.write_u32(len(self.data.events_pal))
            for event in self.data.events_pal:
                self._write_world_event(event)
                    
            return True
                
        except Exception as e:
            print(f"Error serializing WorldMap: {e}")
            return False
        finally:
            self.finish_writing()
        
    def _read_world_chip(self) -> WorldChip:
        chip = WorldChip()
        chip.header = self.read_u32()
        chip.tile_index = self.read_u32()
        chip.locked = self.read_u32()
        chip.graphic = self.read_u32()
        chip.strings_count = self.read_u32()
        chip.name = self.read_std_string()
        chip.unused_string = self.read_std_string()
        return chip

    def _write_world_chip(self, chip: WorldChip) -> None:
        self.write_u32(chip.header)
        self.write_u32(chip.tile_index)
        self.write_u32(chip.locked)
        self.write_u32(chip.graphic)
        self.write_u32(chip.strings_count or 2)
        self.write_std_string(chip.name)
        self.write_std_string(chip.unused_string)

    def _read_world_event(self) -> WorldEventBase:
        """Helper to read a world event structure"""
        event = WorldEventBase()
        event.header = self.read_u32()
        event.placement_x = self.read_u32()
        event.placement_y = self.read_u32()
        
        event.strings_count = self.read_u32()  # 1
        
        # Read event name
        event.name = self.read_std_string()
        
        # Read pages count
        event.pages_count = self.read_u32()
        
        # Read pages
        for _ in range(event.pages_count):
            page = self._read_world_event_page()
            event.pages.append(page)
            
        return event

    def _read_world_event_page(self) -> WorldEventPage:
        """Helper to read a world event page structure"""
        page = WorldEventPage()
        page.header = self.read_u32()
        page.event_type = self.read_u32()
        page.graphic = self.read_u32()
        
        page.world_number = self.read_u32()
        page.pass_without_clear = self.read_u32()
        page.play_after_clear = self.read_u32()
        page.on_game_clear = self.read_u32()
        
        page.appearance_condition_world = self.read_u32()
        page.appearance_condition_variable = self.read_u32()
        page.appearance_condition_constant = self.read_u32()
        page.appearance_condition_comparison_content = self.read_u32()
        page.appearance_condition_total_score = self.read_u32()
        
        page.variation_setting_present = self.read_u32()
        page.variation_variable = self.read_u32()
        page.variation_constant = self.read_u32()
        
        page.strings_count = self.read_u32()  # 2
        
        # Read world_name
        page.world_name = self.read_std_string()
        
        # Read start_stage
        page.start_stage = self.read_std_string()
            
        return page

    def _write_world_event(self, event: WorldEventBase):
        """Helper to write a world event structure"""
        self.write_u32(event.header)
        self.write_u32(event.placement_x)
        self.write_u32(event.placement_y)
        
        self.write_u32(event.strings_count or 1)

        self.write_std_string(event.name)
        
        self.write_u32(len(event.pages)) # event.pages_count
        
        for page in event.pages:
            self._write_world_event_page(page)

    def _write_world_event_page(self, page: WorldEventPage):
        """Helper to write a world event page structure"""
        self.write_u32(page.header)
        self.write_u32(page.event_type)
        self.write_u32(page.graphic)
        
        self.write_u32(page.world_number)
        self.write_u32(page.pass_without_clear)
        self.write_u32(page.play_after_clear)
        self.write_u32(page.on_game_clear)
        
        self.write_u32(page.appearance_condition_world)
        self.write_u32(page.appearance_condition_variable)
        self.write_u32(page.appearance_condition_constant)
        self.write_u32(page.appearance_condition_comparison_content)
        self.write_u32(page.appearance_condition_total_score)
        
        self.write_u32(page.variation_setting_present)
        self.write_u32(page.variation_variable)
        self.write_u32(page.variation_constant)
        
        self.write_u32(page.strings_count or 2)
        self.write_std_string(page.world_name)
        self.write_std_string(page.start_stage)

@dataclass
class StageDeathFade:
    list_size: int = 0
    auto_disappear_left: int = 0
    auto_disappear_right: int = 0
    auto_disappear_top: int = 0
    auto_disappear_bottom: int = 0
    disappear_left_range: int = 0
    disappear_right_range: int = 0
    disappear_top_range: int = 0
    disappear_bottom_range: int = 0
    block_end: int = 0


@dataclass
class StagePlayerCollision:
    walking_block_width: int = 0
    walking_block_height: int = 0
    flying_block_width: int = 0
    flying_block_height: int = 0
    walking_character_width: int = 0
    walking_character_height: int = 0
    flying_character_width: int = 0
    flying_character_height: int = 0
    shot_width: int = 0
    shot_height: int = 0
    item_width: int = 0
    item_height: int = 0
    walking_block_position: int = 0
    flying_block_position: int = 0
    walking_character_position: int = 0
    flying_character_position: int = 0
    block_display: int = 0
    character_display: int = 0
    shot_display: int = 0
    item_display: int = 0
    block_display_color: int = 0
    character_display_color: int = 0
    shot_display_color: int = 0
    item_display_color: int = 0


@dataclass
class StageEnemyCollision:
    walking_block_width: int = 0
    walking_block_height: int = 0
    flying_block_width: int = 0
    flying_block_height: int = 0
    walking_character_width: int = 0
    walking_character_height: int = 0
    flying_character_width: int = 0
    flying_character_height: int = 0
    shot_width: int = 0
    shot_height: int = 0
    walking_block_position: int = 0
    flying_block_position: int = 0
    walking_character_position: int = 0
    flying_character_position: int = 0


@dataclass
class StageActorHitbox:
    shot_width: int = 0
    shot_height: int = 0
    character_width: int = 0
    character_height: int = 0


@dataclass
class StageHeader:
    magic: int = 0
    entry_count: int = 0
    width: int = 0
    chunk_width: int = 0
    chunk_pow: int = 0
    height: int = 0
    enable_horizontal_scroll_minimum: int = 0
    enable_horizontal_scroll_maximum: int = 0
    enable_vertical_scroll_minimum: int = 0
    enable_vertical_scroll_maximum: int = 0
    horizontal_scroll_minimum_value: int = 0
    horizontal_scroll_maximum_value: int = 0
    vertical_scroll_minimum_value: int = 0
    vertical_scroll_maximum_value: int = 0
    frame_rate: int = 0
    enable_time_limit: int = 0
    time_limit_duration: int = 0
    warning_sound_start_time: int = 0
    enable_side_scroll: int = 0
    enable_vertical_scroll: int = 0
    autoscroll_speed: int = 0
    vertical_scroll_speed: int = 0
    gravity: float = 0.0
    hit_detection_level: int = 0
    character_shot_collision_detection_accuracy: int = 0
    bgm_number: int = 0
    bgm_loop_playback: int = 0
    dont_restart_bgm_if_no_change: int = 0
    enable_z_coordinate: int = 0
    inherit_status_from_stock: int = 0
    store_status_to_stock: int = 0
    show_status_window: int = 0
    switch_scene_immediately_on_clear: int = 0
    allow_replay_save: int = 0
    show_stage: int = 0
    show_ready: int = 0
    show_clear: int = 0
    show_gameover: int = 0
    player_collision: StagePlayerCollision = field(default_factory=StagePlayerCollision)
    enemy_collision: StageEnemyCollision = field(default_factory=StageEnemyCollision)
    item_collision_width: int = 0
    item_collision_height: int = 0
    player_hitbox: StageActorHitbox = field(default_factory=StageActorHitbox)
    enemy_hitbox: StageActorHitbox = field(default_factory=StageActorHitbox)
    undo_max_times: int = 0
    x_coordinate_upper_limit: int = 0
    y_coordinate_upper_limit: int = 0
    unk75: int = 0
    unk76: int = 0
    unk77: int = 0
    unk78: int = 0
    unk79: int = 0
    unk80: int = 0
    unk81: int = 0
    unk82: int = 0
    unk83: int = 0
    unk84: int = 0
    unk85: int = 0
    unk86: int = 0
    disable_damage_outside_screen: int = 0
    player_invincibility_from_same_enemy_duration: int = 0
    player_invincibility_duration: int = 0
    enemy_invincibility_from_same_player_duration: int = 0
    enemy_invincibility_duration: int = 0
    stage_name_count: int = 0
    stage_name: str = ""
    ranking_size: int = 0
    ranking_score: int = 0
    ranking_remaining_time: int = 0
    ranking_clear_time: int = 0
    ranking_remaining_hp: int = 0
    ranking_remaining_sp: int = 0
    nonblock_enemy_death: StageDeathFade = field(default_factory=StageDeathFade)
    block_enemy_death: StageDeathFade = field(default_factory=StageDeathFade)
    item_death: StageDeathFade = field(default_factory=StageDeathFade)
    player_death: StageDeathFade = field(default_factory=StageDeathFade)
    enemy_death: StageDeathFade = field(default_factory=StageDeathFade)


@dataclass
class StageData:
    header: StageHeader = field(default_factory=StageHeader)
    palette_payload: List[int] = field(default_factory=list)


class Stage(ActedBinaryFile):
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = StageData()
        self.version = 0

    def parse(self) -> bool:
        if not self.load():
            return False

        if len(self._data) < 4:
            print(f"Stage file {self.file_path} is too small to contain a version header")
            return False

        try:
            self.version = self.read_u32()
            header = self.data.header

            header.magic = self.read_u32()
            header.entry_count = self.read_u32()
            header.width = self.read_u32()
            header.chunk_width = self.read_u32()
            header.chunk_pow = self.read_u32()
            header.height = self.read_u32()

            header.enable_horizontal_scroll_minimum = self.read_u32()
            header.enable_horizontal_scroll_maximum = self.read_u32()
            header.enable_vertical_scroll_minimum = self.read_u32()
            header.enable_vertical_scroll_maximum = self.read_u32()

            header.horizontal_scroll_minimum_value = self.read_u32()
            header.horizontal_scroll_maximum_value = self.read_u32()
            header.vertical_scroll_minimum_value = self.read_u32()
            header.vertical_scroll_maximum_value = self.read_u32()

            header.frame_rate = self.read_u32()
            header.enable_time_limit = self.read_u32()
            header.time_limit_duration = self.read_u32()
            header.warning_sound_start_time = self.read_u32()

            header.enable_side_scroll = self.read_u32()
            header.enable_vertical_scroll = self.read_u32()
            header.autoscroll_speed = self.read_u32()
            header.vertical_scroll_speed = self.read_u32()

            header.gravity = self.read_f64()

            header.hit_detection_level = self.read_u32()
            header.character_shot_collision_detection_accuracy = self.read_u32()

            header.bgm_number = self.read_u32()
            header.bgm_loop_playback = self.read_u32()
            header.dont_restart_bgm_if_no_change = self.read_u32()

            header.enable_z_coordinate = self.read_u32()

            header.inherit_status_from_stock = self.read_u32()
            header.store_status_to_stock = self.read_u32()
            header.show_status_window = self.read_u32()

            header.switch_scene_immediately_on_clear = self.read_u32()
            header.allow_replay_save = self.read_u32()

            header.show_stage = self.read_u32()
            header.show_ready = self.read_u32()
            header.show_clear = self.read_u32()
            header.show_gameover = self.read_u32()

            header.player_collision = self._read_player_collision()
            header.enemy_collision = self._read_enemy_collision()

            header.item_collision_width = self.read_u32()
            header.item_collision_height = self.read_u32()

            header.player_hitbox = self._read_actor_hitbox()
            header.enemy_hitbox = self._read_actor_hitbox()

            header.undo_max_times = self.read_u32()
            header.x_coordinate_upper_limit = self.read_u32()
            header.y_coordinate_upper_limit = self.read_u32()

            header.unk75 = self.read_u32()
            header.unk76 = self.read_u32()
            header.unk77 = self.read_u32()
            header.unk78 = self.read_u32()
            header.unk79 = self.read_u32()
            header.unk80 = self.read_u32()
            header.unk81 = self.read_u32()
            header.unk82 = self.read_u32()
            header.unk83 = self.read_u32()
            header.unk84 = self.read_u32()
            header.unk85 = self.read_u32()
            header.unk86 = self.read_u32()

            header.disable_damage_outside_screen = self.read_u32()

            header.player_invincibility_from_same_enemy_duration = self.read_u32()
            header.player_invincibility_duration = self.read_u32()

            header.enemy_invincibility_from_same_player_duration = self.read_u32()
            header.enemy_invincibility_duration = self.read_u32()

            header.stage_name_count = self.read_u32()
            header.stage_name = self.read_std_string()

            header.ranking_size = self.read_u32()
            header.ranking_score = self.read_u32()
            header.ranking_remaining_time = self.read_u32()
            header.ranking_clear_time = self.read_u32()
            header.ranking_remaining_hp = self.read_u32()
            header.ranking_remaining_sp = self.read_u32()

            header.nonblock_enemy_death = self._read_death_fade()
            header.block_enemy_death = self._read_death_fade()
            header.item_death = self._read_death_fade()
            header.player_death = self._read_death_fade()
            header.enemy_death = self._read_death_fade()

            remaining = self._data[self._position:]
            self.data.palette_payload = list(remaining)
            return True
        except Exception as error:
            print(f"Failed to parse stage header for {self.file_path}: {error}")
            self.data.header = StageHeader()
            self.data.palette_payload = list(self._data[4:])
            return True

    def _read_death_fade(self) -> StageDeathFade:
        fade = StageDeathFade()
        fade.list_size = self.read_u32()
        fade.auto_disappear_left = self.read_u32()
        fade.auto_disappear_right = self.read_u32()
        fade.auto_disappear_top = self.read_u32()
        fade.auto_disappear_bottom = self.read_u32()
        fade.disappear_left_range = self.read_u32()
        fade.disappear_right_range = self.read_u32()
        fade.disappear_top_range = self.read_u32()
        fade.disappear_bottom_range = self.read_u32()
        fade.block_end = self.read_u32()
        return fade

    def _read_player_collision(self) -> StagePlayerCollision:
        collision = StagePlayerCollision()
        collision.walking_block_width = self.read_u32()
        collision.walking_block_height = self.read_u32()
        collision.flying_block_width = self.read_u32()
        collision.flying_block_height = self.read_u32()
        collision.walking_character_width = self.read_u32()
        collision.walking_character_height = self.read_u32()
        collision.flying_character_width = self.read_u32()
        collision.flying_character_height = self.read_u32()
        collision.shot_width = self.read_u32()
        collision.shot_height = self.read_u32()
        collision.item_width = self.read_u32()
        collision.item_height = self.read_u32()
        collision.walking_block_position = self.read_u32()
        collision.flying_block_position = self.read_u32()
        collision.walking_character_position = self.read_u32()
        collision.flying_character_position = self.read_u32()
        collision.block_display = self.read_u32()
        collision.character_display = self.read_u32()
        collision.shot_display = self.read_u32()
        collision.item_display = self.read_u32()
        collision.block_display_color = self.read_u32()
        collision.character_display_color = self.read_u32()
        collision.shot_display_color = self.read_u32()
        collision.item_display_color = self.read_u32()
        return collision

    def _read_enemy_collision(self) -> StageEnemyCollision:
        collision = StageEnemyCollision()
        collision.walking_block_width = self.read_u32()
        collision.walking_block_height = self.read_u32()
        collision.flying_block_width = self.read_u32()
        collision.flying_block_height = self.read_u32()
        collision.walking_character_width = self.read_u32()
        collision.walking_character_height = self.read_u32()
        collision.flying_character_width = self.read_u32()
        collision.flying_character_height = self.read_u32()
        collision.shot_width = self.read_u32()
        collision.shot_height = self.read_u32()
        collision.walking_block_position = self.read_u32()
        collision.flying_block_position = self.read_u32()
        collision.walking_character_position = self.read_u32()
        collision.flying_character_position = self.read_u32()
        return collision

    def _read_actor_hitbox(self) -> StageActorHitbox:
        hitbox = StageActorHitbox()
        hitbox.shot_width = self.read_u32()
        hitbox.shot_height = self.read_u32()
        hitbox.character_width = self.read_u32()
        hitbox.character_height = self.read_u32()
        return hitbox

    def _write_death_fade(self, fade: StageDeathFade) -> None:
        self.write_u32(fade.list_size)
        self.write_u32(fade.auto_disappear_left)
        self.write_u32(fade.auto_disappear_right)
        self.write_u32(fade.auto_disappear_top)
        self.write_u32(fade.auto_disappear_bottom)
        self.write_u32(fade.disappear_left_range)
        self.write_u32(fade.disappear_right_range)
        self.write_u32(fade.disappear_top_range)
        self.write_u32(fade.disappear_bottom_range)
        self.write_u32(fade.block_end)

    def _write_player_collision(self, collision: StagePlayerCollision) -> None:
        self.write_u32(collision.walking_block_width)
        self.write_u32(collision.walking_block_height)
        self.write_u32(collision.flying_block_width)
        self.write_u32(collision.flying_block_height)
        self.write_u32(collision.walking_character_width)
        self.write_u32(collision.walking_character_height)
        self.write_u32(collision.flying_character_width)
        self.write_u32(collision.flying_character_height)
        self.write_u32(collision.shot_width)
        self.write_u32(collision.shot_height)
        self.write_u32(collision.item_width)
        self.write_u32(collision.item_height)
        self.write_u32(collision.walking_block_position)
        self.write_u32(collision.flying_block_position)
        self.write_u32(collision.walking_character_position)
        self.write_u32(collision.flying_character_position)
        self.write_u32(collision.block_display)
        self.write_u32(collision.character_display)
        self.write_u32(collision.shot_display)
        self.write_u32(collision.item_display)
        self.write_u32(collision.block_display_color)
        self.write_u32(collision.character_display_color)
        self.write_u32(collision.shot_display_color)
        self.write_u32(collision.item_display_color)

    def _write_enemy_collision(self, collision: StageEnemyCollision) -> None:
        self.write_u32(collision.walking_block_width)
        self.write_u32(collision.walking_block_height)
        self.write_u32(collision.flying_block_width)
        self.write_u32(collision.flying_block_height)
        self.write_u32(collision.walking_character_width)
        self.write_u32(collision.walking_character_height)
        self.write_u32(collision.flying_character_width)
        self.write_u32(collision.flying_character_height)
        self.write_u32(collision.shot_width)
        self.write_u32(collision.shot_height)
        self.write_u32(collision.walking_block_position)
        self.write_u32(collision.flying_block_position)
        self.write_u32(collision.walking_character_position)
        self.write_u32(collision.flying_character_position)

    def _write_actor_hitbox(self, hitbox: StageActorHitbox) -> None:
        self.write_u32(hitbox.shot_width)
        self.write_u32(hitbox.shot_height)
        self.write_u32(hitbox.character_width)
        self.write_u32(hitbox.character_height)

    def _write_stage_header(self, header: StageHeader) -> None:
        self.write_u32(header.magic)
        self.write_u32(header.entry_count)
        self.write_u32(header.width)
        self.write_u32(header.chunk_width)
        self.write_u32(header.chunk_pow)
        self.write_u32(header.height)

        self.write_u32(header.enable_horizontal_scroll_minimum)
        self.write_u32(header.enable_horizontal_scroll_maximum)
        self.write_u32(header.enable_vertical_scroll_minimum)
        self.write_u32(header.enable_vertical_scroll_maximum)

        self.write_u32(header.horizontal_scroll_minimum_value)
        self.write_u32(header.horizontal_scroll_maximum_value)
        self.write_u32(header.vertical_scroll_minimum_value)
        self.write_u32(header.vertical_scroll_maximum_value)

        self.write_u32(header.frame_rate)
        self.write_u32(header.enable_time_limit)
        self.write_u32(header.time_limit_duration)
        self.write_u32(header.warning_sound_start_time)

        self.write_u32(header.enable_side_scroll)
        self.write_u32(header.enable_vertical_scroll)
        self.write_u32(header.autoscroll_speed)
        self.write_u32(header.vertical_scroll_speed)

        self.write_f64(header.gravity)

        self.write_u32(header.hit_detection_level)
        self.write_u32(header.character_shot_collision_detection_accuracy)

        self.write_u32(header.bgm_number)
        self.write_u32(header.bgm_loop_playback)
        self.write_u32(header.dont_restart_bgm_if_no_change)

        self.write_u32(header.enable_z_coordinate)

        self.write_u32(header.inherit_status_from_stock)
        self.write_u32(header.store_status_to_stock)
        self.write_u32(header.show_status_window)

        self.write_u32(header.switch_scene_immediately_on_clear)
        self.write_u32(header.allow_replay_save)

        self.write_u32(header.show_stage)
        self.write_u32(header.show_ready)
        self.write_u32(header.show_clear)
        self.write_u32(header.show_gameover)

        self._write_player_collision(header.player_collision)
        self._write_enemy_collision(header.enemy_collision)

        self.write_u32(header.item_collision_width)
        self.write_u32(header.item_collision_height)

        self._write_actor_hitbox(header.player_hitbox)
        self._write_actor_hitbox(header.enemy_hitbox)

        self.write_u32(header.undo_max_times)
        self.write_u32(header.x_coordinate_upper_limit)
        self.write_u32(header.y_coordinate_upper_limit)

        self.write_u32(header.unk75)
        self.write_u32(header.unk76)
        self.write_u32(header.unk77)
        self.write_u32(header.unk78)
        self.write_u32(header.unk79)
        self.write_u32(header.unk80)
        self.write_u32(header.unk81)
        self.write_u32(header.unk82)
        self.write_u32(header.unk83)
        self.write_u32(header.unk84)
        self.write_u32(header.unk85)
        self.write_u32(header.unk86)

        self.write_u32(header.disable_damage_outside_screen)

        self.write_u32(header.player_invincibility_from_same_enemy_duration)
        self.write_u32(header.player_invincibility_duration)

        self.write_u32(header.enemy_invincibility_from_same_player_duration)
        self.write_u32(header.enemy_invincibility_duration)

        self.write_u32(header.stage_name_count)
        stage_name = header.stage_name or ""
        if not stage_name:
            self.write_u32(0)
        else:
            encoded = stage_name.encode("shift-jis", errors="ignore")
            self.write_u32(len(encoded) + 1)
            self.write_str(stage_name, len(encoded))
            self.write_u8(0)

        self.write_u32(header.ranking_size)
        self.write_u32(header.ranking_score)
        self.write_u32(header.ranking_remaining_time)
        self.write_u32(header.ranking_clear_time)
        self.write_u32(header.ranking_remaining_hp)
        self.write_u32(header.ranking_remaining_sp)

        self._write_death_fade(header.nonblock_enemy_death)
        self._write_death_fade(header.block_enemy_death)
        self._write_death_fade(header.item_death)
        self._write_death_fade(header.player_death)
        self._write_death_fade(header.enemy_death)

    def save(self) -> bool:
        self.start_writing()
        self.write_u32(self.version)
        self._write_stage_header(self.data.header)

        payload = bytes(self.data.palette_payload)
        if payload:
            self._ensure_space(len(payload))
            self._data[self._position:self._position + len(payload)] = payload
            self._position += len(payload)

        self.finish_writing()
        return self.save_file()