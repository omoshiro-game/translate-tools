import argparse
import json
from dataclasses import dataclass, field, is_dataclass, asdict
from pathlib import Path
from typing import List, Union, Callable, TypeVar, Any
import struct


# --- Augmented Helper Class (Unchanged from original) ---

class ActedBinaryFile:
    VERSIONS = [
        0x03C6,  # ??
        1020,    # v1020 (stg4/cplt4 magic)
        0x03FC   # v1020
    ]
    T = TypeVar('T')

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self._data = bytearray()
        self._position = 0
        self._append_mode = False

    def load(self) -> bool:
        try:
            self._data = bytearray(self.file_path.read_bytes())
            self._position = 0
            return True
        except Exception as e:
            print(f"Error loading {self.file_path}: {e}")
            return False

    def save_file(self) -> bool:
        try:
            self.file_path.write_bytes(bytes(self._data))
            return True
        except Exception as e:
            print(f"Error saving {self.file_path}: {e}")
            return False

    def save_to(self, file_path: Union[str, Path]) -> bool:
        try:
            Path(file_path).write_bytes(bytes(self._data))
            return True
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
            return False

    def start_writing(self):
        self._data = bytearray()
        self._position = 0
        self._append_mode = True

    def finish_writing(self):
        self._append_mode = False
        # Trim the buffer to the current position
        self._data = self._data[:self._position]

    def _ensure_space(self, size: int):
        if self._append_mode or self._position + size > len(self._data):
            needed = self._position + size - len(self._data)
            if needed > 0:
                self._data.extend(bytearray(needed))

    def read_u8(self) -> int:
        value = self._data[self._position]
        self._position += 1
        return value

    def read_s8(self) -> int:
        value = struct.unpack_from("<b", self._data, self._position)[0]
        self._position += 1
        return value

    def read_u16(self) -> int:
        value = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        return value

    def read_s16(self) -> int:
        value = struct.unpack_from("<h", self._data, self._position)[0]
        self._position += 2
        return value

    def read_u32(self) -> int:
        value = struct.unpack_from("<I", self._data, self._position)[0]
        self._position += 4
        return value
    
    def read_s32(self) -> int:
        value = struct.unpack_from("<i", self._data, self._position)[0]
        self._position += 4
        return value

    def read_f32(self) -> float:
        value = struct.unpack_from("<f", self._data, self._position)[0]
        self._position += 4
        return value

    def read_f64(self) -> float:
        value = struct.unpack_from("<d", self._data, self._position)[0]
        self._position += 8
        return value

    def read_bytes(self, length: int) -> bytes:
        data = self._data[self._position:self._position + length]
        self._position += length
        return bytes(data)

    def read_str(self, length: int) -> str:
        data = self.read_bytes(length)
        try:
            return data.decode('shift-jis').rstrip('\x00')
        except UnicodeDecodeError:
            return data.decode('latin-1').rstrip('\x00')

    def read_std_string(self) -> str:
        length = self.read_u32()
        if length > 1:
            # The length from file seems to include the null terminator
            return self.read_str(length if length > 1 else 0)
        return ""

    def write_u8(self, value: int):
        self._ensure_space(1)
        struct.pack_into("<B", self._data, self._position, value)
        self._position += 1

    def write_s8(self, value: int):
        self._ensure_space(1)
        struct.pack_into("<b", self._data, self._position, value)
        self._position += 1

    def write_u16(self, value: int):
        self._ensure_space(2)
        struct.pack_into("<H", self._data, self._position, value)
        self._position += 2

    def write_s16(self, value: int):
        self._ensure_space(2)
        struct.pack_into("<h", self._data, self._position, value)
        self._position += 2

    def write_u32(self, value: int):
        self._ensure_space(4)
        struct.pack_into("<I", self._data, self._position, value)
        self._position += 4
    
    def write_s32(self, value: int):
        self._ensure_space(4)
        struct.pack_into("<i", self._data, self._position, value)
        self._position += 4

    def write_f32(self, value: float):
        self._ensure_space(4)
        struct.pack_into("<f", self._data, self._position, value)
        self._position += 4

    def write_f64(self, value: float):
        self._ensure_space(8)
        struct.pack_into("<d", self._data, self._position, value)
        self._position += 8

    def write_bytes(self, data: Union[bytes, bytearray]):
        length = len(data)
        self._ensure_space(length)
        self._data[self._position:self._position + length] = data
        self._position += length
        
    def write_str(self, value: str, fixed_length: int = -1):
        encoded = value.encode('shift-jis', errors='ignore')
        if fixed_length != -1:
            encoded = encoded[:fixed_length].ljust(fixed_length, b'\x00')
        self.write_bytes(encoded)

    def write_std_string(self, value: str):
        if not value:
            self.write_u32(1)
            return
        encoded = value.encode('shift-jis', errors='ignore')
        # +1 for null terminator
        self.write_u32(len(encoded) + 1)
        self.write_bytes(encoded)
        self.write_u8(0) # Null terminator

    def _read_array(self, parser_func: Callable[[], T]) -> List[T]:
        count = self.read_u32()
        return [parser_func() for _ in range(count)]

    def _write_array(self, arr: List[Any], writer_func: Callable[[Any], None]):
        self.write_u32(len(arr))
        for item in arr:
            writer_func(item)

# --- Palette Dataclasses ---

# region Stage Header
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
# endregion

# region Palette Stage
@dataclass
class BasicCondition:
    header: int = 0
    type: int = 0
    right_side_constant: int = 0
    right_side_random_lower_limit: int = 0
    right_side_random_upper_limit: int = 0
    left_side_status_target: int = 0
    left_side_status_number: int = 0
    left_side_type: int = 0
    left_side_common_variable_or_stage_variable: int = 0
    left_side_variable_number: int = 0
    left_side_flow_variable_number: int = 0
    right_side_type: int = 0
    right_side_status_target: int = 0
    right_side_status_number: int = 0
    right_side_common_variable_or_stage_variable: int = 0
    right_side_variable_number: int = 0
    right_side_flow_variable_number: int = 0
    how_to_compare: int = 0
    specify_in_percent: int = 0
    left_side_coordinate_type: int = 0
    right_side_coordinate_type: int = 0
    left_side_gigantic_character_coordinate_position: int = 0
    right_side_gigantic_character_coordinate_position: int = 0
    unk1: int = 0
    unk2: int = 0
    unk3: int = 0
    unk4: int = 0
    unk5: int = 0

@dataclass
class KeyCondition:
    header: int = 0
    right_and_left_to_front_and_back: int = 0
    minimum_input_time: int = 0
    maximum_input_time: int = 0
    input_time_1_to_infinity: int = 0
    judgment_type: int = 0
    unknown: int = 0
    number_of_key_data: int = 0
    direction_key_neutral: int = 0
    left_key: int = 0
    right_key: int = 0
    up_key: int = 0
    down_key: int = 0
    up_left_key: int = 0
    down_left_key: int = 0
    up_right_key: int = 0
    down_right_key: int = 0
    any_direction_key: int = 0
    action_key_neutral: int = 0
    z_key: int = 0
    x_key: int = 0
    c_key: int = 0
    v_key: int = 0
    a_key: int = 0
    s_key: int = 0
    d_key: int = 0
    f_key: int = 0

@dataclass
class Command:
    header: int = 8
    unk1: int = 0
    type: int = 0
    details: Any = None # Will hold specific detail dataclass

@dataclass
class ItemEffect:
    header: int = 8
    unk1: int = 0
    type: int = 0
    details: Any = None # Will hold specific detail dataclass

@dataclass
class Flow:
    header: int = 10
    id: int = 0
    group: int = 0
    test_play_only: int = 0
    basic_condition_judgment_type: int = 0
    basic_condition_once_met_always_met: int = 0
    timing: int = 0
    target_character_involved_in_timing: int = 0
    target_number_of_character_involved_in_timing: int = 0
    ease_of_input_with_multiple_key_conditions: int = 0
    allow_continuous_execution_by_holding_key: int = 0
    memo_count: int = 1
    memo: str = ""
    conditions: List[BasicCondition] = field(default_factory=list)
    key_conditions: List[KeyCondition] = field(default_factory=list)
    commands: List[Command] = field(default_factory=list)

@dataclass
class Block:
    header: int = 0
    inherit_palette: int = 0
    inherit_palette_data: int = 0
    any_of_appearance_conditions_true: int = 0
    appearance_condition_once_met_always_true: int = 0
    image_number: int = 0
    image_type: int = 0
    unknown1: int = 0
    in_front_of_character: int = 0
    transparency: int = 0
    mark_display: int = 0
    mark_number: int = 0
    unknown2: int = 0
    block_type: int = 0
    invalid_faction: int = 0
    action: int = 0
    action_parameter: int = 0
    acquired_item_palette: int = 0
    acquired_item_palette_data_number: int = 0
    block_summon_invalid: int = 0
    name: str = ""
    position_x: int = 0
    position_y: int = 0
    inherited_data_count: int = 0
    inherit_block_name: int = 0
    inherit_appearance_condition: int = 0
    inherit_image: int = 0
    inherit_in_front_of_character: int = 0
    inherit_transparency: int = 0
    inherit_mark: int = 0
    inherit_block_type: int = 0
    inherit_invalid_faction: int = 0
    inherit_action: int = 0
    inherit_acquired_item: int = 0
    inherit_block_summon: int = 0
    display_conditions: List[BasicCondition] = field(default_factory=list)

@dataclass
class Character:
    header: int = 0
    inherit_palette: int = 0
    inherit_palette_data_number: int = 0
    any_of_appearance_conditions_true: int = 0
    appearance_condition_once_met_always_true: int = 0
    facing_right: int = 0
    number_of_doubles: int = 0
    appearance_position_offset_x_bl: int = 0
    appearance_position_offset_x_dot: int = 0
    appearance_position_offset_y_bl: int = 0
    appearance_position_offset_y_dot: int = 0
    appearance_position_offset_x_flip_if_facing_right: int = 0
    appearance_position_offset_y_flip_if_facing_right: int = 0
    image_number: int = 0
    image_type: int = 0
    image_offset: int = 0
    animation_set: int = 0
    z_coordinate: int = 0
    transparency: int = 0
    initial_character_effect: int = 0
    initial_character_effect_execution_type: int = 0
    initial_character_effect_loop_execution: int = 0
    character_effect_on_death: int = 0
    character_effect_on_death_execution_type: int = 0
    mark_display: int = 0
    mark_number: int = 0
    operation: int = 0
    faction: int = 0
    character_id: int = 0
    flying: int = 0
    direction_fixed: int = 0
    invincible: int = 0
    invincible_effect: int = 0
    block: int = 0
    gigantic: int = 0
    synchronize_with_auto_scroll: int = 0
    line_of_sight: int = 0
    line_of_sight_range: int = 0
    hp: int = 0
    sp: int = 0
    stopping_ease_during_inertial_movement: int = 0
    body_hit_detection_range: int = 0
    body_hit_power: int = 0
    body_hit_impact: int = 0
    body_hit_effect: int = 0
    defense: int = 0
    impact_resistance: int = 0
    score: int = 0
    holds_item_at_same_position: int = 0
    has_group: int = 0
    group_number: int = 0
    action_condition_range: int = 0
    action_condition_judgment_type: int = 0
    strings_count: int = 1 # For parsing only
    character_name: str = ""
    position_x: int = 0
    position_y: int = 0
    some_count: int = 0
    inherited_data_count: int = 0
    inherit_character_name: int = 0
    inherit_operation: int = 0
    inherit_faction: int = 0
    inherit_character_id: int = 0
    inherit_appearance_condition: int = 0
    inherit_facing_right: int = 0
    inherit_number_of_doubles: int = 0
    inherit_initial_position_offset_x: int = 0
    inherit_initial_position_offset_y: int = 0
    inherit_image: int = 0
    inherit_animation_set: int = 0
    inherit_z_coordinate: int = 0
    inherit_transparency: int = 0
    inherit_initial_character_effect: int = 0
    inherit_character_effect_on_death: int = 0
    inherit_mark: int = 0
    inherit_direction_fixed: int = 0
    inherit_flying: int = 0
    inherit_invincible: int = 0
    inherit_block: int = 0
    inherit_gigantic: int = 0
    inherit_synchronize_with_auto_scroll: int = 0
    inherit_line_of_sight: int = 0
    inherit_hp: int = 0
    inherit_sp: int = 0
    inherit_body_hit_detection_range: int = 0
    inherit_body_hit_power: int = 0
    inherit_body_hit_impact: int = 0
    inherit_body_hit_effect: int = 0
    inherit_defense: int = 0
    inherit_impact_resistance: int = 0
    inherit_stopping_ease_during_inertial_movement: int = 0
    inherit_action_condition: int = 0
    inherit_group: int = 0
    inherit_score: int = 0
    inherit_holds_item_at_same_position: int = 0
    inherit_action: int = 0
    conditions: List[BasicCondition] = field(default_factory=list)
    flows: List[Flow] = field(default_factory=list)

@dataclass
class Item:
    header: int = 0
    inherit_palette: int = 0
    inherit_palette_data_number: int = 0
    any_of_appearance_conditions_true: int = 0
    appearance_condition_once_met_always_true: int = 0
    appearance_position_offset_x_dot: int = 0
    appearance_position_offset_y_dot: int = 0
    image_number: int = 0
    image_type: int = 0
    frame: int = 0
    z_coordinate: int = 0
    transparency: int = 0
    mark_display: int = 0
    mark_number: int = 0
    display_above_head_on_acquisition: int = 0
    acquisition_type: int = 0
    gigantic: int = 0
    sound_effect: int = 0
    item_name_length: int = 1
    item_name: str = ""
    position_x: int = 0
    position_y: int = 0
    number_of_inherited_data: int = 0
    inherit_item_name: int = 0
    inherit_appearance_condition: int = 0
    inherit_initial_position_offset_x: int = 0
    inherit_initial_position_offset_y: int = 0
    inherit_image: int = 0
    inherit_z_coordinate: int = 0
    inherit_transparency: int = 0
    inherit_mark: int = 0
    inherit_gigantic: int = 0
    inherit_acquisition_type: int = 0
    inherit_display_above_head_on_acquisition: int = 0
    inherit_sound_effect: int = 0
    inherit_effect: int = 0
    conditions: List[BasicCondition] = field(default_factory=list)
    item_effects: List[ItemEffect] = field(default_factory=list)

@dataclass
class StagePalette:
    blocks: List[Block] = field(default_factory=list)
    characters: List[Character] = field(default_factory=list)
    items: List[Item] = field(default_factory=list)

@dataclass
class StageBlock:
    position: int = 0
    block: Block = field(default_factory=Block)

@dataclass
class StageCharacter:
    position: int = 0
    character: Character = field(default_factory=Character)

@dataclass
class StageItem:
    position: int = 0
    item: Item = field(default_factory=Item)

@dataclass
class Background:
    start: int = 0
    display_from_start: int = 0
    specified_by_color: int = 0
    color_number: int = 0
    display_in_front_of_character: int = 0
    horizontal_scroll_speed: float = 0.0
    vertical_scroll_speed: float = 0.0
    horizontal_auto_scroll: int = 0
    vertical_auto_scroll: int = 0
    horizontal_auto_scroll_speed: float = 0.0
    vertical_auto_scroll_speed: float = 0.0
    bytes61_80: bytes = b'\x00' * 20
    image_path: str = ""

@dataclass
class StageVar:
    unk: int = 0
    count: int = 1
    var_name: str = ""
# endregion

# region Cmd + ItemFx Details (Unchanged)
# Note: Many structures are identical for Commands and ItemEffects, so they are shared.
@dataclass
class FlowChangeDetails:
    bytes1_30: bytes = b'\x00' * 30
    flows: List[Flow] = field(default_factory=list)
    bytes69_72: bytes = b'\x00' * 4
    operation: int = 0
    bytes77_80: bytes = b'\x00' * 4

