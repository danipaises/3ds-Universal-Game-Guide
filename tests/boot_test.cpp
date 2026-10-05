#include "boot.hpp"
#include <cassert>
#include <iostream>
#include <string>
namespace {
unsigned writes, opens;
bool failWrite;
std::string last;
u64 declaredSize;
} // namespace
Result FSUSER_OpenArchive(FS_Archive *a, int kind, FS_Path) {
    assert(kind == ARCHIVE_SDMC);
    *a = 1;
    return 0;
}
Result FSUSER_CreateDirectory(FS_Archive, FS_Path path, u32) {
    const std::string p(static_cast<const char *>(path.data));
    assert(p == "/3ds" || p == "/3ds/UniversalGameGuide" || p == "/3ds/UniversalGameGuide/logs");
    return 0;
}
Result FSUSER_CloseArchive(FS_Archive) { return 0; }
Result FSUSER_OpenFileDirectly(Handle *f, int kind, FS_Path, FS_Path path, u32 mode, u32) {
    assert(kind == ARCHIVE_SDMC && mode == (FS_OPEN_WRITE | FS_OPEN_CREATE));
    assert(std::string(static_cast<const char *>(path.data)) ==
           "/3ds/UniversalGameGuide/logs/boot-stage.txt");
    ++opens;
    *f = 1;
    return 0;
}
Result FSFILE_SetSize(Handle, u64 size) {
    assert(size <= 3072);
    declaredSize = size;
    return 0;
}
Result FSFILE_Write(Handle, u32 *count, u64 offset, const void *data, u32 size, u32 flags) {
    ++writes;
    assert(offset == 0 && flags == FS_WRITE_FLUSH && size == declaredSize);
    if (failWrite)
        return -7;
    last.assign(static_cast<const char *>(data), size);
    *count = size;
    return 0;
}
Result FSFILE_Close(Handle) { return 0; }
int main(int argc, char **argv) {
    assert(argc == 2);
    const std::string scenario(argv[1]);
    UGGBootStage(1, "entry");
    UGGBootStage(2, "before heap");
    assert(opens == 0 && writes == 0);
    failWrite = scenario == "io-fail";
    UGGBootFsReady(scenario == "fs-fail" ? -1 : 0);
    for (unsigned i = 1; i < 64; ++i) {
        UGGBootStage(i, "checkpoint");
        UGGBootStage(i, "duplicate");
    }
    UGGBootStage(64, "invalid");
    for (unsigned i = 0; i < 10000; ++i)
        UGGBootResult("sample", 0);
    assert(opens <= 40 && writes <= 40 && last.size() <= 3072);
    if (scenario == "normal") {
        assert(writes == 40 && last.find("entry") != std::string::npos);
        assert(last.find("duplicate") == std::string::npos);
        assert(std::string(UGGBootVariant()) == "full");
    } else if (scenario == "fs-fail") {
        assert(opens == 0);
        assert(UGGBootLastWrite() == -1);
    } else if (scenario == "io-fail") {
        assert(writes == 1 && UGGBootLastWrite() == -7);
    } else
        return 2;
    std::cout << "Boot trace: " << scenario << " passed; writes=" << writes << '\n';
}
