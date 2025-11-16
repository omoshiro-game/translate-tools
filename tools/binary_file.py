from dataclasses import dataclass
from pathlib import Path
from typing import Union
import struct

class ActedBinaryFile:
    VERSIONS = [
        0xB6, # v248b
        0x03C6, # ??
        0x03FC # v1020
    ]

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
        """Reset the buffer and position, entering append mode"""
        self._data = bytearray()
        self._position = 0
        self._append_mode = True

    def finish_writing(self):
        """Finish writing mode"""
        self._append_mode = False

    def _ensure_space(self, size: int):
        """Ensure there's enough space in the buffer for writing"""
        if self._append_mode or self._position + size > len(self._data):
            # If in append mode or not enough space, extend the buffer
            needed = self._position + size - len(self._data)
            if needed > 0:
                self._data.extend(bytearray(needed))

    def read_u8(self) -> int:
        value = self._data[self._position]
        self._position += 1
        return value
        
    def read_u16(self) -> int:
        value = struct.unpack_from("<H", self._data, self._position)[0]
        self._position += 2
        return value
        
    def read_u32(self) -> int:
        value = struct.unpack_from("<I", self._data, self._position)[0]
        self._position += 4
        return value
    
    def read_f64(self) -> float:
        value = struct.unpack_from("<d", self._data, self._position)[0]
        self._position += 8
        return value
        
    def read_s32(self) -> int:
        value = struct.unpack_from("<i", self._data, self._position)[0]
        self._position += 4
        return value
        
    def read_str(self, length: int) -> str:
        data = self._data[self._position:self._position + length]
        self._position += length
        return data.decode('shift-jis', errors='ignore').rstrip('\x00')
        
    def write_u8(self, value: int):
        self._ensure_space(1)
        self._data[self._position] = value
        self._position += 1
        
    def write_u16(self, value: int):
        self._ensure_space(2)
        struct.pack_into("<H", self._data, self._position, value)
        self._position += 2
        
    def write_u32(self, value: int):
        self._ensure_space(4)
        struct.pack_into("<I", self._data, self._position, value)
        self._position += 4
        
    def write_s32(self, value: int):
        self._ensure_space(4)
        struct.pack_into("<i", self._data, self._position, value)
        self._position += 4

    def write_f64(self, value: float):
        self._ensure_space(8)
        struct.pack_into("<d", self._data, self._position, float(value))
        self._position += 8
        
    def write_str(self, value: str, length: int):
        self._ensure_space(length)
        encoded = value.encode('shift-jis')[:length]
        encoded = encoded.ljust(length, b'\x00')
        self._data[self._position:self._position + length] = encoded
        self._position += length

    def read_std_string(self) -> str:
        length = self.read_u32()
        if length <= 1:
            return ""
        if length > 1:
            return self.read_str(length)
        return ""
    
    def write_std_string(self, value: str) -> None:
        encoded = value.encode("shift-jis", errors="ignore")
        length = len(encoded)
        self._ensure_space(4 + length)
        self.write_u32(length + 1) # Off-by one ? 
        if length > 0:
            self.write_str(value, length)
            
            # null-terminator
            self.write_u8(0)