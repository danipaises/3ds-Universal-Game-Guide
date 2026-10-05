#!/usr/bin/env python3
"""Reapply a documented patch from the pinned pristine archive, idempotently."""

import difflib
import json
import re
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / ".deps/ctrpluginframework-0.8.0"
lock = json.loads((ROOT / "data/dependencies.lock.json").read_text())
for name, target in [
    ("libcwav", FW / "Library/libcwav"),
    ("libncsnd", FW / "Library/libcwav/libncsnd"),
]:
    source = ROOT / ".deps" / name
    if not (target / "Makefile").is_file():
        shutil.copytree(source, target, dirs_exist_ok=True)
dep = next(d for d in lock["dependencies"] if d["name"] == "ctrpf")
with tarfile.open(ROOT / "research" / dep["archive"]) as tf:
    member = next(m for m in tf.getmembers() if m.name.endswith("/Library/source/pluginInit.cpp"))
    original = tf.extractfile(member).read().decode()
    member = next(m for m in tf.getmembers() if m.name.endswith("/Library/Makefile"))
    original_make = tf.extractfile(member).read().decode()
    member = next(
        m
        for m in tf.getmembers()
        if m.name.endswith("/Library/source/CTRPluginFramework/System/Controller.cpp")
    )
    original_controller = tf.extractfile(member).read().decode()
    member = next(m for m in tf.getmembers() if m.name.endswith("/Library/source/csvc.s"))
    original_csvc = tf.extractfile(member).read().decode()
s = original
start = s.index("        // Set current working directory")
end = s.index("\n    static void     InitHeap", start)
s = (
    s[:start]
    + """        // Universal Game Guide downstream patch: confined framework output.
        const std::string root = "/3ds/UniversalGameGuide";
        Directory::Create("/3ds");
        Directory::Create(root);
        Directory::Create(root + "/state");
        Directory::Create(root + "/runtime");
        Directory::Create(root + "/logs");
        Directory::ChangeWorkingDirectory(root + "/runtime/");
    }
"""
    + s[end:]
)
s = (
    s.replace('"/cheats"', '"/3ds/UniversalGameGuide/runtime/cheats"')
    .replace('"/cheats/%016llX.txt"', '"/3ds/UniversalGameGuide/runtime/cheats/%016llX.txt"')
    .replace('"/Screenshots"', '"/3ds/UniversalGameGuide/runtime/screenshots"')
)
# A default plugin can also be selected for system applications. Bypass heap,
# services and graphics, but keep replying to Luma's exit/swap/HOME protocol.
s = s.replace(
    "        initLib();",
    """        // UGG: system applications/applets must not initialize this overlay.
        s64 titleId = 0;
        if (R_FAILED(svcGetProcessInfo(&titleId, CUR_PROCESS_HANDLE, 0x10001)) ||
            (static_cast<u64>(titleId) >> 32) != 0x00040000ULL)
        {
            // No initLib(): it maps generic hook memory before services start.
            // plgLdrInit uses the loader port directly, without srv or graphics.
            const Result loader = plgLdrInit();
            svcSignalEvent(g_continueGameEvent);
            if (R_FAILED(loader))
                svcExitThread();
            while (true)
            {
                svcSleepThread(250000000LL);
                const s32 event = PLGLDR__FetchEvent();
                if (event > PLG_OK)
                    PLGLDR__Reply(event); // swap waits; exit terminates this thread
            }
        }

        initLib();""",
)
# These generic hooks support cheats and game HID redirection; neither is used.
s = s.replace(
    "        // Init Screen",
    """        // UGG startup bypass: standard HID, before graphics/OSD initialization.
        hidExitFake();
        const Result uggHid = hidInit();
        bool uggBypass = false;
        if (R_SUCCEEDED(uggHid))
        {
            svcSleepThread(20000000LL);
            hidScanInput();
            uggBypass = (hidKeysHeld() & KEY_R) != 0;
            hidExit();
        }
        hidInitFake(); // restore the upstream initialization contract
        if (uggBypass)
        {
            // Loader allocation already occurred; this bypass only skips CTRPF UI.
            hidExitFake();
            ncsndExit();
            cfguExit();
            fsExit();
            amExit();
            acExit();
            srvExit();
            svcSignalEvent(g_continueGameEvent);
            while (true)
            {
                svcSleepThread(250000000LL);
                const s32 event = PLGLDR__FetchEvent();
                if (event > PLG_OK)
                    PLGLDR__Reply(event);
            }
        }

        // Init Screen""",
)
if "const Result uggHid" not in s:
    raise RuntimeError("Pinned framework startup anchor changed")
