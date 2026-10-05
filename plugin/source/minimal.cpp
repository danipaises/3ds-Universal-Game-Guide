#include "CTRPluginFramework.hpp"
#include "CTRPluginFrameworkImpl/System/SystemImpl.hpp"
#include "boot.hpp"
extern "C" int getMemFree(void);

namespace CTRPluginFramework {
bool UGGTouchEnabled = true;
void PatchProcess(FwkSettings &s) {
    s.AllowActionReplay = false;
    s.AllowSearchEngine = false;
    s.TryLoadSDSounds = false;
    s.UseGameHidMemory = false;
}
int main() {
    UGGBootStage(16, "minimal main; no guide/config/catalog parsing");
    const u64 title = Process::GetTitleID();
    UGGBootTitle(title);
    UGGBootHeap(getMemFree());
    OSD::Notify("UGG MINIMAL 0.2.1 carregado");
    UGGBootStage(17, "load indication requested; entering hotkey loop");
    constexpr u32 combo = Key::Start | Key::Select | Key::A;
    while (!SystemImpl::Status()) {
        if (SystemImpl::WantsToSleep()) {
            SystemImpl::ReadyToSleep();
            continue;
        }
        Controller::Update();
        if (Controller::IsKeysPressed(combo)) {
            UGGBootStage(18, "minimal overlay requested");
            Process::Pause();
            Controller::Update();
            while ((Controller::GetKeysDown() & combo) && !SystemImpl::Status() &&
                   !SystemImpl::WantsToSleep()) {
                Sleep(Milliseconds(16));
                Controller::Update();
            }
            while (!SystemImpl::Status() && !SystemImpl::WantsToSleep()) {
                auto &top = OSD::GetTopScreen();
                auto &bottom = OSD::GetBottomScreen();
                top.DrawRect(0, 0, 400, 240, Color::Black);
                bottom.DrawRect(0, 0, 320, 240, Color::Black);
                top.DrawSysfont("UGG MINIMAL 0.2.1-alpha", 12, 20, Color::White);
                top.DrawSysfont(Utils::Format("Title ID: %016llX", title), 12, 52, Color::White);
                top.DrawSysfont(Utils::Format("Heap newlib: %d bytes", getMemFree()), 12, 84,
                                Color::White);
                top.DrawSysfont(Utils::Format("Boot log result: %08lX", u32(UGGBootLastWrite())),
                                12, 116, Color::White);
                bottom.DrawSysfont("NEEDS HARDWARE RETEST", 12, 28, Color::White);
                bottom.DrawSysfont("B: voltar ao jogo", 12, 64, Color::White);
                OSD::SwapBuffers();
                UGGBootStage(19, "minimal overlay frame submitted");
                Sleep(Milliseconds(16));
                Controller::Update();
                if (Controller::IsKeyPressed(Key::B))
                    break;
            }
            Process::Play();
            UGGBootStage(20, "minimal returned to game");
            SystemImpl::ReadyToSleep();
        }
        Sleep(Milliseconds(16));
    }
    return 0;
}
} // namespace CTRPluginFramework
