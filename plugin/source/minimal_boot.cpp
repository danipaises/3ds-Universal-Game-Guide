// Heap/constructors probe: the pinned CTRPF CRT and allocator, no CTRPF UI.
// Loader events follow the pinned plgldr.c/pluginInit.cpp contract.
#include "boot.hpp"
#include "CTRPluginFramework/System/FwkSettings.hpp"
#include "csvc.h"
#include "plgldr.h"
#include "ctrulibExtension.h"

// Header data only. Pulling FwkSettings.o would also pull Preferences/UI globals.
// This definition matches the pinned SDK; the allocator itself is unchanged.
namespace CTRPluginFramework {
PluginHeader *FwkSettings::Header = reinterpret_cast<PluginHeader *>(0x07000000);
}

// No game hooks or extra callback threads exist in this probe. SDK syscalls
// may use this fallback only for the one initialized probe thread.
extern "C" ThreadVars *__ctrpf_getThreadVars(ThreadVars *mainThreadVars) {
    return mainThreadVars;
}

extern "C" {
void initLib(void);
Result __sync_init(void);
void __system_initSyscalls(void);
s32 PLGLDR__FetchEvent(void);
void PLGLDR__Reply(s32 event);
extern u32 __ctru_heap;
extern u32 __ctru_heap_size;
}

namespace {
alignas(8) u8 stack[0x1000];
Handle resumeGame;

void keepThread(void *) {
    UGGBootStage(2, "MINIMAL-BOOT thread; before CTRPF allocator/constructors");
    const Result sync = __sync_init();
    if (R_FAILED(sync)) {
        svcSignalEvent(resumeGame);
        svcExitThread();
    }
    __system_initSyscalls();
    s64 title = 0;
    const Result titleResult = svcGetProcessInfo(&title, CUR_PROCESS_HANDLE, 0x10001);
    if (R_FAILED(titleResult) || (static_cast<u64>(title) >> 32) != 0x00040000ULL) {
        // Same system-application bypass as the patched framework startup:
        // no heap, SD or UI, but continue replying to loader lifecycle events.
        const Result loader = plgLdrInit();
        svcSignalEvent(resumeGame);
        if (R_FAILED(loader))
            svcExitThread();
        while (true) {
            svcSleepThread(250000000LL);
            const s32 event = PLGLDR__FetchEvent();
            if (event > PLG_OK)
                PLGLDR__Reply(event);
        }
    }
    initLib(); // The SAME strong allocator and stack_adjust.s as MINIMAL/FULL.
    UGGBootStage(3, "CTRPF heap allocation and linked constructors returned");

    const Result srv = srvInit();
    UGGBootResult("srvInit", srv);
    const Result fs = R_SUCCEEDED(srv) ? fsInit() : srv;
    UGGBootFsReady(fs);
    UGGBootResult("title query", titleResult);
    if (R_SUCCEEDED(titleResult))
        UGGBootTitle(static_cast<u64>(title));
    const auto *header = CTRPluginFramework::FwkSettings::Header;
    UGGBootValue("loader-heap-va", header->heapVA);
    UGGBootValue("loader-heap-bytes", header->heapSize);
    UGGBootValue("newlib-heap-va", __ctru_heap);
    UGGBootValue("newlib-heap-bytes", __ctru_heap_size);
    s64 cfw = 0;
    const Result cfwResult = svcGetSystemInfo(&cfw, 0x10000, 0);
    UGGBootResult("Luma version query", cfwResult);
    if (R_SUCCEEDED(cfwResult))
        UGGBootValue("Luma-version-encoded", static_cast<u64>(cfw));

    const Result loader = plgLdrInit();
    UGGBootResult("plgLdrInit", loader);
    UGGBootStage(16, "MINIMAL-BOOT ready; NO graphics/HID/overlay; releasing game");
    svcSignalEvent(resumeGame);
    if (R_FAILED(loader)) {
        svcUnmapProcessMemoryEx(CUR_PROCESS_HANDLE, 0x01E80000, 0x2000);
        if (R_SUCCEEDED(fs))
            fsExit();
        if (R_SUCCEEDED(srv))
            srvExit();
        svcExitThread();
    }
    while (true) {
        svcSleepThread(250000000LL);
        const s32 event = PLGLDR__FetchEvent();
        if (event <= PLG_OK)
            continue;
        if (event == PLG_ABOUT_TO_SWAP || event == PLG_ABOUT_TO_EXIT)
            svcUnmapProcessMemoryEx(CUR_PROCESS_HANDLE, 0x01E80000, 0x2000);
        if (event == PLG_ABOUT_TO_EXIT) {
            if (R_SUCCEEDED(fs))
                fsExit();
            if (R_SUCCEEDED(srv))
                srvExit();
        }
        PLGLDR__Reply(event); // EXIT never returns; SWAP waits for loader resume.
        if (event == PLG_ABOUT_TO_SWAP) {
            const Result mapped = svcMapProcessMemoryEx(
                CUR_PROCESS_HANDLE, 0x01E80000, CUR_PROCESS_HANDLE,
                __ctru_heap + __ctru_heap_size, 0x2000, static_cast<MapExFlags>(0));
            if (R_FAILED(mapped))
                svcExitThread();
        }
    }
}
} // namespace

extern "C" int __entrypoint(int) {
    UGGBootStage(1, "MINIMAL-BOOT entry; BSS only");
    const Result event = svcCreateEvent(&resumeGame, RESET_ONESHOT);
    if (R_FAILED(event))
        return 0;
    Handle thread = 0;
    const Result created =
        svcCreateThread(&thread, keepThread, 0, reinterpret_cast<u32 *>(stack + sizeof(stack)),
                        0x1A, 0);
    if (R_SUCCEEDED(created)) {
        svcWaitSynchronization(resumeGame, U64_MAX);
        svcCloseHandle(thread);
    }
    svcCloseHandle(resumeGame);
    return 0;
}
