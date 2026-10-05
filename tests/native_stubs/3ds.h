#pragma once
#include <cstdint>
using u32 = uint32_t;
using u64 = uint64_t;
using Result = int32_t;
using Handle = u32;
using FS_Archive = u64;
struct FS_Path {
    const void *data;
};
constexpr int PATH_EMPTY = 0, PATH_ASCII = 1, ARCHIVE_SDMC = 9;
constexpr u32 FS_OPEN_WRITE = 2, FS_OPEN_CREATE = 4, FS_WRITE_FLUSH = 1;
inline bool R_SUCCEEDED(Result result) { return result >= 0; }
inline bool R_FAILED(Result result) { return result < 0; }
inline FS_Path fsMakePath(int, const void *data) { return {data}; }
Result FSUSER_OpenFileDirectly(Handle *, int, FS_Path, FS_Path, u32, u32);
Result FSUSER_OpenArchive(FS_Archive *, int, FS_Path);
Result FSUSER_CreateDirectory(FS_Archive, FS_Path, u32);
Result FSUSER_CloseArchive(FS_Archive);
Result FSFILE_SetSize(Handle, u64);
Result FSFILE_Write(Handle, u32 *, u64, const void *, u32, u32);
Result FSFILE_Close(Handle);