@dataclass
class StageClearDetails:
    bytes1_14: bytes = b'\x00' * 14
    path: str = ""
    bytes19_38: bytes = b'\x00' * 20
    stage_transition: int = 0
    number: int = 0
    change_world_map_position: int = 0
    world_map_position_x: int = 0
    world_map_position_y: int = 0
    change_initial_position: int = 0
    initial_position_x: int = 0
    initial_position_y: int = 0
    initial_position_main_character_direction: int = 0
    execute_autosave: int = 0
    add_clear_text_to_replay: int = 0

@dataclass
class GameWaitDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    bytes6_38: bytes = b'\x00' * 33
    game_wait_execution_time: int = 0

@dataclass
class MessageDetails:
    bytes1_14: bytes = b'\x00' * 14
    message: str = ""
    bytes19_38: bytes = b'\x00' * 20
    display_position_specification_method: int = 0
    coordinate_x: int = 0
    coordinate_y: int = 0
    display_position_offset_x: int = 0
    display_position_offset_y: int = 0
    auto_adjust_to_not_go_off_screen: int = 0
    display_time_specification_method: int = 0
    display_time: int = 0
    pause: int = 0
    display_variables: int = 0
    follow_screen: int = 0
    auto_update: int = 0
    message_id_present: int = 0
    message_id: int = 0
    window_display: int = 0
    message_clear: int = 0
    update_interval: int = 0
    instant_display: int = 0
    coordinate_unit: int = 0
    set_options: int = 0
    assign_return_value_to_flow_variable: int = 0

@dataclass
class WarpDetails:
    bytes1_26: bytes = b'\x00' * 26
    setting_type: int = 0
    direction: int = 0
    bytes29_33: bytes = b'\x00' * 5
    target_x_present: int = 0
    target_y_present: int = 0
    target_x_bl: int = 0
    target_y_bl: int = 0
    target_x_dot: int = 0
    target_y_dot: int = 0
    target_type: int = 0
    target_unit: int = 0
    gigantic_character_coordinate_position: int = 0
    bytes47_49: bytes = b'\x00' * 3
    target_x_flip_if_facing_right: int = 0
    target_y_flip_if_facing_right: int = 0
    bytes52_59: bytes = b'\x00' * 8
    distance: int = 0
    distance_double: int = 0
    bytes64_101: bytes = b'\x00' * 38
    assign_return_value_to_flow: int = 0

@dataclass
class StatusOperationDetails:
    bytes1_38: bytes = b'\x00' * 38
    operation_target_type: int = 0
    bytes40_43: bytes = b'\x00' * 4
    operation_target_variable_type: int = 0
    bytes45_46: bytes = b'\x00' * 2
    operation_target_variable_number: int = 0
    bytes49_52: bytes = b'\x00' * 4
    operation_target_target: int = 0
    bytes54_56: bytes = b'\x00' * 3
    operation_target_status: int = 0
    byte58: bytes = b'\x00' * 1
    operation_target_flow_variable_number: int = 0
    bytes60_62: bytes = b'\x00' * 3
    operator_type: int = 0
    bytes64_66: bytes = b'\x00' * 3
    calculation_content_type: int = 0
    calculation_content_constant: int = 0
    calculation_content_random_lower_limit: int = 0
    calculation_content_random_upper_limit: int = 0
    calculation_content_variable_type: int = 0
    calculation_content_variable_number: int = 0
    calculation_content_target: int = 0
    calculation_content_status: int = 0
    calculation_content_flow_variable_number: int = 0
    bytes103_138: bytes = b'\x00' * 36

@dataclass
class StatusOperation2Details:
    bytes1_38: bytes = b'\x00' * 38
    target: int = 0
    status: int = 0
    on: int = 0
    bytes51_62: bytes = b'\x00' * 12

@dataclass
class DisappearanceDetails:
    bytes1_38: bytes = b'\x00' * 38
    target: int = 0
    faction: int = 0
    range: int = 0
    assign_return_value_to_flow_variable: int = 0

@dataclass
class ItemAcquisitionDetails:
    bytes1_38: bytes = b'\x00' * 38
    palette_type: int = 0
    palette_data_number: int = 0

@dataclass
class GraphicChangeDetails:
    bytes1_38: bytes = b'\x00' * 38
    image_type: int = 0
    image_number: int = 0
    offset: int = 0

@dataclass
class BasicAnimationSetChangeDetails:
    bytes1_38: bytes = b'\x00' * 38
    animation_set: int = 0

@dataclass
class AnimationExecutionDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    bytes: "bytes" = b'\x00' * 41

@dataclass
class EffectExecutionDetails:
    bytes1_38: bytes = b'\x00' * 38
    bytes: "bytes" = b'\x00' * 40

@dataclass
class CharacterEffectExecutionDetails:
    bytes1_38: bytes = b'\x00' * 38
    effect: int = 0
    execution_type: int = 0
    loop_execution: int = 0

@dataclass
class ScreenEffectExecutionDetails:
    bytes1_38: bytes = b'\x00' * 38
    effect: int = 0
    execution_type: int = 0
    loop_execution: int = 0

@dataclass
class PictureDisplayDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    bytes: "bytes" = b'\x00' * 113

@dataclass
class ScreenColorChangeDetails:
    bytes1_38: bytes = b'\x00' * 38
    r: int = 0
    g: int = 0
    b: int = 0
    percent: int = 0
    restore_to_original_color: int = 0
    time_required_for_change: int = 0
    instant_display: int = 0
    instant_display_count: int = 0

@dataclass
class BackgroundChangeDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    bytes: "bytes" = b'\x00' * 41

@dataclass
class SoundEffectPlaybackDetails:
    bytes1_7: bytes = b'\x00' * 7
    play_if_outside_screen: int = 0
    bytes9_38: bytes = b'\x00' * 30
    sound_effect: int = 0

@dataclass
class BGMPlaybackDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    bytes: "bytes" = b'\x00' * 41

@dataclass
class CodeExecutionDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    bytes6_14: bytes = b'\x00' * 9
    code: str = ""
    bytes19_38: bytes = b'\x00' * 20

@dataclass
class ArrangementDetails:
    bytes1_38: bytes = b'\x00' * 38
    command: int = 0
    parameter: int = 0
    operator_type: int = 0
    variable_type: int = 0
    variable_number: int = 0

@dataclass
class LoopDetails:
    bytes1_38: bytes = b'\x00' * 38
    repeat_count: int = 0
    command_count: int = 0
    
@dataclass
class WaitDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    bytes: "bytes" = b'\x00' * 33

@dataclass
class LinearMovementDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    bytes6_8: bytes = b'\x00' * 3
    animation_and_other_type: int = 0
    bytes11_26: bytes = b'\x00' * 16
    movement_direction_setting_type: int = 0
    movement_direction_direction: int = 0
    movement_direction_angle: int = 0
    movement_direction_angle_double: int = 0
    movement_direction_angle_reverse_rotation_if_facing_right: int = 0
    movement_direction_target_x_present: int = 0
    movement_direction_target_y_present: int = 0
    movement_direction_target_x: int = 0
    movement_direction_target_y: int = 0
    movement_direction_target_x_dot: int = 0
    movement_direction_target_y_dot: int = 0
    movement_direction_target_type: int = 0
    movement_direction_target_coordinate_unit: int = 0
    byte46: bytes = b'\x00' * 1
    movement_direction_execute_until_target_coordinate_reached: int = 0
    movement_direction_invalidate_horizontal_movement: int = 0
    movement_direction_invalidate_vertical_movement: int = 0
    movement_direction_target_x_flip_if_facing_right: int = 0
    movement_direction_target_y_flip_if_facing_right: int = 0
    movement_direction_reverse_speed_if_direction_changes: int = 0
    movement_direction_prevent_blur: int = 0
    movement_direction_dont_change_character_direction: int = 0
    time_speed_distance_setting_type: int = 0
    time_speed_distance_speed: int = 0
    time_speed_distance_speed_double: int = 0
    time_speed_distance_distance: int = 0
    time_speed_distance_distance_double: int = 0
    time_speed_distance_distance_unit: int = 0
    bytes65_68: bytes = b'\x00' * 4
    inertia_present: int = 0
    inertia_max_speed: int = 0
    inertia_speed_correction_on_direction_change: float = 0.0
    animation_type: int = 0
    bytes81_101: bytes = b'\x00' * 21

@dataclass
class GenericMovementDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    bytes6_101: bytes = b'\x00' * 96

@dataclass
class DirectionChangeDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    bytes6_42: bytes = b'\x00' * 37

@dataclass
class JumpDetails:
    bytes1_5: bytes = b'\x00' * 5
    sound_effect: int = 0
    play_if_outside_screen: int = 0
    animation: int = 0
    bytes11_38: bytes = b'\x00' * 28
    jump_type: int = 0
    max_jump_inertial_movement_speed: int = 0
    max_jump_height: int = 0
    min_jump_inertial_movement_speed: int = 0
    min_jump_height: int = 0

@dataclass
class ShotDetails:
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    sound_effect: int = 0
    play_if_outside_screen: int = 0
    animation: int = 0
    bytes11_30: bytes = b'\x00' * 20
    number_of_shots_fired: int = 0
    formation: int = 0
    firing_parameter1: int = 0
    firing_parameter2: int = 0
    firing_parameter3: int = 0
    target: int = 0
    direction: int = 0
    set_angle_to_target: int = 0
    firing_target: int = 0
    angle_offset: int = 0
    angle_offset_double: int = 0
    angle_offset_reverse_rotation_if_facing_right: int = 0
    angle_dispersion: int = 0
    change_firing_position_according_to_angle: int = 0
    number_of_doubles: int = 0
    firing_position_offset_x: int = 0
    firing_position_offset_x_double: int = 0
    firing_position_offset_y: int = 0
    firing_position_offset_y_double: int = 0
    firing_position_offset_x_flip_if_facing_right: int = 0
    firing_position_offset_y_flip_if_facing_right: int = 0
    graphic: int = 0
    z_coordinate: int = 0
    transparency: int = 0
    faction_same_as_user: int = 0
    faction: int = 0
    gigantic: int = 0
    movement_type: int = 0
    movement_type_parameter1: int = 0
    movement_type_parameter2: int = 0
    movement_type_parameter3: int = 0
    movement_target: int = 0
    synchronize_with_auto_scroll: int = 0
    speed: int = 0
    speed_double: int = 0
    acceleration_enabled: int = 0
    acceleration: int = 0
    acceleration_double: int = 0
    flight_distance: int = 0
    flight_distance_valid: int = 0
    flight_distance_double: int = 0
    flight_distance_does_not_disappear_at_end: int = 0
    disappearance_time_valid: int = 0
    disappearance_time: int = 0
    disappearance_time_double: int = 0
    penetrate_blocks: int = 0
    penetrate_actors: int = 0
    penetrate_block_actors: int = 0
    disappear_on_hitting_shot: int = 0
    value_for_disappearing_on_hitting_shot: int = 0
    power: int = 0
    bytes109_110: bytes = b'\x00' * 2
    impact: int = 0
    effect: int = 0
    acquired_item_palette_type: int = 0
    acquired_item_palette_number: int = 0
    bytes117_125: bytes = b'\x00' * 9
    attack: int = 0
    attack_id: int = 0
    bytes128_143: bytes = b'\x00' * 16

@dataclass
class SwordDetails:
    execution_time: int = 0
    parallel_execution: int = 0
    sound_effect: int = 0
    play_if_outside_screen: int = 0
    animation: int = 0
    bytes11_63: bytes = b'\x00' * 53
    z_coordinate: int = 0
    transparency: int = 0
    faction_same_as_user: int = 0
    faction: int = 0
    gigantic: int = 0
    sword_type: int = 0
    bytes75_104: bytes = b'\x00' * 30
    power: int = 0
    bytes109_110: bytes = b'\x00' * 2
    impact: int = 0
    effect: int = 0
    acquired_item_palette_type: int = 0
    acquired_item_palette_number: int = 0
    bytes117_125: bytes = b'\x00' * 9
    attack: int = 0
    attack_id: int = 0
    bytes128_143: bytes = b'\x00' * 16

@dataclass
class SummonDetails: # For Block, Character, Item
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    sound_effect: int = 0
    play_sound_effect_if_outside_screen: int = 0
    animation: int = 0
    bytes10_30: bytes = b'\x00' * 21
    count: int = 0
    formation: int = 0
    interval: int = 0
    number_of_columns: int = 0
    column_interval: int = 0
    target: int = 0
    direction: int = 0
    byte41: int = 0
    target2: int = 0
    bytes43_51: bytes = b'\x00' * 9
    summon_position_offset_x: int = 0
    summon_position_offset_y: int = 0
    summon_position_offset_x_flip: int = 0
    summon_position_offset_y_flip: int = 0
    bytes62_66: bytes = b'\x00' * 5
    faction: int = 0
    bytes68_88: bytes = b'\x00' * 21
    existence_time: int = 0
    existence_time_present: int = 0
    bytes92_119: bytes = b'\x00' * 28
    palette_type: int = 0
    palette_data_number: int = 0
    faction_specification_method: int = 0
    set_acquired_score_to_0: int = 0
    direction_flip: int = 0
    attack: int = 0
    attack_flow: int = 0
    bytes128_143: bytes = b'\x00' * 16
    return_value_to_flow_variable: int = 0 # For Block/Character
    bytes145_147: bytes = b'\x00' * 3 # For Block/Character

@dataclass
class ItemSummonDetails: # Item
    execution_time: int = 0
    execution_time_double: int = 0
    parallel_execution: int = 0
    sound_effect: int = 0
    play_sound_effect_if_outside_screen: int = 0
    animation: int = 0
    bytes10_30: bytes = b'\x00' * 21
    count: int = 0
    formation: int = 0
    interval: int = 0
    number_of_columns: int = 0
    column_interval: int = 0
    target: int = 0
    direction: int = 0
    byte41: int = 0
    target2: int = 0
    bytes43_51: bytes = b'\x00' * 9
    summon_position_offset_x: int = 0
    summon_position_offset_y: int = 0
    summon_position_offset_x_flip: int = 0
    summon_position_offset_y_flip: int = 0
    bytes62_66: bytes = b'\x00' * 5
    faction: int = 0
    bytes68_88: bytes = b'\x00' * 21
    existence_time: int = 0
    existence_time_present: int = 0
    bytes92_119: bytes = b'\x00' * 28
    palette_type: int = 0
    palette_data_number: int = 0
    faction_specification_method: int = 0
    set_acquired_score_to_0: int = 0
    direction_flip: int = 0
    attack: int = 0
    attack_flow: int = 0
    bytes128_143: bytes = b'\x00' * 16

@dataclass
class FlowOperationDetails:
    bytes1_34: bytes = b'\x00' * 34
    condition_present: int = 0
    judgment_type: int = 0
    bytes37_40: bytes = b'\x00' * 4
    conditions: List[BasicCondition] = field(default_factory=list)
    bytes45_52: bytes = b'\x00' * 8
    operation: int = 0
    target_flow: int = 0
    id: int = 0
    target_character: int = 0
    assign_return_value_to_flow_variable: int = 0
    
@dataclass
class TargetSettingDetails:
    bytes1_38: bytes = b'\x00' * 38
    bytes39_106: bytes = b'\x00' * 68
# endregion

# --- NEW: Main CPLT4 Data Container ---
@dataclass
class Cplt4Data:
    magic: int = 1020
    unk1: int = 0
    unk2: int = 0
    palette: StagePalette = field(default_factory=StagePalette)


