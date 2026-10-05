#include "boot.hpp"
#include <initializer_list>

namespace {
char trace[3072];
u32 length;
u64 recorded;
bool fsReady;
bool recording;
unsigned writes;
Result lastWrite;
constexpr unsigned MaxWrites = 40;
constexpr const char *Path = "/3ds/UniversalGameGuide/logs/boot-stage.txt";

void append(const char *s) {
    for (unsigned n = 0; s && *s && n < 160 && length + 1 < sizeof(trace); ++n)
        trace[length++] = *s++;
    trace[length] = 0;
}
void hex(u64 value, unsigned digits) {
    static const char table[] = "0123456789ABCDEF";
    for (unsigned i = digits; i && length + 1 < sizeof(trace); --i)
        trace[length++] = table[(value >> ((i - 1) * 4)) & 15];
    trace[length] = 0;
}
void flush() {
    if (!fsReady || writes >= MaxWrites)
        return;
    ++writes;
    Handle file = 0;
    lastWrite =
        FSUSER_OpenFileDirectly(&file, ARCHIVE_SDMC, fsMakePath(PATH_EMPTY, ""),
                                fsMakePath(PATH_ASCII, Path), FS_OPEN_WRITE | FS_OPEN_CREATE, 0);
    if (R_SUCCEEDED(lastWrite)) {
        lastWrite = FSFILE_SetSize(file, length);
        if (R_SUCCEEDED(lastWrite)) {
            u32 count = 0;
            lastWrite = FSFILE_Write(file, &count, 0, trace, length, FS_WRITE_FLUSH);
            if (R_SUCCEEDED(lastWrite) && count != length)
                lastWrite = -1;
        }
        const Result closed = FSFILE_Close(file);
        if (R_SUCCEEDED(lastWrite))
            lastWrite = closed;
    }
    // A failed SD stops diagnostic writes. It must not stop the game.
    if (R_FAILED(lastWrite))
        fsReady = false;
}
} // namespace

extern "C" const char *UGGBootVariant() {
#ifdef UGG_MINIMAL_BOOT
    return "minimal-boot";
#elif defined(UGG_MINIMAL)
    return "minimal";
#else
    return "full";
#endif
}
extern "C" Result UGGBootLastWrite() { return lastWrite; }
extern "C" void UGGBootStage(unsigned stage, const char *label) {
    if (!stage || stage >= 64 || (recorded & (1ULL << stage)))
        return;
    if (!recording) {
        // Only the experimental hardware-test builds enable this marker file.
        recording = true;
        append("UGG 0.2.2-alpha / ");
        append(UGGBootVariant());
        append(" / PRIVATE=false / MemorySize=5MiB\nNEEDS HARDWARE RETEST\n");
    }
    recorded |= 1ULL << stage;
    append("STAGE 0x");
    hex(stage, 2);
    append(" ");
    append(label);
    append("\n");
    flush();
}
extern "C" void UGGBootResult(const char *label, Result result) {
    if (!recording)
        return;
    append(label);
    append(" result=0x");
    hex(static_cast<u32>(result), 8);
    append("\n");
    flush();
}
extern "C" void UGGBootTitle(u64 title) {
    append("title-id=");
    hex(title, 16);
    append("\n");
    flush();
}
extern "C" void UGGBootHeap(int bytes) {
    append("newlib-free-bytes-hex=");
    hex(static_cast<u32>(bytes), 8);
    append("\n");
    flush();
}
extern "C" void UGGBootValue(const char *label, u64 value) {
    if (!recording)
        return;
    append(label);
    append("=0x");
    hex(value, 16);
    append("\n");
    flush();
}
extern "C" void UGGBootFsReady(Result result) {
    UGGBootResult("fsInit", result);
    if (R_FAILED(result)) {
        lastWrite = result;
        return;
    }
    FS_Archive archive;
    lastWrite = FSUSER_OpenArchive(&archive, ARCHIVE_SDMC, fsMakePath(PATH_EMPTY, ""));
    if (R_FAILED(lastWrite))
        return;
    // Existing directories are permitted; all writes stay inside the project.
    for (const char *dir : {"/3ds", "/3ds/UniversalGameGuide", "/3ds/UniversalGameGuide/logs"})
        FSUSER_CreateDirectory(archive, fsMakePath(PATH_ASCII, dir), 0);
    FSUSER_CloseArchive(archive);
    fsReady = true;
    UGGBootStage(6, "SD marker available; earlier stages were buffered in RAM");
}