# Hardware-retest checkpoints preserve service order and the loader protocol.
# The earliest checkpoints only touch fixed BSS; SD starts after fsInit succeeds.
s = s.replace(
    '#include "plgldr.h"',
    '#include "plgldr.h"\nextern "C" void UGGBootStage(unsigned, const char *);\n'
    'extern "C" void UGGBootResult(const char *, Result);\n'
    'extern "C" void UGGBootTitle(u64);\n'
    'extern "C" void UGGBootFsReady(Result);',
)


def checkpoint(anchor, replacement):
    global s
    if s.count(anchor) != 1:
        raise RuntimeError("Pinned checkpoint anchor changed: " + anchor)
    s = s.replace(anchor, replacement)


checkpoint(
    "    int   __entrypoint(int arg)\n    {",
    '    int   __entrypoint(int arg)\n    {\n        UGGBootStage(1, "plugin entry; BSS only");',
)
checkpoint(
    "    void    KeepThreadMain(void *arg UNUSED)\n    {",
    "    void    KeepThreadMain(void *arg UNUSED)\n    {\n"
    '        UGGBootStage(2, "keep thread entered; before initLib/constructors");',
)
checkpoint(
    "        initLib();",
    '        initLib();\n        UGGBootStage(3, "initLib/constructors complete");',
)
checkpoint(
    "        srvInit();",
    '        UGGBootStage(4, "srvInit begin");\n        UGGBootResult("srvInit", srvInit());',
)
checkpoint(
    "        fsInit();",
    '        UGGBootStage(5, "fsInit begin");\n        UGGBootFsReady(fsInit());',
)
for call in ["acInit()", "amInit()", "cfguInit()"]:
    checkpoint("        " + call + ";", '        UGGBootResult("' + call + '", ' + call + ");")
s = s.replace(
    "        ncsndInit(false);", '        UGGBootResult("ncsndInit", ncsndInit(false));', 1
)
checkpoint("        plgLdrInit();", '        UGGBootResult("plgLdrInit", plgLdrInit());')
checkpoint(
    "        // Set cwav VA to PA function",
    '        UGGBootStage(7, "basic service calls returned; before Kernel/System/Process init");\n\n'
    "        // Set cwav VA to PA function",
)
checkpoint(
    "        ProcessImpl::Initialize();",
    '        ProcessImpl::Initialize();\n        UGGBootStage(8, "process initialized");\n'
    "        UGGBootTitle(Process::GetTitleID());",
)
checkpoint(
    "        ScreenImpl::Initialize();",
    '        ScreenImpl::Initialize();\n        UGGBootStage(9, "screens initialized");',
)
checkpoint(
    "        OSDImpl::_Initialize();",
    '        OSDImpl::_Initialize();\n        UGGBootStage(10, "OSD initialized");',
)
checkpoint(
    "        InitHeap();",
    '        InitHeap();\n        UGGBootStage(11, "framework FS and 1MiB heap initialized");',
)
checkpoint(
    "        Preferences::LoadSettings();",
    '        Preferences::LoadSettings();\n        UGGBootStage(12, "HID/settings ready; releasing game");',
)
checkpoint(
    "        // Wait for the required time",
    '        UGGBootStage(13, "GSP ready; waiting before main thread");\n\n'
    "        // Wait for the required time",
)
checkpoint(
    "        Initialize();",
    '        UGGBootStage(14, "main thread font/screenshots initialization begin");\n'
    '        Initialize();\n        UGGBootStage(15, "CTRPF initialized; about to call plugin main");',
)
start = s.index("        // Install CRO hook")
end = s.index("        // Init sdmc & paths", start)
s = s[:start] + "        // UGG: CRO and game HID hooks deliberately omitted.\n\n" + s[end:]
m = original_make.replace(
    "@cd libcwav && git pull", "@true # checksum-pinned dependencies"
).replace("-Wall -Werror", "-Wall -Wno-error")
# Archives have no upstream .git; never derive SDK identity from the parent
# project's repository. The build script also supplies these pinned values.
for variable, value in {
    "CTRPF_REVISION": "0.8.0",
    "CTRPF_VERSION_MAJOR": "0",
    "CTRPF_VERSION_MINOR": "8",
    "CTRPF_VERSION_BUILD": "0",
    "COMMIT": "a502818c",
}.items():
    m, changed = re.subn(
        rf"^export {variable}\s*:=.*$", f"export {variable} := {value}", m, flags=re.MULTILINE
    )
    if changed != 1:
        raise RuntimeError(f"Pinned SDK metadata definition changed: {variable}")