# --- NEW: Main Parser/Serializer Class for CPLT4 ---

class Cplt4(ActedBinaryFile):
    """
    Parser and serializer for CPLT4 palette files.
    Adapted from the STG4 tool.
    """
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.data = Cplt4Data()

    def parse(self) -> bool:
        if not self.load():
            return False

        try:
            magic = self.read_u32()
            if magic not in self.VERSIONS:
                print(f"Invalid CPLT4 magic number: {magic}, expected one of {self.VERSIONS}")
                return False
            self.data.magic = magic
            
            # Read Header
            self.data.unk1 = self.read_u32()
            self.data.unk2 = self.read_u32()

            # Read Palette
            self.data.palette = self._read_stage_palette()
            
            return True

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error parsing CPLT4 file at offset {self._position}: {e}")
            return False

    def save(self) -> bool:
        try:
            self.start_writing()
            
            self.write_u32(self.data.magic)
            
            # Write Header
            self.write_u32(self.data.unk1)
            self.write_u32(self.data.unk2)
            
            # Write Palette
            self._write_stage_palette(StagePalette(**self.data.palette))
            
            self.finish_writing()
            return self.save_file()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error saving CPLT4 file: {e}")
            return False

    # region Struct R/W (Copied from STG4 tool as they are needed for StagePalette)

    def _read_stage_header(self):
        d = self.data
        d.some_count = self.read_u32()
        d.item_width = self.read_u32()
        d.chunk_width = self.read_u32()
        d.chunk_pow = self.read_u32()
        d.height = self.read_u32()
        d.enable_horizontal_scroll_minimum = self.read_u32()
        d.enable_horizontal_scroll_maximum = self.read_u32()
        d.enable_vertical_scroll_minimum = self.read_u32()
        d.enable_vertical_scroll_maximum = self.read_u32()
        d.horizontal_scroll_minimum_value = self.read_u32()
        d.horizontal_scroll_maximum_value = self.read_u32()
        d.vertical_scroll_minimum_value = self.read_u32()
        d.vertical_scroll_maximum_value = self.read_u32()
        d.frame_rate = self.read_u32()
        d.enable_time_limit = self.read_u32()
        d.time_limit_duration = self.read_u32()
        d.warning_sound_start_time = self.read_u32()
        d.enable_side_scroll = self.read_u32()
        d.enable_vertical_scroll = self.read_u32()
        d.autoscroll_speed = self.read_u32()
        d.vertical_scroll_speed = self.read_u32()
        d.gravity = self.read_f64()
        d.hit_detection_level = self.read_u32()
        d.character_shot_collision_detection_accuracy = self.read_u32()
        d.bgm_number = self.read_u32()
        d.bgm_loop_playback = self.read_u32()
        d.dont_restart_bgm_if_no_change = self.read_u32()
        d.enable_z_coordinate = self.read_u32()
        d.inherit_status_from_stock = self.read_u32()
        d.store_status_to_stock = self.read_u32()
        d.show_status_window = self.read_u32()
        d.switch_scene_immediately_on_clear = self.read_u32()
        d.allow_replay_save = self.read_u32()
        d.show_stage = self.read_u32()
        d.show_ready = self.read_u32()
        d.show_clear = self.read_u32()
        d.show_gameover = self.read_u32()
        d.player_collide = self._read_player_collision()
        d.enemy_collide = self._read_enemy_collision()
        d.item_collision_width = self.read_u32()
        d.item_collision_height = self.read_u32()
        d.player_hitbox = self._read_actor_hitbox()
        d.enemy_hitbox = self._read_actor_hitbox()
        d.undo_max_times = self.read_u32()
        d.x_coordinate_upper_limit = self.read_u32()
        d.y_coordinate_upper_limit = self.read_u32()
        d.unk75 = self.read_u32()
        d.unk76 = self.read_u32()
        d.unk77 = self.read_u32()
        d.unk78 = self.read_u32()
        d.unk79 = self.read_u32()
        d.unk80 = self.read_u32()
        d.unk81 = self.read_u32()
        d.unk82 = self.read_u32()
        d.unk83 = self.read_u32()
        d.unk84 = self.read_u32()
        d.unk85 = self.read_u32()
        d.unk86 = self.read_u32()
        d.disable_damage_outside_screen = self.read_u32()
        d.player_invincibility_from_same_enemy_duration = self.read_u32()
        d.player_invincibility_duration = self.read_u32()
        d.enemy_invincibility_from_same_player_duration = self.read_u32()
        d.enemy_invincibility_duration = self.read_u32()
        
        stage_names_count = self.read_u32() # Should be 1
        d.stage_names = stage_names_count
        if stage_names_count > 0:
            d.stage_name = self.read_std_string()
        
        d.ranking_size = self.read_u32()
        d.ranking_score = self.read_u32()
        d.ranking_remaining_time = self.read_u32()
        d.ranking_clear_time = self.read_u32()
        d.ranking_remaining_hp = self.read_u32()
        d.ranking_remaining_sp = self.read_u32()
        
        d.nonblock_enemy_death = self._read_death_fade()
        d.block_enemy_death = self._read_death_fade()
        d.item_death = self._read_death_fade()
        d.player_death = self._read_death_fade()
        d.enemy_death = self._read_death_fade()

    def _write_stage_header(self):
        d = self.data
        self.write_u32(d.some_count)
        self.write_u32(d.item_width)
        self.write_u32(d.chunk_width)
        self.write_u32(d.chunk_pow)
        self.write_u32(d.height)
        self.write_u32(d.enable_horizontal_scroll_minimum)
        self.write_u32(d.enable_horizontal_scroll_maximum)
        self.write_u32(d.enable_vertical_scroll_minimum)
        self.write_u32(d.enable_vertical_scroll_maximum)
        self.write_u32(d.horizontal_scroll_minimum_value)
        self.write_u32(d.horizontal_scroll_maximum_value)
        self.write_u32(d.vertical_scroll_minimum_value)
        self.write_u32(d.vertical_scroll_maximum_value)
        self.write_u32(d.frame_rate)
        self.write_u32(d.enable_time_limit)
        self.write_u32(d.time_limit_duration)
        self.write_u32(d.warning_sound_start_time)
        self.write_u32(d.enable_side_scroll)
        self.write_u32(d.enable_vertical_scroll)
        self.write_u32(d.autoscroll_speed)
        self.write_u32(d.vertical_scroll_speed)
        self.write_f64(d.gravity)
        self.write_u32(d.hit_detection_level)
        self.write_u32(d.character_shot_collision_detection_accuracy)
        self.write_u32(d.bgm_number)
        self.write_u32(d.bgm_loop_playback)
        self.write_u32(d.dont_restart_bgm_if_no_change)
        self.write_u32(d.enable_z_coordinate)
        self.write_u32(d.inherit_status_from_stock)
        self.write_u32(d.store_status_to_stock)
        self.write_u32(d.show_status_window)
        self.write_u32(d.switch_scene_immediately_on_clear)
        self.write_u32(d.allow_replay_save)
        self.write_u32(d.show_stage)
        self.write_u32(d.show_ready)
        self.write_u32(d.show_clear)
        self.write_u32(d.show_gameover)
        self._write_player_collision(StagePlayerCollision(**d.player_collide))
        self._write_enemy_collision(StageEnemyCollision(**d.enemy_collide))
        self.write_u32(d.item_collision_width)
        self.write_u32(d.item_collision_height)
        self._write_actor_hitbox(StageActorHitbox(**d.player_hitbox))
        self._write_actor_hitbox(StageActorHitbox(**d.enemy_hitbox))
        self.write_u32(d.undo_max_times)
        self.write_u32(d.x_coordinate_upper_limit)
        self.write_u32(d.y_coordinate_upper_limit)
        self.write_u32(d.unk75)
        self.write_u32(d.unk76)
        self.write_u32(d.unk77)
        self.write_u32(d.unk78)
        self.write_u32(d.unk79)
        self.write_u32(d.unk80)
        self.write_u32(d.unk81)
        self.write_u32(d.unk82)
        self.write_u32(d.unk83)
        self.write_u32(d.unk84)
        self.write_u32(d.unk85)
        self.write_u32(d.unk86)
        self.write_u32(d.disable_damage_outside_screen)
        self.write_u32(d.player_invincibility_from_same_enemy_duration)
        self.write_u32(d.player_invincibility_duration)
        self.write_u32(d.enemy_invincibility_from_same_player_duration)
        self.write_u32(d.enemy_invincibility_duration)
        
        self.write_u32(1) # Stage names count, always 1
        self.write_std_string(d.stage_name)
        
        self.write_u32(d.ranking_size)
        self.write_u32(d.ranking_score)
        self.write_u32(d.ranking_remaining_time)
        self.write_u32(d.ranking_clear_time)
        self.write_u32(d.ranking_remaining_hp)
        self.write_u32(d.ranking_remaining_sp)
        
        self._write_death_fade(StageDeathFade(**d.nonblock_enemy_death))
        self._write_death_fade(StageDeathFade(**d.block_enemy_death))
        self._write_death_fade(StageDeathFade(**d.item_death))
        self._write_death_fade(StageDeathFade(**d.player_death))
        self._write_death_fade(StageDeathFade(**d.enemy_death))

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

    def _write_death_fade(self, fade: StageDeathFade):
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

    def _read_player_collision(self) -> StagePlayerCollision:
        coll = StagePlayerCollision()
        coll.walking_block_width = self.read_u32()
        coll.walking_block_height = self.read_u32()
        coll.flying_block_width = self.read_u32()
        coll.flying_block_height = self.read_u32()
        coll.walking_character_width = self.read_u32()
        coll.walking_character_height = self.read_u32()
        coll.flying_character_width = self.read_u32()
        coll.flying_character_height = self.read_u32()
        coll.shot_width = self.read_u32()
        coll.shot_height = self.read_u32()
        coll.item_width = self.read_u32()
        coll.item_height = self.read_u32()
        coll.walking_block_position = self.read_u32()
        coll.flying_block_position = self.read_u32()
        coll.walking_character_position = self.read_u32()
        coll.flying_character_position = self.read_u32()
        coll.block_display = self.read_u32()
        coll.character_display = self.read_u32()
        coll.shot_display = self.read_u32()
        coll.item_display = self.read_u32()
        coll.block_display_color = self.read_u32()
        coll.character_display_color = self.read_u32()
        coll.shot_display_color = self.read_u32()
        coll.item_display_color = self.read_u32()
        return coll
    
    def _write_player_collision(self, coll: StagePlayerCollision):
        self.write_u32(coll.walking_block_width)
        self.write_u32(coll.walking_block_height)
        self.write_u32(coll.flying_block_width)
        self.write_u32(coll.flying_block_height)
        self.write_u32(coll.walking_character_width)
        self.write_u32(coll.walking_character_height)
        self.write_u32(coll.flying_character_width)
        self.write_u32(coll.flying_character_height)
        self.write_u32(coll.shot_width)
        self.write_u32(coll.shot_height)
        self.write_u32(coll.item_width)
        self.write_u32(coll.item_height)
        self.write_u32(coll.walking_block_position)
        self.write_u32(coll.flying_block_position)
        self.write_u32(coll.walking_character_position)
        self.write_u32(coll.flying_character_position)
        self.write_u32(coll.block_display)
        self.write_u32(coll.character_display)
        self.write_u32(coll.shot_display)
        self.write_u32(coll.item_display)
        self.write_u32(coll.block_display_color)
        self.write_u32(coll.character_display_color)
        self.write_u32(coll.shot_display_color)
        self.write_u32(coll.item_display_color)

    def _read_enemy_collision(self) -> StageEnemyCollision:
        coll = StageEnemyCollision()
        coll.walking_block_width = self.read_u32()
        coll.walking_block_height = self.read_u32()
        coll.flying_block_width = self.read_u32()
        coll.flying_block_height = self.read_u32()
        coll.walking_character_width = self.read_u32()
        coll.walking_character_height = self.read_u32()
        coll.flying_character_width = self.read_u32()
        coll.flying_character_height = self.read_u32()
        coll.shot_width = self.read_u32()
        coll.shot_height = self.read_u32()
        coll.walking_block_position = self.read_u32()
        coll.flying_block_position = self.read_u32()
        coll.walking_character_position = self.read_u32()
        coll.flying_character_position = self.read_u32()
        return coll

    def _write_enemy_collision(self, coll: StageEnemyCollision):
        self.write_u32(coll.walking_block_width)
        self.write_u32(coll.walking_block_height)
        self.write_u32(coll.flying_block_width)
        self.write_u32(coll.flying_block_height)
        self.write_u32(coll.walking_character_width)
        self.write_u32(coll.walking_character_height)
        self.write_u32(coll.flying_character_width)
        self.write_u32(coll.flying_character_height)
        self.write_u32(coll.shot_width)
        self.write_u32(coll.shot_height)
        self.write_u32(coll.walking_block_position)
        self.write_u32(coll.flying_block_position)
        self.write_u32(coll.walking_character_position)
        self.write_u32(coll.flying_character_position)
        
    def _read_actor_hitbox(self) -> StageActorHitbox:
        hitbox = StageActorHitbox()
        hitbox.shot_width = self.read_u32()
        hitbox.shot_height = self.read_u32()
        hitbox.character_width = self.read_u32()
        hitbox.character_height = self.read_u32()
        return hitbox

    def _write_actor_hitbox(self, hitbox: StageActorHitbox):
        self.write_u32(hitbox.shot_width)
        self.write_u32(hitbox.shot_height)
        self.write_u32(hitbox.character_width)
        self.write_u32(hitbox.character_height)
    # endregion

    # region Struct R/W
    def _read_basic_condition(self) -> BasicCondition:
        c = BasicCondition()
        c.header = self.read_u32()
        c.type = self.read_u8()
        c.right_side_constant = self.read_u32()
        c.right_side_random_lower_limit = self.read_u32()
        c.right_side_random_upper_limit = self.read_u32()
        c.left_side_status_target = self.read_u8()
        c.left_side_status_number = self.read_u8()
        c.left_side_type = self.read_u8()
        c.left_side_common_variable_or_stage_variable = self.read_u8()
        c.left_side_variable_number = self.read_u16()
        c.left_side_flow_variable_number = self.read_u8()
        c.right_side_type = self.read_u8()
        c.right_side_status_target = self.read_u8()
        c.right_side_status_number = self.read_u8()
        c.right_side_common_variable_or_stage_variable = self.read_u8()
        c.right_side_variable_number = self.read_u16()
        c.right_side_flow_variable_number = self.read_u8()
        c.how_to_compare = self.read_u8()
        c.specify_in_percent = self.read_u8()
        c.left_side_coordinate_type = self.read_u8()
        c.right_side_coordinate_type = self.read_u8()
        c.left_side_gigantic_character_coordinate_position = self.read_u8()
        c.right_side_gigantic_character_coordinate_position = self.read_u8()
        c.unk1 = self.read_u8()
        c.unk2 = self.read_u8()
        c.unk3 = self.read_u8()
        c.unk4 = self.read_u8()
        c.unk5 = self.read_u8()
        return c

    def _write_basic_condition(self, c: BasicCondition):
        self.write_u32(c.header)
        self.write_u8(c.type)
        self.write_u32(c.right_side_constant)
        self.write_u32(c.right_side_random_lower_limit)
        self.write_u32(c.right_side_random_upper_limit)
        self.write_u8(c.left_side_status_target)
        self.write_u8(c.left_side_status_number)
        self.write_u8(c.left_side_type)
        self.write_u8(c.left_side_common_variable_or_stage_variable)
        self.write_u16(c.left_side_variable_number)
        self.write_u8(c.left_side_flow_variable_number)
        self.write_u8(c.right_side_type)
        self.write_u8(c.right_side_status_target)
        self.write_u8(c.right_side_status_number)
        self.write_u8(c.right_side_common_variable_or_stage_variable)
        self.write_u16(c.right_side_variable_number)
        self.write_u8(c.right_side_flow_variable_number)
        self.write_u8(c.how_to_compare)
        self.write_u8(c.specify_in_percent)
        self.write_u8(c.left_side_coordinate_type)
        self.write_u8(c.right_side_coordinate_type)
        self.write_u8(c.left_side_gigantic_character_coordinate_position)
        self.write_u8(c.right_side_gigantic_character_coordinate_position)
        self.write_u8(c.unk1)
        self.write_u8(c.unk2)
        self.write_u8(c.unk3)
        self.write_u8(c.unk4)
        self.write_u8(c.unk5)

    def _read_block(self) -> Block:
        b = Block()
        b.header = self.read_u32()
        b.inherit_palette = self.read_u8()
        b.inherit_palette_data = self.read_u16()
        b.any_of_appearance_conditions_true = self.read_u8()
        b.appearance_condition_once_met_always_true = self.read_u8()
        b.image_number = self.read_u16()
        b.image_type = self.read_u16()
        b.unknown1 = self.read_u8()
        b.in_front_of_character = self.read_u8()
        b.transparency = self.read_u8()
        b.mark_display = self.read_u8()
        b.mark_number = self.read_u8()
        b.unknown2 = self.read_u8()
        b.block_type = self.read_u8()
        b.invalid_faction = self.read_u8()
        b.action = self.read_u8()
        b.action_parameter = self.read_u32()
        b.acquired_item_palette = self.read_u8()
        b.acquired_item_palette_data_number = self.read_u16()
        b.block_summon_invalid = self.read_u8()
        
        strings_count = self.read_u32()
        if strings_count > 0:
            b.name = self.read_std_string()

        b.position_x = self.read_s16()
        b.position_y = self.read_s16()
        b.inherited_data_count = self.read_u32()
        b.inherit_block_name = self.read_u8()
        b.inherit_appearance_condition = self.read_u8()
        b.inherit_image = self.read_u8()
        b.inherit_in_front_of_character = self.read_u8()
        b.inherit_transparency = self.read_u8()
        b.inherit_mark = self.read_u8()
        b.inherit_block_type = self.read_u8()
        b.inherit_invalid_faction = self.read_u8()
        b.inherit_action = self.read_u8()
        b.inherit_acquired_item = self.read_u8()
        b.inherit_block_summon = self.read_u8()
        b.display_conditions = self._read_array(self._read_basic_condition)
        return b

    def _write_block(self, b: Block):
        self.write_u32(b.header)
        self.write_u8(b.inherit_palette)
        self.write_u16(b.inherit_palette_data)
        self.write_u8(b.any_of_appearance_conditions_true)
        self.write_u8(b.appearance_condition_once_met_always_true)
        self.write_u16(b.image_number)
        self.write_u16(b.image_type)
        self.write_u8(b.unknown1)
        self.write_u8(b.in_front_of_character)
        self.write_u8(b.transparency)
        self.write_u8(b.mark_display)
        self.write_u8(b.mark_number)
        self.write_u8(b.unknown2)
        self.write_u8(b.block_type)
        self.write_u8(b.invalid_faction)
        self.write_u8(b.action)
        self.write_u32(b.action_parameter)
        self.write_u8(b.acquired_item_palette)
        self.write_u16(b.acquired_item_palette_data_number)
        self.write_u8(b.block_summon_invalid)
        
        self.write_u32(1) # strings_count, must be 1
        self.write_std_string(b.name)
        
        self.write_s16(b.position_x)
        self.write_s16(b.position_y)
        self.write_u32(b.inherited_data_count)
        self.write_u8(b.inherit_block_name)
        self.write_u8(b.inherit_appearance_condition)
        self.write_u8(b.inherit_image)
        self.write_u8(b.inherit_in_front_of_character)
        self.write_u8(b.inherit_transparency)
        self.write_u8(b.inherit_mark)
        self.write_u8(b.inherit_block_type)
        self.write_u8(b.inherit_invalid_faction)
        self.write_u8(b.inherit_action)
        self.write_u8(b.inherit_acquired_item)
        self.write_u8(b.inherit_block_summon)
        self._write_array([BasicCondition(**i) for i in b.display_conditions], self._write_basic_condition)

    def _read_character(self) -> Character:
        c = Character()
        c.header = self.read_u32()
        c.inherit_palette = self.read_u8()
        c.inherit_palette_data_number = self.read_u16()
        c.any_of_appearance_conditions_true = self.read_u8()
        c.appearance_condition_once_met_always_true = self.read_u8()
        c.facing_right = self.read_u8()
        c.number_of_doubles = self.read_u8()
        c.appearance_position_offset_x_bl = self.read_u16()
        c.appearance_position_offset_x_dot = self.read_u16()
        c.appearance_position_offset_y_bl = self.read_u16()
        c.appearance_position_offset_y_dot = self.read_u16()
        c.appearance_position_offset_x_flip_if_facing_right = self.read_u8()
        c.appearance_position_offset_y_flip_if_facing_right = self.read_u8()
        c.image_number = self.read_u16()
        c.image_type = self.read_u8()
        c.image_offset = self.read_u16()
        c.animation_set = self.read_u16()
        c.z_coordinate = self.read_u8()
        c.transparency = self.read_u8()
        c.initial_character_effect = self.read_u16()
        c.initial_character_effect_execution_type = self.read_u8()
        c.initial_character_effect_loop_execution = self.read_u8()
        c.character_effect_on_death = self.read_u16()
        c.character_effect_on_death_execution_type = self.read_u8()
        c.mark_display = self.read_u8()
        c.mark_number = self.read_u16()
        c.operation = self.read_u16()
        c.faction = self.read_u8()
        c.character_id = self.read_u8()
        c.flying = self.read_u8()
        c.direction_fixed = self.read_u8()
        c.invincible = self.read_u8()
        c.invincible_effect = self.read_u8()
        c.block = self.read_u8()
        c.gigantic = self.read_u8()
        c.synchronize_with_auto_scroll = self.read_u8()
        c.line_of_sight = self.read_u8()
        c.line_of_sight_range = self.read_u8()
        c.hp = self.read_u32()
        c.sp = self.read_u32()
        c.stopping_ease_during_inertial_movement = self.read_u16()
        c.body_hit_detection_range = self.read_u8()
        c.body_hit_power = self.read_u32()
        c.body_hit_impact = self.read_u8()
        c.body_hit_effect = self.read_u16()
        c.defense = self.read_u32()
        c.impact_resistance = self.read_u8()
        c.score = self.read_u32()
        c.holds_item_at_same_position = self.read_u8()
        c.has_group = self.read_u8()
        c.group_number = self.read_u16()
        c.action_condition_range = self.read_u8()
        c.action_condition_judgment_type = self.read_u8()
        
        c.strings_count = self.read_u32()
        if c.strings_count > 0:
            c.character_name = self.read_std_string()
            for _ in range(1, c.strings_count):
                self.read_std_string() # Read and discard extra strings

        c.position_x = self.read_u16()
        c.position_y = self.read_u16()
        c.some_count = self.read_s32()
        c.inherited_data_count = self.read_u32()
        c.inherit_character_name = self.read_u8()
        c.inherit_operation = self.read_u8()
        c.inherit_faction = self.read_u8()
        c.inherit_character_id = self.read_u8()
        c.inherit_appearance_condition = self.read_u8()
        c.inherit_facing_right = self.read_u8()
        c.inherit_number_of_doubles = self.read_u8()
        c.inherit_initial_position_offset_x = self.read_u8()
        c.inherit_initial_position_offset_y = self.read_u8()
        c.inherit_image = self.read_u8()
        c.inherit_animation_set = self.read_u8()
        c.inherit_z_coordinate = self.read_u8()
        c.inherit_transparency = self.read_u8()
        c.inherit_initial_character_effect = self.read_u8()
        c.inherit_character_effect_on_death = self.read_u8()
        c.inherit_mark = self.read_u8()
        c.inherit_direction_fixed = self.read_u8()
        c.inherit_flying = self.read_u8()
        c.inherit_invincible = self.read_u8()
        c.inherit_block = self.read_u8()
        c.inherit_gigantic = self.read_u8()
        c.inherit_synchronize_with_auto_scroll = self.read_u8()
        c.inherit_line_of_sight = self.read_u8()
        c.inherit_hp = self.read_u8()
        c.inherit_sp = self.read_u8()
        c.inherit_body_hit_detection_range = self.read_u8()
        c.inherit_body_hit_power = self.read_u8()
        c.inherit_body_hit_impact = self.read_u8()
        c.inherit_body_hit_effect = self.read_u8()
        c.inherit_defense = self.read_u8()
        c.inherit_impact_resistance = self.read_u8()
        c.inherit_stopping_ease_during_inertial_movement = self.read_u8()
        c.inherit_action_condition = self.read_u8()
        c.inherit_group = self.read_u8()
        c.inherit_score = self.read_u8()
        c.inherit_holds_item_at_same_position = self.read_u8()
        c.inherit_action = self.read_u8()
        
        c.conditions = self._read_array(self._read_basic_condition)
        c.flows = self._read_array(self._read_flow)
        return c

    def _write_character(self, c: Character):
        self.write_u32(c.header)
        self.write_u8(c.inherit_palette)
        self.write_u16(c.inherit_palette_data_number)
        self.write_u8(c.any_of_appearance_conditions_true)
        self.write_u8(c.appearance_condition_once_met_always_true)
        self.write_u8(c.facing_right)
        self.write_u8(c.number_of_doubles)
        self.write_u16(c.appearance_position_offset_x_bl)
        self.write_u16(c.appearance_position_offset_x_dot)
        self.write_u16(c.appearance_position_offset_y_bl)
        self.write_u16(c.appearance_position_offset_y_dot)
        self.write_u8(c.appearance_position_offset_x_flip_if_facing_right)
        self.write_u8(c.appearance_position_offset_y_flip_if_facing_right)
        self.write_u16(c.image_number)
        self.write_u8(c.image_type)
        self.write_u16(c.image_offset)
        self.write_u16(c.animation_set)
        self.write_u8(c.z_coordinate)
        self.write_u8(c.transparency)
        self.write_u16(c.initial_character_effect)
        self.write_u8(c.initial_character_effect_execution_type)
        self.write_u8(c.initial_character_effect_loop_execution)
        self.write_u16(c.character_effect_on_death)
        self.write_u8(c.character_effect_on_death_execution_type)
        self.write_u8(c.mark_display)
        self.write_u16(c.mark_number)
        self.write_u16(c.operation)
        self.write_u8(c.faction)
        self.write_u8(c.character_id)
        self.write_u8(c.flying)
        self.write_u8(c.direction_fixed)
        self.write_u8(c.invincible)
        self.write_u8(c.invincible_effect)
        self.write_u8(c.block)
        self.write_u8(c.gigantic)
        self.write_u8(c.synchronize_with_auto_scroll)
        self.write_u8(c.line_of_sight)
        self.write_u8(c.line_of_sight_range)
        self.write_u32(c.hp)
        self.write_u32(c.sp)
        self.write_u16(c.stopping_ease_during_inertial_movement)
        self.write_u8(c.body_hit_detection_range)
        self.write_u32(c.body_hit_power)
        self.write_u8(c.body_hit_impact)
        self.write_u16(c.body_hit_effect)
        self.write_u32(c.defense)
        self.write_u8(c.impact_resistance)
        self.write_u32(c.score)
        self.write_u8(c.holds_item_at_same_position)
        self.write_u8(c.has_group)
        self.write_u16(c.group_number)
        self.write_u8(c.action_condition_range)
        self.write_u8(c.action_condition_judgment_type)

        self.write_u32(1) # c.strings_count
        self.write_std_string(c.character_name)

        self.write_u16(c.position_x)
        self.write_u16(c.position_y)
        self.write_s32(c.some_count)
        self.write_u32(c.inherited_data_count)
        self.write_u8(c.inherit_character_name)
        self.write_u8(c.inherit_operation)
        self.write_u8(c.inherit_faction)
        self.write_u8(c.inherit_character_id)
        self.write_u8(c.inherit_appearance_condition)
        self.write_u8(c.inherit_facing_right)
        self.write_u8(c.inherit_number_of_doubles)
        self.write_u8(c.inherit_initial_position_offset_x)
        self.write_u8(c.inherit_initial_position_offset_y)
        self.write_u8(c.inherit_image)
        self.write_u8(c.inherit_animation_set)
        self.write_u8(c.inherit_z_coordinate)
        self.write_u8(c.inherit_transparency)
        self.write_u8(c.inherit_initial_character_effect)
        self.write_u8(c.inherit_character_effect_on_death)
        self.write_u8(c.inherit_mark)
        self.write_u8(c.inherit_direction_fixed)
        self.write_u8(c.inherit_flying)
        self.write_u8(c.inherit_invincible)
        self.write_u8(c.inherit_block)
        self.write_u8(c.inherit_gigantic)
        self.write_u8(c.inherit_synchronize_with_auto_scroll)
        self.write_u8(c.inherit_line_of_sight)
        self.write_u8(c.inherit_hp)
        self.write_u8(c.inherit_sp)
        self.write_u8(c.inherit_body_hit_detection_range)
        self.write_u8(c.inherit_body_hit_power)
        self.write_u8(c.inherit_body_hit_impact)
        self.write_u8(c.inherit_body_hit_effect)
        self.write_u8(c.inherit_defense)
        self.write_u8(c.inherit_impact_resistance)
        self.write_u8(c.inherit_stopping_ease_during_inertial_movement)
        self.write_u8(c.inherit_action_condition)
        self.write_u8(c.inherit_group)
        self.write_u8(c.inherit_score)
        self.write_u8(c.inherit_holds_item_at_same_position)
        self.write_u8(c.inherit_action)
        
        self._write_array([BasicCondition(**i) for i in c.conditions], self._write_basic_condition)
        self._write_array([Flow(**i) for i in c.flows], self._write_flow)

    def _read_item(self) -> Item:
        i = Item()
        i.header = self.read_u32()
        i.inherit_palette = self.read_u8()
        i.inherit_palette_data_number = self.read_u16()
        i.any_of_appearance_conditions_true = self.read_u8()
        i.appearance_condition_once_met_always_true = self.read_u8()
        i.appearance_position_offset_x_dot = self.read_u16()
        i.appearance_position_offset_y_dot = self.read_u16()
        i.image_number = self.read_u16()
        i.image_type = self.read_u8()
        i.frame = self.read_u16()
        i.z_coordinate = self.read_u8()
        i.transparency = self.read_u8()
        i.mark_display = self.read_u8()
        i.mark_number = self.read_u16()
        i.display_above_head_on_acquisition = self.read_u8()
        i.acquisition_type = self.read_u8()
        i.gigantic = self.read_u8()
        i.sound_effect = self.read_u16()
        
        i.item_name_length = self.read_u32()
        if i.item_name_length > 0:
            i.item_name = self.read_std_string()

        i.position_x = self.read_u16()
        i.position_y = self.read_u16()
        i.number_of_inherited_data = self.read_u32()
        i.inherit_item_name = self.read_u8()
        i.inherit_appearance_condition = self.read_u8()
        i.inherit_initial_position_offset_x = self.read_u8()
        i.inherit_initial_position_offset_y = self.read_u8()
        i.inherit_image = self.read_u8()
        i.inherit_z_coordinate = self.read_u8()
        i.inherit_transparency = self.read_u8()
        i.inherit_mark = self.read_u8()
        i.inherit_gigantic = self.read_u8()
        i.inherit_acquisition_type = self.read_u8()
        i.inherit_display_above_head_on_acquisition = self.read_u8()
        i.inherit_sound_effect = self.read_u8()
        i.inherit_effect = self.read_u8()
        i.conditions = self._read_array(self._read_basic_condition)
        i.item_effects = self._read_array(self._read_item_effect)
        return i

    def _write_item(self, i: Item):
        self.write_u32(i.header)
        self.write_u8(i.inherit_palette)
        self.write_u16(i.inherit_palette_data_number)
        self.write_u8(i.any_of_appearance_conditions_true)
        self.write_u8(i.appearance_condition_once_met_always_true)
        self.write_u16(i.appearance_position_offset_x_dot)
        self.write_u16(i.appearance_position_offset_y_dot)
        self.write_u16(i.image_number)
        self.write_u8(i.image_type)
        self.write_u16(i.frame)
        self.write_u8(i.z_coordinate)
        self.write_u8(i.transparency)
        self.write_u8(i.mark_display)
        self.write_u16(i.mark_number)
        self.write_u8(i.display_above_head_on_acquisition)
        self.write_u8(i.acquisition_type)
        self.write_u8(i.gigantic)
        self.write_u16(i.sound_effect)
        
        self.write_u32(1) # Item name count, must be 1
        self.write_std_string(i.item_name)
        
        self.write_u16(i.position_x)
        self.write_u16(i.position_y)
        self.write_u32(i.number_of_inherited_data)
        self.write_u8(i.inherit_item_name)
        self.write_u8(i.inherit_appearance_condition)
        self.write_u8(i.inherit_initial_position_offset_x)
        self.write_u8(i.inherit_initial_position_offset_y)
        self.write_u8(i.inherit_image)
        self.write_u8(i.inherit_z_coordinate)
        self.write_u8(i.inherit_transparency)
        self.write_u8(i.inherit_mark)
        self.write_u8(i.inherit_gigantic)
        self.write_u8(i.inherit_acquisition_type)
        self.write_u8(i.inherit_display_above_head_on_acquisition)
        self.write_u8(i.inherit_sound_effect)
        self.write_u8(i.inherit_effect)
        self._write_array([BasicCondition(**i) for i in i.conditions], self._write_basic_condition)
        self._write_array([ItemEffect(**i) for i in i.item_effects], self._write_item_effect)

    def _read_flow(self) -> Flow:
        f = Flow()
        f.header = self.read_u32()
        if f.header != 10:
            raise ValueError(f"Invalid Flow header: expected 10, got {f.header}")
        f.id = self.read_u8()
        f.group = self.read_u8()
        f.test_play_only = self.read_u8()
        f.basic_condition_judgment_type = self.read_u8()
        f.basic_condition_once_met_always_met = self.read_u8()
        f.timing = self.read_u8()
        f.target_character_involved_in_timing = self.read_u8()
        f.target_number_of_character_involved_in_timing = self.read_u8()
        f.ease_of_input_with_multiple_key_conditions = self.read_u8()
        f.allow_continuous_execution_by_holding_key = self.read_u8()
        
        f.memo_count = self.read_u32()
        # if f.memo_count > 0:
        f.memo = self.read_std_string()

        f.conditions = self._read_array(self._read_basic_condition)
        f.key_conditions = self._read_array(self._read_key_condition)
        f.commands = self._read_array(self._read_command)
        return f

    def _write_flow(self, f: Flow):
        self.write_u32(f.header or 10)
        self.write_u8(f.id)
        self.write_u8(f.group)
        self.write_u8(f.test_play_only)
        self.write_u8(f.basic_condition_judgment_type)
        self.write_u8(f.basic_condition_once_met_always_met)
        self.write_u8(f.timing)
        self.write_u8(f.target_character_involved_in_timing)
        self.write_u8(f.target_number_of_character_involved_in_timing)
        self.write_u8(f.ease_of_input_with_multiple_key_conditions)
        self.write_u8(f.allow_continuous_execution_by_holding_key)
        
        self.write_u32(1)
        self.write_std_string(f.memo)
            
        self._write_array([BasicCondition(**i) for i in f.conditions], self._write_basic_condition)
        self._write_array([KeyCondition(**i) for i in f.key_conditions], self._write_key_condition)
        self._write_array([Command(**i) for i in f.commands], self._write_command)

    def _read_key_condition(self) -> KeyCondition:
        kc = KeyCondition()
        kc.header = self.read_u32()
        kc.right_and_left_to_front_and_back = self.read_u8()
        kc.minimum_input_time = self.read_u16()
        kc.maximum_input_time = self.read_u16()
        kc.input_time_1_to_infinity = self.read_u8()
        kc.judgment_type = self.read_u8()
        kc.unknown = self.read_u32()
        kc.number_of_key_data = self.read_u32()
        kc.direction_key_neutral = self.read_u8()
        kc.left_key = self.read_u8()
        kc.right_key = self.read_u8()
        kc.up_key = self.read_u8()
        kc.down_key = self.read_u8()
        kc.up_left_key = self.read_u8()
        kc.down_left_key = self.read_u8()
        kc.up_right_key = self.read_u8()
        kc.down_right_key = self.read_u8()
        kc.any_direction_key = self.read_u8()
        kc.action_key_neutral = self.read_u8()
        kc.z_key = self.read_u8()
        kc.x_key = self.read_u8()
        kc.c_key = self.read_u8()
        kc.v_key = self.read_u8()
        kc.a_key = self.read_u8()
        kc.s_key = self.read_u8()
        kc.d_key = self.read_u8()
        kc.f_key = self.read_u8()
        return kc
    
    def _write_key_condition(self, kc: KeyCondition):
        self.write_u32(kc.header)
        self.write_u8(kc.right_and_left_to_front_and_back)
        self.write_u16(kc.minimum_input_time)
        self.write_u16(kc.maximum_input_time)
        self.write_u8(kc.input_time_1_to_infinity)
        self.write_u8(kc.judgment_type)
        self.write_u32(kc.unknown)
        self.write_u32(kc.number_of_key_data)
        self.write_u8(kc.direction_key_neutral)
        self.write_u8(kc.left_key)
        self.write_u8(kc.right_key)
        self.write_u8(kc.up_key)
        self.write_u8(kc.down_key)
        self.write_u8(kc.up_left_key)
        self.write_u8(kc.down_left_key)
        self.write_u8(kc.up_right_key)
        self.write_u8(kc.down_right_key)
        self.write_u8(kc.any_direction_key)
        self.write_u8(kc.action_key_neutral)
        self.write_u8(kc.z_key)
        self.write_u8(kc.x_key)
        self.write_u8(kc.c_key)
        self.write_u8(kc.v_key)
        self.write_u8(kc.a_key)
        self.write_u8(kc.s_key)
        self.write_u8(kc.d_key)
        self.write_u8(kc.f_key)

    def _read_stage_palette(self) -> StagePalette:
        p = StagePalette()
        p.blocks = self._read_array(self._read_block)
        p.characters = self._read_array(self._read_character)
        p.items = self._read_array(self._read_item)
        return p

    def _write_stage_palette(self, p: StagePalette):
        self._write_array([Block(**i) for i in p.blocks], self._write_block)
        self._write_array([Character(**i) for i in p.characters], self._write_character)
        self._write_array([Item(**i) for i in p.items], self._write_item)

    def _read_stage_block(self) -> StageBlock:
        sb = StageBlock()
        sb.position = self.read_u32()
        sb.block = self._read_block()
        return sb

    def _write_stage_block(self, sb: StageBlock):
        self.write_u32(sb.position)
        self._write_block(Block(**sb.block))

    def _read_stage_character(self) -> StageCharacter:
        sc = StageCharacter()
        sc.position = self.read_u32()
        sc.character = self._read_character()
        return sc

    def _write_stage_character(self, sc: StageCharacter):
        self.write_u32(sc.position)
        self._write_character(Character(**sc.character))

    def _read_stage_item(self) -> StageItem:
        si = StageItem()
        si.position = self.read_u32()
        si.item = self._read_item()
        return si
    
    def _write_stage_item(self, si: StageItem):
        self.write_u32(si.position)
        self._write_item(si.item)

    def _read_background(self) -> Background:
        b = Background()
        b.start = self.read_u32()
        b.display_from_start = self.read_u32()
        b.specified_by_color = self.read_u32()
        b.color_number = self.read_u32()
        b.display_in_front_of_character = self.read_u32()
        b.horizontal_scroll_speed = self.read_f64()
        b.vertical_scroll_speed = self.read_f64()
        b.horizontal_auto_scroll = self.read_u32()
        b.vertical_auto_scroll = self.read_u32()
        b.horizontal_auto_scroll_speed = self.read_f64()
        b.vertical_auto_scroll_speed = self.read_f64()
        b.bytes61_80 = self.read_bytes(20)
        b.image_path = self.read_std_string()
        return b

    def _write_background(self, b: Background):
        self.write_u32(b.start)
        self.write_u32(b.display_from_start)
        self.write_u32(b.specified_by_color)
        self.write_u32(b.color_number)
        self.write_u32(b.display_in_front_of_character)
        self.write_f64(b.horizontal_scroll_speed)
        self.write_f64(b.vertical_scroll_speed)
        self.write_u32(b.horizontal_auto_scroll)
        self.write_u32(b.vertical_auto_scroll)
        self.write_f64(b.horizontal_auto_scroll_speed)
        self.write_f64(b.vertical_auto_scroll_speed)
        self.write_bytes(b.bytes61_80)
        self.write_std_string(b.image_path)

    def _read_stage_var(self) -> StageVar:
        sv = StageVar()
        sv.unk = self.read_u32()
        sv.count = self.read_u32()
        sv.var_name = self.read_std_string()
        return sv

    def _write_stage_var(self, sv: StageVar):
        self.write_u32(sv.unk)
        self.write_u32(sv.count)
        self.write_std_string(sv.var_name)

    # endregion

    # region Command/Effect Details R/W (Copied from STG4 tool)
    def _read_command(self) -> Command:
        cmd = Command()
        cmd.header = self.read_u32()
        if cmd.header != 8:
            raise ValueError(f"Invalid Command header: expected 8, got {cmd.header}")
        cmd.unk1 = self.read_u8()
        cmd.type = self.read_u8()
        # print(cmd.type, hex(self._position - 1))
        
        # Dispatch to the correct details reader based on type
        reader_map = {
            1: self._read_wait_details,
            2: self._read_linear_movement_details,
            3: self._read_generic_movement_details, # GroundMovement
            4: self._read_generic_movement_details, # CircularMovement
            5: self._read_generic_movement_details, # ChargeMovement
            6: self._read_generic_movement_details, # GuidedMovement
            7: self._read_generic_movement_details, # ScreenOutsideAvoidanceMovement
            8: self._read_generic_movement_details, # MovementInvalidation
            9: self._read_direction_change_details,
            10: self._read_jump_details,
            11: self._read_shot_details,
            12: self._read_sword_details,
            13: self._read_block_summon_details, # BlockSummon
            14: self._read_chara_summon_details, # CharacterSummon
            15: self._read_item_summon_details, # ItemSummon
            16: self._read_flow_operation_details,
            17: self._read_stage_clear_details,
            18: self._read_game_wait_details,
            19: self._read_message_details,
            20: self._read_warp_details,
            21: self._read_target_setting_details,
            22: self._read_status_operation_details,
            23: self._read_status_operation2_details,
            24: self._read_disappearance_details,
            25: self._read_item_acquisition_details,
            26: self._read_graphic_change_details,
            27: self._read_basic_animation_set_change_details,
            28: self._read_animation_execution_details,
            29: self._read_effect_execution_details,
            30: self._read_character_effect_execution_details,
            31: self._read_screen_effect_execution_details,
            32: self._read_picture_display_details,
            33: self._read_screen_color_change_details,
            34: self._read_background_change_details,
            35: self._read_sound_effect_playback_details,
            36: self._read_bgm_playback_details,
            37: self._read_code_execution_details,
            38: self._read_arrangement_details,
            39: self._read_loop_details,
        }
        reader_func = reader_map.get(cmd.type)
        if reader_func:
            cmd.details = reader_func()
        else:
            raise ValueError(f"Unknown command type: {cmd.type}")
            
        return cmd

    def _write_command(self, cmd: Command):
        self.write_u32(cmd.header or 8)
        self.write_u8(cmd.unk1)
        self.write_u8(cmd.type)

        writer_map = {
            1: self._write_wait_details,
            2: self._write_linear_movement_details,
            3: self._write_generic_movement_details,
            4: self._write_generic_movement_details,
            5: self._write_generic_movement_details,
            6: self._write_generic_movement_details,
            7: self._write_generic_movement_details,
            8: self._write_generic_movement_details,
            9: self._write_direction_change_details,
            10: self._write_jump_details,
            11: self._write_shot_details,
            12: self._write_sword_details,
            13: self._write_summon_details,
            14: self._write_summon_details,
            15: self._write_item_summon_details,
            16: self._write_flow_operation_details,
            17: self._write_stage_clear_details,
            18: self._write_game_wait_details,
            19: self._write_message_details,
            20: self._write_warp_details,
            21: self._write_target_setting_details,
            22: self._write_status_operation_details,
            23: self._write_status_operation2_details,
            24: self._write_disappearance_details,
            25: self._write_item_acquisition_details,
            26: self._write_graphic_change_details,
            27: self._write_basic_animation_set_change_details,
            28: self._write_animation_execution_details,
            29: self._write_effect_execution_details,
            30: self._write_character_effect_execution_details,
            31: self._write_screen_effect_execution_details,
            32: self._write_picture_display_details,
            33: self._write_screen_color_change_details,
            34: self._write_background_change_details,
            35: self._write_sound_effect_playback_details,
            36: self._write_bgm_playback_details,
            37: self._write_code_execution_details,
            38: self._write_arrangement_details,
            39: self._write_loop_details,
        }

        command_details_map = {
            1: WaitDetails, 2: LinearMovementDetails, 3: GenericMovementDetails,
            4: GenericMovementDetails, 5: GenericMovementDetails, 6: GenericMovementDetails,
            7: GenericMovementDetails, 8: GenericMovementDetails, 9: DirectionChangeDetails,
            10: JumpDetails, 11: ShotDetails, 12: SwordDetails, 13: SummonDetails,
            14: SummonDetails, 15: ItemSummonDetails, 16: FlowOperationDetails,
            17: StageClearDetails, 18: GameWaitDetails, 19: MessageDetails,
            20: WarpDetails, 21: TargetSettingDetails, 22: StatusOperationDetails,
            23: StatusOperation2Details, 24: DisappearanceDetails, 25: ItemAcquisitionDetails,
            26: GraphicChangeDetails, 27: BasicAnimationSetChangeDetails,
            28: AnimationExecutionDetails, 29: EffectExecutionDetails,
            30: CharacterEffectExecutionDetails, 31: ScreenEffectExecutionDetails,
            32: PictureDisplayDetails, 33: ScreenColorChangeDetails,
            34: BackgroundChangeDetails, 35: SoundEffectPlaybackDetails,
            36: BGMPlaybackDetails, 37: CodeExecutionDetails, 38: ArrangementDetails,
            39: LoopDetails
        }
        
        writer_func = writer_map.get(cmd.type)
        details_class = command_details_map.get(cmd.type)
        if writer_func and details_class:
            details_data = cmd.details
            if isinstance(details_data, dict):
                details_obj = details_class(**details_data)
            else:
                details_obj = details_data
            
            writer_func(details_obj)
        else:
            raise ValueError(f"Unknown command type to write: {cmd.type}")


    def _read_item_effect(self) -> ItemEffect:
        effect = ItemEffect()
        effect.header = self.read_u32()
        if effect.header != 8:
            raise ValueError(f"Invalid item effect header: expected 8, got {effect.header}")
        effect.unk1 = self.read_s8()
        effect.type = self.read_u8()

        reader_map = {
            1: self._read_flow_change_details,
            2: self._read_stage_clear_details,
            3: self._read_game_wait_details,
            4: self._read_message_details,
            5: self._read_warp_details,
            7: self._read_status_operation_details,
            8: self._read_status_operation2_details,
            9: self._read_disappearance_details,
            10: self._read_item_acquisition_details,
            11: self._read_graphic_change_details,
            12: self._read_basic_animation_set_change_details,
            13: self._read_animation_execution_details,
            14: self._read_effect_execution_details,
            15: self._read_character_effect_execution_details,
            16: self._read_screen_effect_execution_details,
            17: self._read_picture_display_details,
            18: self._read_screen_color_change_details,
            19: self._read_background_change_details,
            20: self._read_sound_effect_playback_details,
            21: self._read_bgm_playback_details,
            22: self._read_code_execution_details,
            23: self._read_arrangement_details,
            24: self._read_loop_details,
        }
        reader_func = reader_map.get(effect.type)
        if reader_func:
            effect.details = reader_func()
        else:
            raise ValueError(f"Unknown item effect type: {effect.type}")

        return effect

    def _write_item_effect(self, effect: ItemEffect):
        self.write_u32(effect.header or 8)
        self.write_s8(effect.unk1)
        self.write_u8(effect.type)

        writer_map = {
            1: self._write_flow_change_details,
            2: self._write_stage_clear_details,
            3: self._write_game_wait_details,
            4: self._write_message_details,
            5: self._write_warp_details,
            7: self._write_status_operation_details,
            8: self._write_status_operation2_details,
            9: self._write_disappearance_details,
            10: self._write_item_acquisition_details,
            11: self._write_graphic_change_details,
            12: self._write_basic_animation_set_change_details,
            13: self._write_animation_execution_details,
            14: self._write_effect_execution_details,
            15: self._write_character_effect_execution_details,
            16: self._write_screen_effect_execution_details,
            17: self._write_picture_display_details,
            18: self._write_screen_color_change_details,
            19: self._write_background_change_details,
            20: self._write_sound_effect_playback_details,
            21: self._write_bgm_playback_details,
            22: self._write_code_execution_details,
            23: self._write_arrangement_details,
            24: self._write_loop_details,
        }

        item_effect_details_map = {
            1: FlowChangeDetails, 2: StageClearDetails, 3: GameWaitDetails,
            4: MessageDetails, 5: WarpDetails, 7: StatusOperationDetails,
            8: StatusOperation2Details, 9: DisappearanceDetails, 10: ItemAcquisitionDetails,
            11: GraphicChangeDetails, 12: BasicAnimationSetChangeDetails,
            13: AnimationExecutionDetails, 14: EffectExecutionDetails,
            15: CharacterEffectExecutionDetails, 16: ScreenEffectExecutionDetails,
            17: PictureDisplayDetails, 18: ScreenColorChangeDetails,
            19: BackgroundChangeDetails, 20: SoundEffectPlaybackDetails,
            21: BGMPlaybackDetails, 22: CodeExecutionDetails, 23: ArrangementDetails,
            24: LoopDetails
        }
            
        writer_func = writer_map.get(effect.type)
        details_class = item_effect_details_map.get(effect.type)

        if writer_func and details_class:
            details_data = effect.details
            if isinstance(details_data, dict):
                details_obj = details_class(**details_data)
            else:
                details_obj = details_data

            writer_func(details_obj)
        else:
            raise ValueError(f"Unknown item effect type to write: {effect.type}")

    # The implementation for each _read_*_details and _write_*_details follows
    # Due to the large number and repetitive nature, they are defined below.
    # Note: I've created methods for each specific detail type for clarity.

    def _read_flow_change_details(self) -> FlowChangeDetails:
        d = FlowChangeDetails()
        d.bytes1_30 = self.read_bytes(30)
        d.flows = self._read_array(self._read_flow)
        d.bytes69_72 = self.read_bytes(4)
        d.operation = self.read_u32()
        d.bytes77_80 = self.read_bytes(4)
        return d

    def _write_flow_change_details(self, d: FlowChangeDetails):
        self.write_bytes(d.bytes1_30)
        self._write_array([Flow(**i) for i in d.flows], self._write_flow)
        self.write_bytes(d.bytes69_72)
        self.write_u32(d.operation)
        self.write_bytes(d.bytes77_80)

    def _read_stage_clear_details(self) -> StageClearDetails:
        d = StageClearDetails()
        d.bytes1_14 = self.read_bytes(14)
        d.path = self.read_std_string()
        d.bytes19_38 = self.read_bytes(20)
        d.stage_transition = self.read_u32()
        d.number = self.read_u32()
        d.change_world_map_position = self.read_u32()
        d.world_map_position_x = self.read_u32()
        d.world_map_position_y = self.read_u32()
        d.change_initial_position = self.read_u32()
        d.initial_position_x = self.read_u32()
        d.initial_position_y = self.read_u32()
        d.initial_position_main_character_direction = self.read_u32()
        d.execute_autosave = self.read_u32()
        d.add_clear_text_to_replay = self.read_u32()
        return d
    
    def _write_stage_clear_details(self, d: StageClearDetails):
        self.write_bytes(d.bytes1_14)
        self.write_std_string(d.path)
        self.write_bytes(d.bytes19_38)
        self.write_u32(d.stage_transition)
        self.write_u32(d.number)
        self.write_u32(d.change_world_map_position)
        self.write_u32(d.world_map_position_x)
        self.write_u32(d.world_map_position_y)
        self.write_u32(d.change_initial_position)
        self.write_u32(d.initial_position_x)
        self.write_u32(d.initial_position_y)
        self.write_u32(d.initial_position_main_character_direction)
        self.write_u32(d.execute_autosave)
        self.write_u32(d.add_clear_text_to_replay)

    def _read_game_wait_details(self) -> GameWaitDetails:
        d = GameWaitDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.bytes6_38 = self.read_bytes(33)
        d.game_wait_execution_time = self.read_u32()
        return d

    def _write_game_wait_details(self, d: GameWaitDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_bytes(d.bytes6_38)
        self.write_u32(d.game_wait_execution_time)

    def _read_message_details(self) -> MessageDetails:
        d = MessageDetails()
        d.bytes1_14 = self.read_bytes(14)
        d.message = self.read_std_string()
        d.bytes19_38 = self.read_bytes(20)
        d.display_position_specification_method = self.read_u32()
        d.coordinate_x = self.read_u32()
        d.coordinate_y = self.read_u32()
        d.display_position_offset_x = self.read_u32()
        d.display_position_offset_y = self.read_u32()
        d.auto_adjust_to_not_go_off_screen = self.read_u32()
        d.display_time_specification_method = self.read_u32()
        d.display_time = self.read_u32()
        d.pause = self.read_u32()
        d.display_variables = self.read_u32()
        d.follow_screen = self.read_u32()
        d.auto_update = self.read_u32()
        d.message_id_present = self.read_u32()
        d.message_id = self.read_u32()
        d.window_display = self.read_u32()
        d.message_clear = self.read_u32()
        d.update_interval = self.read_u32()
        d.instant_display = self.read_u32()
        d.coordinate_unit = self.read_u32()
        d.set_options = self.read_u32()
        d.assign_return_value_to_flow_variable = self.read_u32()
        return d
    
    def _write_message_details(self, d: MessageDetails):
        self.write_bytes(d.bytes1_14)
        self.write_std_string(d.message)
        self.write_bytes(d.bytes19_38)
        self.write_u32(d.display_position_specification_method)
        self.write_u32(d.coordinate_x)
        self.write_u32(d.coordinate_y)
        self.write_u32(d.display_position_offset_x)
        self.write_u32(d.display_position_offset_y)
        self.write_u32(d.auto_adjust_to_not_go_off_screen)
        self.write_u32(d.display_time_specification_method)
        self.write_u32(d.display_time)
        self.write_u32(d.pause)
        self.write_u32(d.display_variables)
        self.write_u32(d.follow_screen)
        self.write_u32(d.auto_update)
        self.write_u32(d.message_id_present)
        self.write_u32(d.message_id)
        self.write_u32(d.window_display)
        self.write_u32(d.message_clear)
        self.write_u32(d.update_interval)
        self.write_u32(d.instant_display)
        self.write_u32(d.coordinate_unit)
        self.write_u32(d.set_options)
        self.write_u32(d.assign_return_value_to_flow_variable)

    def _read_wait_details(self) -> WaitDetails:
        d = WaitDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.bytes = self.read_bytes(33)
        return d
    
    def _write_wait_details(self, d: WaitDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_bytes(d.bytes)

    def _read_linear_movement_details(self) -> LinearMovementDetails:
        d = LinearMovementDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.bytes6_8 = self.read_bytes(3)
        d.animation_and_other_type = self.read_u16()
        d.bytes11_26 = self.read_bytes(16)
        d.movement_direction_setting_type = self.read_u8()
        d.movement_direction_direction = self.read_u8()
        d.movement_direction_angle = self.read_u16()
        d.movement_direction_angle_double = self.read_u16()
        d.movement_direction_angle_reverse_rotation_if_facing_right = self.read_u8()
        d.movement_direction_target_x_present = self.read_u8()
        d.movement_direction_target_y_present = self.read_u8()
        d.movement_direction_target_x = self.read_u16()
        d.movement_direction_target_y = self.read_u16()
        d.movement_direction_target_x_dot = self.read_u16()
        d.movement_direction_target_y_dot = self.read_u16()
        d.movement_direction_target_type = self.read_u8()
        d.movement_direction_target_coordinate_unit = self.read_u8()
        d.byte46 = self.read_bytes(1)
        d.movement_direction_execute_until_target_coordinate_reached = self.read_u8()
        d.movement_direction_invalidate_horizontal_movement = self.read_u8()
        d.movement_direction_invalidate_vertical_movement = self.read_u8()
        d.movement_direction_target_x_flip_if_facing_right = self.read_u8()
        d.movement_direction_target_y_flip_if_facing_right = self.read_u8()
        d.movement_direction_reverse_speed_if_direction_changes = self.read_u8()
        d.movement_direction_prevent_blur = self.read_u8()
        d.movement_direction_dont_change_character_direction = self.read_u8()
        d.time_speed_distance_setting_type = self.read_u8()
        d.time_speed_distance_speed = self.read_u16()
        d.time_speed_distance_speed_double = self.read_u16()
        d.time_speed_distance_distance = self.read_u16()
        d.time_speed_distance_distance_double = self.read_u16()
        d.time_speed_distance_distance_unit = self.read_u8()
        d.bytes65_68 = self.read_bytes(4)
        d.inertia_present = self.read_u8()
        d.inertia_max_speed = self.read_u16()
        d.inertia_speed_correction_on_direction_change = self.read_f64()
        d.animation_type = self.read_u8()
        d.bytes81_101 = self.read_bytes(21)
        return d
    
    def _write_linear_movement_details(self, d: LinearMovementDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_bytes(d.bytes6_8)
        self.write_u16(d.animation_and_other_type)
        self.write_bytes(d.bytes11_26)
        self.write_u8(d.movement_direction_setting_type)
        self.write_u8(d.movement_direction_direction)
        self.write_u16(d.movement_direction_angle)
        self.write_u16(d.movement_direction_angle_double)
        self.write_u8(d.movement_direction_angle_reverse_rotation_if_facing_right)
        self.write_u8(d.movement_direction_target_x_present)
        self.write_u8(d.movement_direction_target_y_present)
        self.write_u16(d.movement_direction_target_x)
        self.write_u16(d.movement_direction_target_y)
        self.write_u16(d.movement_direction_target_x_dot)
        self.write_u16(d.movement_direction_target_y_dot)
        self.write_u8(d.movement_direction_target_type)
        self.write_u8(d.movement_direction_target_coordinate_unit)
        self.write_bytes(d.byte46)
        self.write_u8(d.movement_direction_execute_until_target_coordinate_reached)
        self.write_u8(d.movement_direction_invalidate_horizontal_movement)
        self.write_u8(d.movement_direction_invalidate_vertical_movement)
        self.write_u8(d.movement_direction_target_x_flip_if_facing_right)
        self.write_u8(d.movement_direction_target_y_flip_if_facing_right)
        self.write_u8(d.movement_direction_reverse_speed_if_direction_changes)
        self.write_u8(d.movement_direction_prevent_blur)
        self.write_u8(d.movement_direction_dont_change_character_direction)
        self.write_u8(d.time_speed_distance_setting_type)
        self.write_u16(d.time_speed_distance_speed)
        self.write_u16(d.time_speed_distance_speed_double)
        self.write_u16(d.time_speed_distance_distance)
        self.write_u16(d.time_speed_distance_distance_double)
        self.write_u8(d.time_speed_distance_distance_unit)
        self.write_bytes(d.bytes65_68)
        self.write_u8(d.inertia_present)
        self.write_u16(d.inertia_max_speed)
        self.write_f64(d.inertia_speed_correction_on_direction_change)
        self.write_u8(d.animation_type)
        self.write_bytes(d.bytes81_101)
    
    def _read_generic_movement_details(self) -> GenericMovementDetails:
        d = GenericMovementDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.bytes6_101 = self.read_bytes(96)
        return d
        
    def _write_generic_movement_details(self, d: GenericMovementDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_bytes(d.bytes6_101)

    def _read_shot_details(self) -> ShotDetails:
        d = ShotDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.sound_effect = self.read_u16()
        d.play_if_outside_screen = self.read_u8()
        d.animation = self.read_u16()
        d.bytes11_30 = self.read_bytes(20)
        d.number_of_shots_fired = self.read_u8()
        d.formation = self.read_u8()
        d.firing_parameter1 = self.read_u16()
        d.firing_parameter2 = self.read_u16()
        d.firing_parameter3 = self.read_u16()
        d.target = self.read_u8()
        d.direction = self.read_u8()
        d.set_angle_to_target = self.read_u8()
        d.firing_target = self.read_u8()
        d.angle_offset = self.read_u16()
        d.angle_offset_double = self.read_u16()
        d.angle_offset_reverse_rotation_if_facing_right = self.read_u8()
        d.angle_dispersion = self.read_u16()
        d.change_firing_position_according_to_angle = self.read_u8()
        d.number_of_doubles = self.read_u8()
        d.firing_position_offset_x = self.read_u16()
        d.firing_position_offset_x_double = self.read_u16()
        d.firing_position_offset_y = self.read_u16()
        d.firing_position_offset_y_double = self.read_u16()
        d.firing_position_offset_x_flip_if_facing_right = self.read_u8()
        d.firing_position_offset_y_flip_if_facing_right = self.read_u8()
        d.graphic = self.read_u16()
        d.z_coordinate = self.read_u8()
        d.transparency = self.read_u8()
        d.faction_same_as_user = self.read_u8()
        d.faction = self.read_u16()
        d.gigantic = self.read_u16()
        d.movement_type = self.read_u8()
        d.movement_type_parameter1 = self.read_u16()
        d.movement_type_parameter2 = self.read_u16()
        d.movement_type_parameter3 = self.read_u16()
        d.movement_target = self.read_u8()
        d.synchronize_with_auto_scroll = self.read_u8()
        d.speed = self.read_u16()
        d.speed_double = self.read_u16()
        d.acceleration_enabled = self.read_u8()
        d.acceleration = self.read_u16()
        d.acceleration_double = self.read_u16()
        d.flight_distance = self.read_u16()
        d.flight_distance_valid = self.read_u8()
        d.flight_distance_double = self.read_u16()
        d.flight_distance_does_not_disappear_at_end = self.read_u8()
        d.disappearance_time_valid = self.read_u8()
        d.disappearance_time = self.read_u16()
        d.disappearance_time_double = self.read_u16()
        d.penetrate_blocks = self.read_u8()
        d.penetrate_actors = self.read_u8()
        d.penetrate_block_actors = self.read_u8()
        d.disappear_on_hitting_shot = self.read_u8()
        d.value_for_disappearing_on_hitting_shot = self.read_u8()
        d.power = self.read_u32()
        d.bytes109_110 = self.read_bytes(2)
        d.impact = self.read_u8()
        d.effect = self.read_u16()
        d.acquired_item_palette_type = self.read_u8()
        d.acquired_item_palette_number = self.read_u16()
        d.bytes117_125 = self.read_bytes(9)
        d.attack = self.read_u8()
        d.attack_id = self.read_u8()
        d.bytes128_143 = self.read_bytes(16)
        return d
    
    def _write_shot_details(self, d: ShotDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_u16(d.sound_effect)
        self.write_u8(d.play_if_outside_screen)
        self.write_u16(d.animation)
        self.write_bytes(d.bytes11_30)
        self.write_u8(d.number_of_shots_fired)
        self.write_u8(d.formation)
        self.write_u16(d.firing_parameter1)
        self.write_u16(d.firing_parameter2)
        self.write_u16(d.firing_parameter3)
        self.write_u8(d.target)
        self.write_u8(d.direction)
        self.write_u8(d.set_angle_to_target)
        self.write_u8(d.firing_target)
        self.write_u16(d.angle_offset)
        self.write_u16(d.angle_offset_double)
        self.write_u8(d.angle_offset_reverse_rotation_if_facing_right)
        self.write_u16(d.angle_dispersion)
        self.write_u8(d.change_firing_position_according_to_angle)
        self.write_u8(d.number_of_doubles)
        self.write_u16(d.firing_position_offset_x)
        self.write_u16(d.firing_position_offset_x_double)
        self.write_u16(d.firing_position_offset_y)
        self.write_u16(d.firing_position_offset_y_double)
        self.write_u8(d.firing_position_offset_x_flip_if_facing_right)
        self.write_u8(d.firing_position_offset_y_flip_if_facing_right)
        self.write_u16(d.graphic)
        self.write_u8(d.z_coordinate)
        self.write_u8(d.transparency)
        self.write_u8(d.faction_same_as_user)
        self.write_u16(d.faction)
        self.write_u16(d.gigantic)
        self.write_u8(d.movement_type)
        self.write_u16(d.movement_type_parameter1)
        self.write_u16(d.movement_type_parameter2)
        self.write_u16(d.movement_type_parameter3)
        self.write_u8(d.movement_target)
        self.write_u8(d.synchronize_with_auto_scroll)
        self.write_u16(d.speed)
        self.write_u16(d.speed_double)
        self.write_u8(d.acceleration_enabled)
        self.write_u16(d.acceleration)
        self.write_u16(d.acceleration_double)
        self.write_u16(d.flight_distance)
        self.write_u8(d.flight_distance_valid)
        self.write_u16(d.flight_distance_double)
        self.write_u8(d.flight_distance_does_not_disappear_at_end)
        self.write_u8(d.disappearance_time_valid)
        self.write_u16(d.disappearance_time)
        self.write_u16(d.disappearance_time_double)
        self.write_u8(d.penetrate_blocks)
        self.write_u8(d.penetrate_actors)
        self.write_u8(d.penetrate_block_actors)
        self.write_u8(d.disappear_on_hitting_shot)
        self.write_u8(d.value_for_disappearing_on_hitting_shot)
        self.write_u32(d.power)
        self.write_bytes(d.bytes109_110)
        self.write_u8(d.impact)
        self.write_u16(d.effect)
        self.write_u8(d.acquired_item_palette_type)
        self.write_u16(d.acquired_item_palette_number)
        self.write_bytes(d.bytes117_125)
        self.write_u8(d.attack)
        self.write_u8(d.attack_id)
        self.write_bytes(d.bytes128_143)

    def _read_block_summon_details(self) -> SummonDetails:
        return self._read_summon_details()
    def _read_chara_summon_details(self) -> SummonDetails:
        return self._read_summon_details()
    
    def _read_item_summon_details(self) -> ItemSummonDetails:
        d = ItemSummonDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.sound_effect = self.read_u16()
        d.play_sound_effect_if_outside_screen = self.read_u8()
        d.animation = self.read_u8()
        d.bytes10_30 = self.read_bytes(21)
        d.count = self.read_u8()
        d.formation = self.read_u8()
        d.interval = self.read_u16()
        d.number_of_columns = self.read_u16()
        d.column_interval = self.read_u16()
        d.target = self.read_u8()
        d.direction = self.read_u8()
        d.byte41 = self.read_u8()
        d.target2 = self.read_u8()
        d.bytes43_51 = self.read_bytes(9)
        d.summon_position_offset_x = self.read_u32()
        d.summon_position_offset_y = self.read_u32()
        d.summon_position_offset_x_flip = self.read_u8()
        d.summon_position_offset_y_flip = self.read_u8()
        d.bytes62_66 = self.read_bytes(5)
        d.faction = self.read_u8()
        d.bytes68_88 = self.read_bytes(21)
        d.existence_time = self.read_u16()
        d.existence_time_present = self.read_u8()
        d.bytes92_119 = self.read_bytes(28)
        d.palette_type = self.read_u8()
        d.palette_data_number = self.read_u16()
        d.faction_specification_method = self.read_u8()
        d.set_acquired_score_to_0 = self.read_u8()
        d.direction_flip = self.read_u8()
        d.attack = self.read_u8()
        d.attack_flow = self.read_u8()
        d.bytes128_143 = self.read_bytes(16)
        return d

    def _read_summon_details(self) -> SummonDetails:
        d = SummonDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.sound_effect = self.read_u16()
        d.play_sound_effect_if_outside_screen = self.read_u8()
        d.animation = self.read_u8()
        d.bytes10_30 = self.read_bytes(21)
        d.count = self.read_u8()
        d.formation = self.read_u8()
        d.interval = self.read_u16()
        d.number_of_columns = self.read_u16()
        d.column_interval = self.read_u16()
        d.target = self.read_u8()
        d.direction = self.read_u8()
        d.byte41 = self.read_u8()
        d.target2 = self.read_u8()
        d.bytes43_51 = self.read_bytes(9)
        d.summon_position_offset_x = self.read_u32()
        d.summon_position_offset_y = self.read_u32()
        d.summon_position_offset_x_flip = self.read_u8()
        d.summon_position_offset_y_flip = self.read_u8()
        d.bytes62_66 = self.read_bytes(5)
        d.faction = self.read_u8()
        d.bytes68_88 = self.read_bytes(21)
        d.existence_time = self.read_u16()
        d.existence_time_present = self.read_u8()
        d.bytes92_119 = self.read_bytes(28)
        d.palette_type = self.read_u8()
        d.palette_data_number = self.read_u16()
        d.faction_specification_method = self.read_u8()
        d.set_acquired_score_to_0 = self.read_u8()
        d.direction_flip = self.read_u8()
        d.attack = self.read_u8()
        d.attack_flow = self.read_u8()
        d.bytes128_143 = self.read_bytes(16)
        d.return_value_to_flow_variable = self.read_u8()
        d.bytes145_147 = self.read_bytes(3)
        return d
    
    def _write_item_summon_details(self, d: ItemSummonDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_u16(d.sound_effect)
        self.write_u8(d.play_sound_effect_if_outside_screen)
        self.write_u8(d.animation)
        self.write_bytes(d.bytes10_30)
        self.write_u8(d.count)
        self.write_u8(d.formation)
        self.write_u16(d.interval)
        self.write_u16(d.number_of_columns)
        self.write_u16(d.column_interval)
        self.write_u8(d.target)
        self.write_u8(d.direction)
        self.write_u8(d.byte41)
        self.write_u8(d.target2)
        self.write_bytes(d.bytes43_51)
        self.write_u32(d.summon_position_offset_x)
        self.write_u32(d.summon_position_offset_y)
        self.write_u8(d.summon_position_offset_x_flip)
        self.write_u8(d.summon_position_offset_y_flip)
        self.write_bytes(d.bytes62_66)
        self.write_u8(d.faction)
        self.write_bytes(d.bytes68_88)
        self.write_u16(d.existence_time)
        self.write_u8(d.existence_time_present)
        self.write_bytes(d.bytes92_119)
        self.write_u8(d.palette_type)
        self.write_u16(d.palette_data_number)
        self.write_u8(d.faction_specification_method)
        self.write_u8(d.set_acquired_score_to_0)
        self.write_u8(d.direction_flip)
        self.write_u8(d.attack)
        self.write_u8(d.attack_flow)
        self.write_bytes(d.bytes128_143)

    def _write_summon_details(self, d: SummonDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_u16(d.sound_effect)
        self.write_u8(d.play_sound_effect_if_outside_screen)
        self.write_u8(d.animation)
        self.write_bytes(d.bytes10_30)
        self.write_u8(d.count)
        self.write_u8(d.formation)
        self.write_u16(d.interval)
        self.write_u16(d.number_of_columns)
        self.write_u16(d.column_interval)
        self.write_u8(d.target)
        self.write_u8(d.direction)
        self.write_u8(d.byte41)
        self.write_u8(d.target2)
        self.write_bytes(d.bytes43_51)
        self.write_u32(d.summon_position_offset_x)
        self.write_u32(d.summon_position_offset_y)
        self.write_u8(d.summon_position_offset_x_flip)
        self.write_u8(d.summon_position_offset_y_flip)
        self.write_bytes(d.bytes62_66)
        self.write_u8(d.faction)
        self.write_bytes(d.bytes68_88)
        self.write_u16(d.existence_time)
        self.write_u8(d.existence_time_present)
        self.write_bytes(d.bytes92_119)
        self.write_u8(d.palette_type)
        self.write_u16(d.palette_data_number)
        self.write_u8(d.faction_specification_method)
        self.write_u8(d.set_acquired_score_to_0)
        self.write_u8(d.direction_flip)
        self.write_u8(d.attack)
        self.write_u8(d.attack_flow)
        self.write_bytes(d.bytes128_143)
        self.write_u8(d.return_value_to_flow_variable)
        self.write_bytes(d.bytes145_147)

    def _read_sword_details(self) -> SwordDetails:
        d = SwordDetails()
        d.execution_time = self.read_u32()
        d.parallel_execution = self.read_u8()
        d.sound_effect = self.read_u16()
        d.play_if_outside_screen = self.read_u8()
        d.animation = self.read_u16()
        d.bytes11_63 = self.read_bytes(53)
        d.z_coordinate = self.read_u8()
        d.transparency = self.read_u8()
        d.faction_same_as_user = self.read_u8()
        d.faction = self.read_u16()
        d.gigantic = self.read_u16()
        d.sword_type = self.read_u32()
        d.bytes75_104 = self.read_bytes(30)
        d.power = self.read_u32()
        d.bytes109_110 = self.read_bytes(2)
        d.impact = self.read_u8()
        d.effect = self.read_u16()
        d.acquired_item_palette_type = self.read_u8()
        d.acquired_item_palette_number = self.read_u16()
        d.bytes117_125 = self.read_bytes(9)
        d.attack = self.read_u8()
        d.attack_id = self.read_u8()
        d.bytes128_143 = self.read_bytes(16)
        return d
    
    def _write_sword_details(self, d: SwordDetails):
        self.write_u32(d.execution_time)
        self.write_u8(d.parallel_execution)
        self.write_u16(d.sound_effect)
        self.write_u8(d.play_if_outside_screen)
        self.write_u16(d.animation)
        self.write_bytes(d.bytes11_63)
        self.write_u8(d.z_coordinate)
        self.write_u8(d.transparency)
        self.write_u8(d.faction_same_as_user)
        self.write_u16(d.faction)
        self.write_u16(d.gigantic)
        self.write_u32(d.sword_type)
        self.write_bytes(d.bytes75_104)
        self.write_u32(d.power)
        self.write_bytes(d.bytes109_110)
        self.write_u8(d.impact)
        self.write_u16(d.effect)
        self.write_u8(d.acquired_item_palette_type)
        self.write_u16(d.acquired_item_palette_number)
        self.write_bytes(d.bytes117_125)
        self.write_u8(d.attack)
        self.write_u8(d.attack_id)
        self.write_bytes(d.bytes128_143)

    def _read_code_execution_details(self) -> CodeExecutionDetails:
        d = CodeExecutionDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.bytes6_14 = self.read_bytes(9)
        d.code = self.read_std_string()
        d.bytes19_38 = self.read_bytes(20)
        return d

    def _write_code_execution_details(self, d: CodeExecutionDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_bytes(d.bytes6_14)
        self.write_std_string(d.code)
        self.write_bytes(d.bytes19_38)

    def _read_warp_details(self) -> WarpDetails:
        d = WarpDetails()
        d.bytes1_26 = self.read_bytes(26)
        d.setting_type = self.read_u8()
        d.direction = self.read_u8()
        d.bytes29_33 = self.read_bytes(5)
        d.target_x_present = self.read_u8()
        d.target_y_present = self.read_u8()
        d.target_x_bl = self.read_u16()
        d.target_y_bl = self.read_u16()
        d.target_x_dot = self.read_u16()
        d.target_y_dot = self.read_u16()
        d.target_type = self.read_u8()
        d.target_unit = self.read_u8()
        d.gigantic_character_coordinate_position = self.read_u8()
        d.bytes47_49 = self.read_bytes(3)
        d.target_x_flip_if_facing_right = self.read_u8()
        d.target_y_flip_if_facing_right = self.read_u8()
        d.bytes52_59 = self.read_bytes(8)
        d.distance = self.read_u16()
        d.distance_double = self.read_u16()
        d.bytes64_101 = self.read_bytes(38)
        d.assign_return_value_to_flow = self.read_u32()
        return d

    def _write_warp_details(self, d: WarpDetails):
        self.write_bytes(d.bytes1_26)
        self.write_u8(d.setting_type)
        self.write_u8(d.direction)
        self.write_bytes(d.bytes29_33)
        self.write_u8(d.target_x_present)
        self.write_u8(d.target_y_present)
        self.write_u16(d.target_x_bl)
        self.write_u16(d.target_y_bl)
        self.write_u16(d.target_x_dot)
        self.write_u16(d.target_y_dot)
        self.write_u8(d.target_type)
        self.write_u8(d.target_unit)
        self.write_u8(d.gigantic_character_coordinate_position)
        self.write_bytes(d.bytes47_49)
        self.write_u8(d.target_x_flip_if_facing_right)
        self.write_u8(d.target_y_flip_if_facing_right)
        self.write_bytes(d.bytes52_59)
        self.write_u16(d.distance)
        self.write_u16(d.distance_double)
        self.write_bytes(d.bytes64_101)
        self.write_u32(d.assign_return_value_to_flow)

    def _read_status_operation_details(self) -> StatusOperationDetails:
        d = StatusOperationDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.operation_target_type = self.read_u8()
        d.bytes40_43 = self.read_bytes(4)
        d.operation_target_variable_type = self.read_u8()
        d.bytes45_46 = self.read_bytes(2)
        d.operation_target_variable_number = self.read_u16()
        d.bytes49_52 = self.read_bytes(4)
        d.operation_target_target = self.read_u8()
        d.bytes54_56 = self.read_bytes(3)
        d.operation_target_status = self.read_u8()
        d.byte58 = self.read_bytes(1)
        d.operation_target_flow_variable_number = self.read_u8()
        d.bytes60_62 = self.read_bytes(3)
        d.operator_type = self.read_u8()
        d.bytes64_66 = self.read_bytes(3)
        d.calculation_content_type = self.read_u32()
        d.calculation_content_constant = self.read_u32()
        d.calculation_content_random_lower_limit = self.read_u32()
        d.calculation_content_random_upper_limit = self.read_u32()
        d.calculation_content_variable_type = self.read_u32()
        d.calculation_content_variable_number = self.read_u32()
        d.calculation_content_target = self.read_u32()
        d.calculation_content_status = self.read_u32()
        d.calculation_content_flow_variable_number = self.read_u32()
        d.bytes103_138 = self.read_bytes(36)
        return d

    def _write_status_operation_details(self, d: StatusOperationDetails):
        self.write_bytes(d.bytes1_38)
        self.write_u8(d.operation_target_type)
        self.write_bytes(d.bytes40_43)
        self.write_u8(d.operation_target_variable_type)
        self.write_bytes(d.bytes45_46)
        self.write_u16(d.operation_target_variable_number)
        self.write_bytes(d.bytes49_52)
        self.write_u8(d.operation_target_target)
        self.write_bytes(d.bytes54_56)
        self.write_u8(d.operation_target_status)
        self.write_bytes(d.byte58)
        self.write_u8(d.operation_target_flow_variable_number)
        self.write_bytes(d.bytes60_62)
        self.write_u8(d.operator_type)
        self.write_bytes(d.bytes64_66)
        self.write_u32(d.calculation_content_type)
        self.write_u32(d.calculation_content_constant)
        self.write_u32(d.calculation_content_random_lower_limit)
        self.write_u32(d.calculation_content_random_upper_limit)
        self.write_u32(d.calculation_content_variable_type)
        self.write_u32(d.calculation_content_variable_number)
        self.write_u32(d.calculation_content_target)
        self.write_u32(d.calculation_content_status)
        self.write_u32(d.calculation_content_flow_variable_number)
        self.write_bytes(d.bytes103_138)

    def _read_status_operation2_details(self) -> StatusOperation2Details:
        d = StatusOperation2Details()
        d.bytes1_38 = self.read_bytes(38)
        d.target = self.read_u32()
        d.status = self.read_u32()
        d.on = self.read_u32()
        d.bytes51_62 = self.read_bytes(12)
        return d

    def _write_status_operation2_details(self, d: StatusOperation2Details):
        self.write_bytes(d.bytes1_38)
        self.write_u32(d.target)
        self.write_u32(d.status)
        self.write_u32(d.on)
        self.write_bytes(d.bytes51_62)

    def _read_disappearance_details(self) -> DisappearanceDetails:
        d = DisappearanceDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.target = self.read_u32()
        d.faction = self.read_u32()
        d.range = self.read_u32()
        d.assign_return_value_to_flow_variable = self.read_u32()
        return d

    def _write_disappearance_details(self, d: DisappearanceDetails):
        self.write_bytes(d.bytes1_38)
        self.write_u32(d.target)
        self.write_u32(d.faction)
        self.write_u32(d.range)
        self.write_u32(d.assign_return_value_to_flow_variable)

    def _read_item_acquisition_details(self) -> ItemAcquisitionDetails:
        d = ItemAcquisitionDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.palette_type = self.read_u32()
        d.palette_data_number = self.read_u32()
        return d

    def _write_item_acquisition_details(self, d: ItemAcquisitionDetails):
        self.write_bytes(d.bytes1_38)
        self.write_u32(d.palette_type)
        self.write_u32(d.palette_data_number)

    def _read_graphic_change_details(self) -> GraphicChangeDetails:
        d = GraphicChangeDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.image_type = self.read_u32()
        d.image_number = self.read_u32()
        d.offset = self.read_u32()
        return d

    def _write_graphic_change_details(self, d: GraphicChangeDetails):
        self.write_bytes(d.bytes1_38)
        self.write_u32(d.image_type)
        self.write_u32(d.image_number)
        self.write_u32(d.offset)

    def _read_basic_animation_set_change_details(self) -> BasicAnimationSetChangeDetails:
        d = BasicAnimationSetChangeDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.animation_set = self.read_u32()
        return d

    def _write_basic_animation_set_change_details(self, d: BasicAnimationSetChangeDetails):
        self.write_bytes(d.bytes1_38)
        self.write_u32(d.animation_set)

    def _read_animation_execution_details(self) -> AnimationExecutionDetails:
        d = AnimationExecutionDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.bytes = self.read_bytes(41)
        return d

    def _write_animation_execution_details(self, d: AnimationExecutionDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_bytes(d.bytes)

    def _read_effect_execution_details(self) -> EffectExecutionDetails:
        d = EffectExecutionDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.bytes = self.read_bytes(40)
        return d

    def _write_effect_execution_details(self, d: EffectExecutionDetails):
        self.write_bytes(d.bytes1_38)
        self.write_bytes(d.bytes)

    def _read_character_effect_execution_details(self) -> CharacterEffectExecutionDetails:
        d = CharacterEffectExecutionDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.effect = self.read_u32()
        d.execution_type = self.read_u32()
        d.loop_execution = self.read_u32()
        return d

    def _write_character_effect_execution_details(self, d: CharacterEffectExecutionDetails):
        self.write_bytes(d.bytes1_38)
        self.write_u32(d.effect)
        self.write_u32(d.execution_type)
        self.write_u32(d.loop_execution)

    def _read_screen_effect_execution_details(self) -> ScreenEffectExecutionDetails:
        d = ScreenEffectExecutionDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.effect = self.read_u32()
        d.execution_type = self.read_u32()
        d.loop_execution = self.read_u32()
        return d

    def _write_screen_effect_execution_details(self, d: ScreenEffectExecutionDetails):
        self.write_bytes(d.bytes1_38)
        self.write_u32(d.effect)
        self.write_u32(d.execution_type)
        self.write_u32(d.loop_execution)

    def _read_picture_display_details(self) -> PictureDisplayDetails:
        d = PictureDisplayDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.bytes = self.read_bytes(113)
        return d

    def _write_picture_display_details(self, d: PictureDisplayDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_bytes(d.bytes)

    def _read_screen_color_change_details(self) -> ScreenColorChangeDetails:
        d = ScreenColorChangeDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.r = self.read_u32()
        d.g = self.read_u32()
        d.b = self.read_u32()
        d.percent = self.read_u32()
        d.restore_to_original_color = self.read_u32()
        d.time_required_for_change = self.read_u32()
        d.instant_display = self.read_u32()
        d.instant_display_count = self.read_u32()
        return d

    def _write_screen_color_change_details(self, d: ScreenColorChangeDetails):
        self.write_bytes(d.bytes1_38)
        self.write_u32(d.r)
        self.write_u32(d.g)
        self.write_u32(d.b)
        self.write_u32(d.percent)
        self.write_u32(d.restore_to_original_color)
        self.write_u32(d.time_required_for_change)
        self.write_u32(d.instant_display)
        self.write_u32(d.instant_display_count)

    def _read_background_change_details(self) -> BackgroundChangeDetails:
        d = BackgroundChangeDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.bytes = self.read_bytes(41)
        return d

    def _write_background_change_details(self, d: BackgroundChangeDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_bytes(d.bytes)

    def _read_sound_effect_playback_details(self) -> SoundEffectPlaybackDetails:
        d = SoundEffectPlaybackDetails()
        d.bytes1_7 = self.read_bytes(7)
        d.play_if_outside_screen = self.read_u8()
        d.bytes9_38 = self.read_bytes(30)
        d.sound_effect = self.read_u32()
        return d

    def _write_sound_effect_playback_details(self, d: SoundEffectPlaybackDetails):
        self.write_bytes(d.bytes1_7)
        self.write_u8(d.play_if_outside_screen)
        self.write_bytes(d.bytes9_38)
        self.write_u32(d.sound_effect)

    def _read_bgm_playback_details(self) -> BGMPlaybackDetails:
        d = BGMPlaybackDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.bytes = self.read_bytes(41)
        return d

    def _write_bgm_playback_details(self, d: BGMPlaybackDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_bytes(d.bytes)

    def _read_arrangement_details(self) -> ArrangementDetails:
        d = ArrangementDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.command = self.read_u32()
        d.parameter = self.read_u32()
        d.operator_type = self.read_u32()
        d.variable_type = self.read_u32()
        d.variable_number = self.read_u32()
        return d

    def _write_arrangement_details(self, d: ArrangementDetails):
        self.write_bytes(d.bytes1_38)
        self.write_u32(d.command)
        self.write_u32(d.parameter)
        self.write_u32(d.operator_type)
        self.write_u32(d.variable_type)
        self.write_u32(d.variable_number)

    def _read_loop_details(self) -> LoopDetails:
        d = LoopDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.repeat_count = self.read_u32()
        d.command_count = self.read_u32()
        return d

    def _write_loop_details(self, d: LoopDetails):
        self.write_bytes(d.bytes1_38)
        self.write_u32(d.repeat_count)
        self.write_u32(d.command_count)

    def _read_direction_change_details(self) -> DirectionChangeDetails:
        d = DirectionChangeDetails()
        d.execution_time = self.read_u16()
        d.execution_time_double = self.read_u16()
        d.parallel_execution = self.read_u8()
        d.bytes6_42 = self.read_bytes(37)
        return d

    def _write_direction_change_details(self, d: DirectionChangeDetails):
        self.write_u16(d.execution_time)
        self.write_u16(d.execution_time_double)
        self.write_u8(d.parallel_execution)
        self.write_bytes(d.bytes6_42)

    def _read_jump_details(self) -> JumpDetails:
        d = JumpDetails()
        d.bytes1_5 = self.read_bytes(5)
        d.sound_effect = self.read_u16()
        d.play_if_outside_screen = self.read_u8()
        d.animation = self.read_u16()
        d.bytes11_38 = self.read_bytes(28)
        d.jump_type = self.read_u32()
        d.max_jump_inertial_movement_speed = self.read_u32()
        d.max_jump_height = self.read_u32()
        d.min_jump_inertial_movement_speed = self.read_u32()
        d.min_jump_height = self.read_u32()
        return d

    def _write_jump_details(self, d: JumpDetails):
        self.write_bytes(d.bytes1_5)
        self.write_u16(d.sound_effect)
        self.write_u8(d.play_if_outside_screen)
        self.write_u16(d.animation)
        self.write_bytes(d.bytes11_38)
        self.write_u32(d.jump_type)
        self.write_u32(d.max_jump_inertial_movement_speed)
        self.write_u32(d.max_jump_height)
        self.write_u32(d.min_jump_inertial_movement_speed)
        self.write_u32(d.min_jump_height)

    def _read_flow_operation_details(self) -> FlowOperationDetails:
        d = FlowOperationDetails()
        d.bytes1_34 = self.read_bytes(34)
        d.condition_present = self.read_u8()
        d.judgment_type = self.read_u8()
        d.bytes37_40 = self.read_bytes(4)
        d.conditions = self._read_array(self._read_basic_condition)
        d.bytes45_52 = self.read_bytes(8)
        d.operation = self.read_u32()
        d.target_flow = self.read_u32()
        d.id = self.read_u32()
        d.target_character = self.read_u32()
        d.assign_return_value_to_flow_variable = self.read_u32()
        return d

    def _write_flow_operation_details(self, d: FlowOperationDetails):
        self.write_bytes(d.bytes1_34)
        self.write_u8(d.condition_present)
        self.write_u8(d.judgment_type)
        self.write_bytes(d.bytes37_40)
        self._write_array([BasicCondition(**i) for i in d.conditions], self._write_basic_condition)
        self.write_bytes(d.bytes45_52)
        self.write_u32(d.operation)
        self.write_u32(d.target_flow)
        self.write_u32(d.id)
        self.write_u32(d.target_character)
        self.write_u32(d.assign_return_value_to_flow_variable)

    def _read_target_setting_details(self) -> TargetSettingDetails:
        d = TargetSettingDetails()
        d.bytes1_38 = self.read_bytes(38)
        d.bytes39_106 = self.read_bytes(68)
        return d

    def _write_target_setting_details(self, d: TargetSettingDetails):
        self.write_bytes(d.bytes1_38)
        self.write_bytes(d.bytes39_106)
    # endregion


# --- JSON Conversion Logic (Unchanged from original) ---

class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            d = asdict(o)
            d['__dataclass__'] = o.__class__.__name__
            return d
        if isinstance(o, bytes):
            return list(o)
        return super().default(o)

def dataclass_json_hook(dct):
    if '__dataclass__' in dct:
        cls_name = dct.pop('__dataclass__')
        cls = globals().get(cls_name)
        if cls and is_dataclass(cls):
            try:
                return cls(**dct)
            except TypeError as e:
                print(f"ERROR: Could not create dataclass '{cls_name}'. Mismatched arguments? Details: {e}")
                dct['__dataclass__'] = cls_name
                return dct
        else:
            dct['__dataclass__'] = cls_name
            return dct
    return dct

# --- Main Application Logic (Adapted for CPLT4) ---

def export_to_json(in_files: List[Path]):
    """
    Parses one or more .cplt4 files and exports them to JSON.
    """
    for in_file in in_files:
        print(f"--> Exporting '{in_file}'...")
        if not in_file.exists():
            print(f"    ERROR: Input file not found.")
            continue

        cplt = Cplt4(in_file)
        if cplt.parse():
            out_file = in_file.with_suffix(in_file.suffix + '.json')
            try:
                with open(out_file, 'w', encoding='utf-8') as f:
                    json.dump(cplt.data, f, cls=DataclassJSONEncoder, indent=2, ensure_ascii=False)
                print(f"    SUCCESS: Exported to '{out_file}'")
            except Exception as e:
                print(f"    ERROR: Could not write JSON file: {e}")
        else:
            print(f"    ERROR: Failed to parse '{in_file}'.")

def import_from_json(in_file: Path, out_file: Path):
    """
    Imports a JSON file and creates a new .cplt4 file.
    """
    print(f"--> Importing '{in_file}'...")
    if not in_file.exists():
        print(f"    ERROR: Input JSON file not found.")
        return

    try:
        with open(in_file, 'r', encoding='utf-8') as f:
            reconstructed_data = json.load(f, object_hook=dataclass_json_hook)

        if not isinstance(reconstructed_data, Cplt4Data):
            print("    ERROR: JSON file does not represent valid Cplt4Data.")
            return

        new_cplt = Cplt4(out_file)
        new_cplt.data = reconstructed_data
        
        if new_cplt.save():
            print(f"    SUCCESS: Imported to '{out_file}'")
        else:
            print(f"    ERROR: Failed to save new palette file.")

    except json.JSONDecodeError as e:
        print(f"    ERROR: Invalid JSON format in '{in_file}': {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"    ERROR: An unexpected error occurred during import: {e}")

def main():
    parser = argparse.ArgumentParser(description="Tool to export/import CPLT4 palette files to/from JSON.")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Export command
    export_parser = subparsers.add_parser('export', help="Export one or more .cplt4 files to JSON.")
    export_parser.add_argument('in_files', nargs='+', type=Path, help="Path to input .cplt4 file(s).")
    
    # Import command
    import_parser = subparsers.add_parser('import', help="Import a JSON file to a new .cplt4 file.")
    import_parser.add_argument('in_file', type=Path, help="Path to the input JSON file.")
    import_parser.add_argument('-o', '--output', type=Path, help="Path for the output .cplt4 file (optional).")

    args = parser.parse_args()

    if args.command == 'export':
        export_to_json(args.in_files)
    elif args.command == 'import':
        out_file = args.output
        if not out_file:
            # Auto-generate output filename if not provided
            in_stem = args.in_file.stem.replace('.cplt4', '')
            out_file = args.in_file.with_name(f"{in_stem}_NEW.cplt4")
        
        import_from_json(args.in_file, out_file)


if __name__ == "__main__":
    main()