(FW / "Library/source/pluginInit.cpp").write_text(s)
(FW / "Library/Makefile").write_text(m)
controller = original_controller.replace(
    "namespace CTRPluginFramework\n{",
    "namespace CTRPluginFramework\n{\n    extern bool UGGTouchEnabled;",
)
controller = controller.replace(
    "        _keysReleased = hidKeysUp();",
    """        _keysReleased = hidKeysUp();
        // Only local CTRPF input masks; never modify game HID shared memory.
        if (!UGGTouchEnabled)
        {
            _keysDown &= ~Key::Touchpad;
            _keysHeld &= ~Key::Touchpad;
            _keysReleased &= ~Key::Touchpad;
        }""",
)
if "extern bool UGGTouchEnabled" not in controller:
    raise RuntimeError("Pinned Controller anchor changed")
(FW / "Library/source/CTRPluginFramework/System/Controller.cpp").write_text(controller)
patch = "".join(
    difflib.unified_diff(
        original.splitlines(True),
        s.splitlines(True),
        fromfile="a/Library/source/pluginInit.cpp",
        tofile="b/Library/source/pluginInit.cpp",
    )
)
patch += "".join(
    difflib.unified_diff(
        original_make.splitlines(True),
        m.splitlines(True),
        fromfile="a/Library/Makefile",
        tofile="b/Library/Makefile",
    )
)
patch += "".join(
    difflib.unified_diff(
        original_controller.splitlines(True),
        controller.splitlines(True),
        fromfile="a/Library/source/CTRPluginFramework/System/Controller.cpp",
        tofile="b/Library/source/CTRPluginFramework/System/Controller.cpp",
    )
)
# Luma 13.1.1 predates the magic/R6 ABI. Current Luma retains the original
# five-argument ABI for zero flags. Nonzero flags still need the new ABI.
old_wrapper = """    mov r6, r0 @ Move the dst handle to r6 to make room for magic value
    mov r0, #0xFFFFFFF2 @ Set r0 to magic value, which allows for backwards compatibility"""
new_wrapper = """    @ UGG: flags=0 uses the legacy ABI supported by old AND current Luma.
    cmp r5, #0
    movne r6, r0 @ Nonzero flags require the newer magic/R6 ABI
    movne r0, #0xFFFFFFF2"""
if original_csvc.count(old_wrapper) != 1:
    raise RuntimeError("Pinned MapProcessMemoryEx ABI anchor changed")
csvc = original_csvc.replace(old_wrapper, new_wrapper)
(FW / "Library/source/csvc.s").write_text(csvc)
patch += "".join(
    difflib.unified_diff(
        original_csvc.splitlines(True),
        csvc.splitlines(True),
        fromfile="a/Library/source/csvc.s",
        tofile="b/Library/source/csvc.s",
    )
)
(ROOT / "docs/CTRPF_FILESYSTEM.patch").write_text(patch)
print(
    "Pinned framework patch applied (filesystem confinement, offline build, GCC16 upstream warnings)."
)
