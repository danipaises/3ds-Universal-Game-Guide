#include "CTRPluginFramework.hpp"
#include "CTRPluginFrameworkImpl/System/SystemImpl.hpp"
#include "boot.hpp"
#include "core.hpp"
#include <algorithm>
#include <limits>
extern "C" int getMemFree(void);

namespace CTRPluginFramework {
bool UGGTouchEnabled = true;
namespace {
const std::string Root = "/3ds/UniversalGameGuide";
ugg::BufferedLog debugLog;
bool testProfile = false;
class SD final : public ugg::Storage {
    bool allowed(const std::string &p) {
        return p.rfind(Root + "/", 0) == 0 && p.find("..") == std::string::npos;
    }

  public:
    uint64_t size(const std::string &p) override {
        File f;
        if (!allowed(p) || File::Open(f, p, File::READ) != 0) {
            debugLog.add("SD open failed: " + p);
            return UINT64_MAX;
        }
        return f.GetSize();
    }
    bool read(const std::string &p, uint64_t off, uint32_t count, std::string &out) override {
        out.clear();
        if (!allowed(p) || count > 256 * 1024)
            return false;
        File f;
        if (File::Open(f, p, File::READ) != 0) {
            debugLog.add("SD read/open failed: " + p);
            return false;
        }
        auto n = f.GetSize();
        if (off > n || count > n - off || f.Seek(off, File::SET) != 0)
            return false;
        out.resize(count);
        if (!count)
            return true;
        if (f.Read(&out[0], count) != 0 || f.Tell() != off + count) {
            out.clear();
            return false;
        }
        return true;
    }
    bool write(const std::string &p, const std::string &s) override {
        if (!allowed(p) || s.size() > 4096 ||
            (p.rfind(Root + "/state/", 0) != 0 && p != Root + "/config.bin" &&
             p != Root + "/unknown-title.txt" && p.rfind(Root + "/logs/", 0) != 0))
            return false;
        const auto temp = p + ".tmp", backup = p + ".bak";
        File f;
        if (File::Open(f, temp, File::WRITE | File::CREATE | File::TRUNCATE) != 0 ||
            f.Write(s.data(), s.size()) != 0 || f.Flush() != 0 || f.Close() != 0)
            return false;
        if (File::Exists(p) == 1) {
            File::Remove(backup);
            if (File::Rename(p, backup) != 0)
                return false;
        }
        return File::Rename(temp, p) == 0;
    }
};
SD sd;
ugg::Config config;
ugg::State progress;
ugg::Guide guide(sd);
ugg::Game game;
std::string gamePath, statePath, message, body, effectiveLanguage = "pt-BR";
uint32_t fingerprint = 0, active = 0, scroll = 0;
std::vector<std::string> lines;
bool revealed = false;
uint32_t navigation = 0, heldNavigation = 0, holdFrames = 0;
uint32_t keys() { return Controller::GetKeysPressed() | navigation; }
bool pressed(uint32_t key) { return (key != Key::Touchpad || config.touch) && (keys() & key) != 0; }
const Color Bg(13, 22, 34), Panel(25, 39, 56), Accent(90, 219, 160), Ink(237, 243, 250),
    Muted(168, 185, 202);
std::string fit(std::string text, float width) {
    while (!text.empty() && OSD::GetTextWidth(true, text) > width) {
        size_t pos = text.size() - 1;
        while (pos > 0 && (static_cast<unsigned char>(text[pos]) & 0xC0) == 0x80)
            --pos;
        text.resize(pos);
    }
    return text;
}
void splitLines(const std::string &text) {
    lines.clear();
    std::string current, word;
    auto flushWord = [&]() {
        if (word.empty())
            return;
        if (!current.empty() && OSD::GetTextWidth(true, current + " " + word) > 376) {
            lines.push_back(current);
            current.clear();
        }
        for (size_t i = 0; i < word.size();) {
            size_t end = i + 1;
            while (end < word.size() && (static_cast<unsigned char>(word[end]) & 0xC0) == 0x80)
                ++end;
            auto cp = word.substr(i, end - i);
            if (OSD::GetTextWidth(true, current + cp) > 376 && !current.empty()) {
                lines.push_back(current);
                current.clear();
            }
            current += cp;
            i = end;
        }
        word.clear();
    };
    for (char c : text) {
        if (c == ' ' || c == '\n' || c == '\t') {
            flushWord();
            if (c == '\n') {
                lines.push_back(current);
                current.clear();
            } else if (!current.empty())
                current += ' ';
        } else
            word += c;
    }
    flushWord();
    if (!current.empty())
        lines.push_back(current);
    if (lines.empty())
        lines.emplace_back("");
}
void chrome(const std::string &title, const std::string &subtitle) {
    const auto &t = OSD::GetTopScreen();
    const auto &b = OSD::GetBottomScreen();
    t.DrawRect(0, 0, 400, 240, Bg);
    b.DrawRect(0, 0, 320, 240, Bg);
    t.DrawRect(0, 0, 400, 28, Panel);
    t.DrawSysfont(fit(title, 376), 12, 6, Accent);
    b.DrawRect(0, 0, 320, 30, Panel);
    b.DrawSysfont(fit(subtitle, 296), 12, 7, Ink);
    if (!message.empty())
        b.DrawSysfont(fit(message, 296), 12, 218, Accent);
}
void row(const std::string &text, int i, bool selected) {
    auto &b = OSD::GetBottomScreen();
    if (selected)
        b.DrawRect(6, 34 + i * 24, 308, 23, Panel);
    b.DrawSysfont(fit(text, 292), 14, 37 + i * 24, selected ? Accent : Ink);
}
void info(const std::string &s) {
    auto &t = OSD::GetTopScreen();
    splitLines(s);
    for (size_t i = 0; i < lines.size() && i < 11; ++i)
        t.DrawSysfont(lines[i], 12, 34 + i * 17, Ink);
}
bool frame() {
    OSD::SwapBuffers();
    Sleep(Milliseconds(16));
    Controller::Update();
    const uint32_t held =
        Controller::GetKeysDown() & (Key::Up | Key::Down | Key::Left | Key::Right);
    if (held != heldNavigation) {
        heldNavigation = held;
        holdFrames = 0;
    } else
        ++holdFrames;
    navigation = held && holdFrames >= 24 && holdFrames % 6 == 0 ? held : 0;
    return !SystemImpl::WantsToSleep() && !SystemImpl::Status();
}
int choice(const std::string &title, const std::vector<std::string> &items) {
    Keyboard k(title, items);
    return k.Open();
}
bool save(bool hasGuide) {
    bool ok = sd.write(Root + "/config.bin", config.encode());
    if (hasGuide) {
        progress.last = config.remember ? active : 0;
        progress.line = config.remember ? scroll : 0;
        ok = sd.write(statePath, progress.encode(fingerprint)) && ok;
    }
    if (!ok)
        debugLog.add("Config/state write failed");
    if (!debugLog.flush(sd, Root + "/logs/latest.log"))
        message = "Não foi possível salvar o log";
    return ok;
}
void saveBeforeReturn(bool hasGuide) {
    if (save(hasGuide))
        return;
    message.clear();
    size_t selected = 0;
    while (!SystemImpl::WantsToSleep() && !SystemImpl::Status()) {
        chrome("3DS Universal Game Guide", "Falha ao salvar no SD");
        info("Não foi possível gravar todas as preferências ou o progresso do guia.\n\n"
             "Você pode tentar novamente ou voltar ao jogo. As alterações não gravadas "
             "podem ser perdidas ao fechar o jogo.\n\nB: voltar ao jogo");
        row("Tentar salvar novamente", 0, selected == 0);
        row("Voltar ao jogo", 1, selected == 1);
        if (!frame() || pressed(Key::B))
            return;
        if (pressed(Key::Up))
            selected = 0;
        if (pressed(Key::Down))
            selected = 1;
        bool open = pressed(Key::A);
        if (pressed(Key::Touchpad)) {
            const auto pos = Touch::GetPosition();
            if (pos.y >= 34 && pos.y < 82) {
                selected = (pos.y - 34) / 24;
                open = true;
            }
        }
        if (open && (selected == 1 || save(hasGuide)))
            return;
    }
}
void readPage(uint32_t p, bool restore = false) {
    if (p >= guide.pages.size())
        return;
    active = p;
    revealed = config.spoilers;
    if (!guide.text(active, body)) {
        debugLog.add("Page read/CRC failed: " + gamePath + " / " + guide.pages[active].id);
        body = "Página corrompida ou SD indisponível. Volte com B e reinstale o pacote.";
    }
    splitLines(body);
    scroll = restore ? std::min<uint32_t>(progress.line, lines.size() - 1) : 0;
    progress.last = active;
    progress.line = scroll;
}
void logContext() {
    debugLog.add(std::string("UGG version=") + ugg::Version);
    debugLog.add(std::string("model-family=") + (System::IsNew3DS() ? "New3DS" : "Old3DS"));
    debugLog.add(Utils::Format("title=%016llX", Process::GetTitleID()));
    debugLog.add("game=" + game.id + " language=" + effectiveLanguage);
    debugLog.add("guide=" + gamePath + " pages=" + std::to_string(guide.pages.size()));
    debugLog.add("newlib-free-bytes=" + std::to_string(getMemFree()));
}
void diagnostic() {
    bool details = false;
    while (!SystemImpl::WantsToSleep() && !SystemImpl::Status()) {
        chrome("Diagnóstico", std::string("UGG ") + ugg::Version);
        size_t maps = 0;
        for (const auto &page : guide.pages)
            if (!page.map.empty())
                ++maps;
        info(details ? "Dados: " + Root + "\nGuia: " + gamePath +
                           "\nHeap newlib livre: " + std::to_string(getMemFree()) +
                           " bytes\nNão é RAM total do console.\nPerfil: " +
                           (testProfile ? "hardware-test" : "release") + "\nNEEDS HARDWARE RETEST"
                     : std::string("Versão: ") + ugg::Version +
                           Utils::Format("\nTitle ID: %016llX", Process::GetTitleID()) +
                           "\nGame ID: " + (game.id.empty() ? "não reconhecido" : game.id) +
                           "\nIdioma: " + effectiveLanguage +
                           "\nGuia: " + (guide.pages.empty() ? "não carregado" : "carregado") +
                           " / " + std::to_string(guide.pages.size()) +
                           " páginas\nPáginas com mapa: " + std::to_string(maps) +
                           "\nLogging: " + (config.logging ? "ON" : "OFF"));
        row("L/R ou toque: detalhes", 0, false);
        row("A: gravar log (se ligado)", 1, false);
        row("B: voltar", 2, false);
        if (!frame() || pressed(Key::B))
            break;
        bool exportLog = pressed(Key::A);
        if (pressed(Key::L) || pressed(Key::R))
            details = !details;
        if (pressed(Key::Touchpad)) {
            auto pos = Touch::GetPosition();
            if (pos.y >= 34 && pos.y < 58)
                details = !details;
            else if (pos.y >= 58 && pos.y < 82)
                exportLog = true;
            else if (pos.y >= 82 && pos.y < 106)
                break;
        }
        if (exportLog) {
            logContext();
            message = !config.logging                                 ? "Logging está OFF"
                      : debugLog.flush(sd, Root + "/logs/latest.log") ? "Log gravado"
                                                                      : "Erro ao gravar log";
        }
    }
}
void settings() {
    std::vector<std::string> options = {"Idioma: Português do Brasil",
                                        config.spoilers ? "Spoilers: mostrar" : "Spoilers: ocultar",
                                        "Alterar hotkey",
                                        "Restaurar START + SELECT + A",
                                        config.touch ? "Touch: ON" : "Touch: OFF",
                                        config.logging ? "Debug Logging: ON" : "Debug Logging: OFF",
                                        config.remember ? "Lembrar última página: ON"
                                                        : "Lembrar última página: OFF",
                                        "Diagnóstico",
                                        "Voltar"};
    int n = choice("Configurações / PT-BR", options);
    if (n == 1)
        config.spoilers = !config.spoilers;
    if (n == 4) {
        config.touch = !config.touch;
        UGGTouchEnabled = config.touch;
    }
    if (n == 5) {
        config.logging = !config.logging;
        debugLog.enable(config.logging);
        logContext();
    }
    if (n == 6)
        config.remember = !config.remember;
    if (n == 7)
        diagnostic();
    if (n == 3) {
        if (!SystemImpl::RosalinaHotkey ||
            (13 & SystemImpl::RosalinaHotkey) != SystemImpl::RosalinaHotkey)
            config.hotkey = 13;
        else
            message = "Atalho conflita com Rosalina";
    }
    if (n == 2) {
        std::vector<std::string> buttons = {"A",       "B",        "SELECT", "START",
                                            "DIREITA", "ESQUERDA", "CIMA",   "BAIXO",
                                            "R",       "L",        "X",      "Y"};
        uint32_t mask = 0;
        for (int i = 0; i < 4; ++i) {
            auto list = buttons;
            list.emplace_back("Concluir");
            int b = choice("Escolha 2 a 4 botões", list);
            if (b < 0 || b == 12)
                break;
            mask |= 1u << b;
        }
        ugg::Config candidate = config;
        candidate.hotkey = mask;
        ugg::Config validated;
        if (validated.decode(candidate.encode()) &&
            (!SystemImpl::RosalinaHotkey ||
             (mask & SystemImpl::RosalinaHotkey) != SystemImpl::RosalinaHotkey)) {
            config.hotkey = mask;
            message = "Atalho salvo ao fechar";
        } else
            message = "Combinação inválida/conflitante";
    }
}
void mapView(const std::string &id) {
    UGGBootStage(25, "map metadata/tile loading begin");
    if (!ugg::safeId(id))
        return;
    std::string base = Root + "/maps/" + game.id + "/" + id, h;
    if (!sd.read(base + ".ugm", 0, 12, h) || h.compare(0, 4, "UGM1")) {
        message = "Mapa indisponível";
        debugLog.add("Map missing: " + base);
        return;
    }
    uint32_t levels = ugg::u32(h.data() + 4), crc = ugg::u32(h.data() + 8);
    std::string dims;
    if (!levels || levels > 3 || sd.size(base + ".ugm") != 12 + levels * 8 ||
        !sd.read(base + ".ugm", 12, levels * 8, dims) || ugg::crc32(dims) != crc) {
        message = "Mapa corrompido";
        debugLog.add("Map header/CRC invalid: " + base);
        return;
    }
    for (uint32_t i = 0; i < levels; ++i) {
        uint32_t c = ugg::u32(dims.data() + i * 8), r = ugg::u32(dims.data() + i * 8 + 4);
        if (!c || !r || c > 64 || r > 64) {
            message = "Mapa fora do limite";
            debugLog.add("Map dimensions invalid: " + base);
            return;
        }
    }
    uint32_t z = 0, x = 0, y = 0;
    bool reload = true;
    unsigned dirty = 2;
    ugg::Tile tile;
    while (!SystemImpl::WantsToSleep() && !SystemImpl::Status()) {
        uint32_t cols = ugg::u32(dims.data() + z * 8), rows = ugg::u32(dims.data() + z * 8 + 4);
        if (reload) {
            std::string path = base + "-" + std::to_string(z) + "-" + std::to_string(x) + "-" +
                               std::to_string(y) + ".ugi";
            if (!ugg::loadTile(sd, path, tile)) {
                message = "Tile corrompido";
                debugLog.add("Tile invalid: " + path);
                return;
            }
            reload = false;
            UGGBootStage(26, "first map tile loaded");
            dirty = 2;
        }
        if (dirty) {
            --dirty;
            chrome("Mapa esquemático / " + guide.pages[active].title,
                   "Zoom " + std::to_string(z + 1) + " / tile " + std::to_string(x + 1) + "," +
                       std::to_string(y + 1));
            auto &t = OSD::GetTopScreen();
            for (uint32_t py = 0; py < tile.height; ++py)
                for (uint32_t px = 0; px < tile.width; ++px) {
                    uint16_t v = tile.pixels[py * tile.width + px];
                    t.DrawPixel(40 + px, 32 + py,
                                Color(((v >> 11) & 31) * 255 / 31, ((v >> 5) & 63) * 255 / 63,
                                      (v & 31) * 255 / 31));
                }
            row("Cima / pan", 0, false);
            row("Esquerda / pan", 1, false);
            row("Direita / pan", 2, false);
            row("Baixo / pan", 3, false);
            row("L/R: zoom", 4, false);
            row("B: voltar", 5, false);
        }
        if (!frame() || pressed(Key::B))
            break;
        uint32_t oldx = x, oldy = y, oldz = z;
        uint32_t k = keys();
        if (pressed(Key::Touchpad)) {
            auto p = Touch::GetPosition();
            if (p.y >= 34 && p.y < 178) {
                unsigned n = (p.y - 34) / 24;
                if (n < 4)
                    k |= (n == 0 ? Key::Up : n == 1 ? Key::Left : n == 2 ? Key::Right : Key::Down);
                else if (n == 4)
                    k |= Key::R;
                else
                    break;
            }
        }
        if ((k & Key::Left) && x)
            x--;
        if ((k & Key::Right) && x + 1 < cols)
            x++;
        if ((k & Key::Up) && y)
            y--;
        if ((k & Key::Down) && y + 1 < rows)
            y++;
        if ((k & Key::R) && z + 1 < levels) {
            ++z;
            x *= 2;
            y *= 2;
        }
        if ((k & Key::L) && z) {
            --z;
            x /= 2;
            y /= 2;
        }
        x = std::min(x, ugg::u32(dims.data() + z * 8) - 1);
        y = std::min(y, ugg::u32(dims.data() + z * 8 + 4) - 1);
        reload = oldx != x || oldy != y || oldz != z;
    }
}
void pageView(uint32_t p, bool restore = false) {
    readPage(p, restore);
    while (!SystemImpl::WantsToSleep() && !SystemImpl::Status()) {
        bool hidden = guide.pages[active].flags && !revealed;
        chrome(game.name, hidden ? "PT-BR / SPOILER" : "PT-BR / " + guide.pages[active].title);
        auto &t = OSD::GetTopScreen();
        if (hidden) {
            t.DrawSysfont("SPOILER", 12, 54, Accent);
            t.DrawSysfont("A: revelar esta página", 12, 82, Ink);
        } else
            for (size_t i = scroll; i < lines.size() && i < scroll + 11; ++i)
                t.DrawSysfont(lines[i], 12, 34 + (i - scroll) * 17, Ink);
        if (!hidden && lines.size() > 11) {
            t.DrawRect(393, 34, 3, 187, Panel);
            const unsigned height = std::max<size_t>(5, 187 * 11 / lines.size());
            const unsigned pos = (187 - height) * scroll / std::max<size_t>(1, lines.size() - 1);
            t.DrawRect(393, 34 + pos, 3, height, Accent);
        }
        row("L: anterior / R: próxima", 0, false);
        row("Cima / baixo: rolar", 1, false);
        row(progress.get(false, active) ? "Y: remover favorito" : "Y: adicionar favorito", 2,
            false);
        row(progress.get(true, active) ? "X: desmarcar conclusão" : "X: marcar conclusão", 3,
            false);
        row(guide.pages[active].map.empty() ? "Sem mapa nesta página" : "A / toque: abrir mapa", 4,
            false);
        row("B: voltar ao índice", 5, false);
        OSD::GetBottomScreen().DrawSysfont(
            std::to_string(active + 1) + "/" + std::to_string(guide.pages.size()), 12, 188, Muted);
        if (!frame() || pressed(Key::B))
            break;
        uint32_t k = keys();
        if (pressed(Key::Touchpad)) {
            auto pos = Touch::GetPosition();
            if (pos.y >= 34 && pos.y < 178) {
                unsigned n = (pos.y - 34) / 24;
                if (n == 0)
                    k |= pos.x < 160 ? Key::L : Key::R;
                else if (n == 1)
                    k |= pos.x < 160 ? Key::Up : Key::Down;
                else if (n == 2)
                    k |= Key::Y;
                else if (n == 3)
                    k |= Key::X;
                else if (n == 4)
                    k |= Key::A;
                else
                    break;
            }
        }
        if (k & Key::Y)
            progress.toggle(false, active);
        if (k & Key::X)
            progress.toggle(true, active);
        if ((k & Key::Up) && scroll)
            scroll--;
        if ((k & Key::Down) && scroll + 1 < lines.size() && !hidden)
            scroll++;
        if ((k & Key::L) && active)
            readPage(active - 1);
        if ((k & Key::R) && active + 1 < guide.pages.size())
            readPage(active + 1);
        if (k & Key::A) {
            if (guide.pages[active].flags && !revealed)
                revealed = true;
            else if (!guide.pages[active].map.empty()) {
                mapView(guide.pages[active].map);
                splitLines(body);
            }
        }
        progress.last = active;
        progress.line = scroll;
    }
}
void searchGuide();
void pageList(const std::vector<uint32_t> &indices, const std::string &label,
              bool allowSearch = false) {
    if (indices.empty()) {
        message = "Nenhuma página encontrada";
        return;
    }
    size_t selected = 0;
    while (!SystemImpl::WantsToSleep() && !SystemImpl::Status()) {
        chrome(game.name, label);
        info(std::string("A / toque: abrir\nD-Pad ou Circle Pad: navegar\nL/R: pular sete "
                         "entradas\nB: voltar") +
             (allowSearch ? " / X: buscar" : "") +
             "\n\nMarcadores e progresso ficam apenas na pasta do guia no SD.");
        size_t first = (selected / 7) * 7;
        for (size_t i = first; i < indices.size() && i < first + 7; ++i) {
            uint32_t n = indices[i];
            std::string name = guide.pages[n].flags && !config.spoilers
                                   ? "SPOILER — página " + std::to_string(n + 1)
                                   : guide.pages[n].title;
            row((progress.get(true, n) ? "[x] " : "[ ] ") + name, i - first, i == selected);
        }
        if (!frame() || pressed(Key::B))
            break;
        if (pressed(Key::Up) && selected)
            --selected;
        if (pressed(Key::Down) && selected + 1 < indices.size())
            ++selected;
        if (pressed(Key::L))
            selected = selected >= 7 ? selected - 7 : 0;
        if (pressed(Key::R))
            selected = std::min(selected + 7, indices.size() - 1);
        bool open = pressed(Key::A);
        if (pressed(Key::Touchpad)) {
            auto pos = Touch::GetPosition();
            if (pos.y >= 34 && pos.y < 202) {
                size_t n = first + (pos.y - 34) / 24;
                if (n < indices.size()) {
                    selected = n;
                    open = true;
                }
            }
        }
        if (open)
            pageView(indices[selected]);
        if (allowSearch && pressed(Key::X))
            searchGuide();
    }
}
void searchGuide() {
    Keyboard keyboard("Pesquisar início do nome / mínimo 2 letras");
    keyboard.SetMaxLength(64);
    std::string query;
    if (keyboard.Open(query) != 0)
        return;
    UGGBootStage(23, "offline search index lookup begin");
    std::vector<uint32_t> matches;
    const bool searched = guide.search(query, config.spoilers, matches);
    UGGBootStage(24, "offline search index lookup returned");
    if (searched)
        pageList(matches, "Busca / " + query);
    else {
        message = "Consulta curta ou índice inválido";
        debugLog.add("Search failed: " + gamePath);
    }
}
struct PauseGuard {
    PauseGuard() { Process::Pause(); }
    ~PauseGuard() { Process::Play(); }
};
void overlay() {
    UGGBootStage(18, "full overlay requested; before pause/catalog/guide");
    PauseGuard pause;
    struct ReleasePages {
        ~ReleasePages() {
            std::vector<ugg::Page>().swap(guide.pages);
            std::vector<std::string>().swap(lines);
            std::string().swap(body);
        }
    } release;
    message.clear();
    guide.pages.clear();
    effectiveLanguage = config.language;
    navigation = heldNavigation = holdFrames = 0;
    Controller::Update();
    // Consume the opening chord so A does not immediately select an entry.
    while (Controller::GetKeysDown() & config.hotkey) {
        Sleep(Milliseconds(16));
        Controller::Update();
        if (SystemImpl::WantsToSleep() || SystemImpl::Status())
            return;
    }
    UGGBootStage(19, "titles.bin lookup begin");
    auto result = ugg::lookup(sd, Root + "/titles.bin", Process::GetTitleID(), game);
    UGGBootStage(20, "catalog lookup returned");
    bool loaded = false;
    debugLog.add(Utils::Format("Overlay title=%016llX", Process::GetTitleID()));
    debugLog.add("Lookup status=" + std::to_string(static_cast<unsigned>(result)));
    if (result == ugg::Lookup::Found) {
        UGGBootStage(21, "recognized game; guide loading begin");
        debugLog.add("Found game=" + game.id + " / " + game.name);
        gamePath = Root + "/guides/" + config.language + "/" + game.id + ".ugg";
        if (getMemFree() >= 1024 * 1024)
            loaded =
                guide.openLanguage(Root + "/guides", game.id, config.language, effectiveLanguage);
        else
            message = "Memória insuficiente para abrir o guia";
        if (!effectiveLanguage.empty())
            gamePath = Root + "/guides/" + effectiveLanguage + "/" + game.id + ".ugg";
        debugLog.add("Guide " + gamePath + (loaded ? " loaded" : " unavailable/low-memory"));
        if (loaded) {
            UGGBootStage(22, "guide index loaded");
            fingerprint = guide.fingerprint();
            statePath = Root + "/state/" + (testProfile ? "test-" : "") + effectiveLanguage + "-" +
                        game.id + ".bin";
            progress = {};
            std::string state;
            if (!sd.read(statePath, 0, ugg::StateSize, state) ||
                !(progress.decode(state, fingerprint) ||
                  ugg::migrateState(sd, gamePath.substr(0, gamePath.size() - 4) + ".ugr", state,
                                    fingerprint, guide.pages.size(), progress))) {
                if (sd.read(statePath + ".bak", 0, ugg::StateSize, state))
                    if (!progress.decode(state, fingerprint))
                        ugg::migrateState(sd, gamePath.substr(0, gamePath.size() - 4) + ".ugr",
                                          state, fingerprint, guide.pages.size(), progress);
            }
            if (progress.last >= guide.pages.size())
                progress = {};
            if (!config.remember)
                progress.last = progress.line = 0;
            active = progress.last;
            scroll = progress.line;
        }
    }
    logContext();
    if (!loaded) {
        const bool guideMissing = result == ugg::Lookup::Found && sd.size(gamePath) == UINT64_MAX;
        std::string tid = Utils::Format("%016llX", Process::GetTitleID());
        size_t selected = 0;
        bool running = true;
        while (running && !SystemImpl::WantsToSleep() && !SystemImpl::Status()) {
            chrome(result == ugg::Lookup::Found ? game.name : "3DS Universal Game Guide",
                   "Diagnóstico");
            info((result == ugg::Lookup::Corrupt   ? "Catálogo ausente ou corrompido."
                  : result == ugg::Lookup::Unknown ? "Jogo não reconhecido."
                  : guideMissing                   ? "Jogo reconhecido, mas guia não instalado."
                  : message == "Memória insuficiente para abrir o guia"
                      ? message
                      : "Arquivo de guia corrompido.") +
                 std::string("\n\nTitle ID: ") + tid + "\nRegião: não detectável\nVersão: " +
                 ugg::Version + "\nAbra uma issue com este Title ID." +
                 "\n\nA / toque: selecionar\nD-Pad / Circle Pad: navegar\nB: voltar ao jogo");
            row("Anotar Title ID no SD", 0, selected == 0);
            row("Voltar ao jogo", 1, selected == 1);
            row("Configurações", 2, selected == 2);
            if (!frame() || pressed(Key::B))
                break;
            if (pressed(Key::Up) && selected)
                --selected;
            if (pressed(Key::Down) && selected < 2)
                ++selected;
            bool open = pressed(Key::A);
            if (pressed(Key::Touchpad)) {
                auto pos = Touch::GetPosition();
                if (pos.y >= 34 && pos.y < 106) {
                    selected = (pos.y - 34) / 24;
                    open = true;
                }
            }
            if (open) {
                if (selected == 0) {
                    const std::string path = Root + "/logs/unknown_titles.log";
                    std::string records;
                    auto size = sd.size(path);
                    if (size <= 4096)
                        sd.read(path, 0, size, records);
                    if (!ugg::validUtf8(records))
                        records.clear();
                    records += tid + " version=" + ugg::Version + "\n";
                    while (records.size() > 4096)
                        records.erase(0, records.find('\n') + 1);
                    message =
                        sd.write(path, records) && sd.write(Root + "/unknown-title.txt", tid + "\n")
                            ? "ID anotado no SD"
                            : "Erro no SD";
                } else if (selected == 1)
                    running = false;
                else
                    settings();
            }
        }
        saveBeforeReturn(false);
        return;
    }
    std::vector<std::string> menu = {
        "Continuar de onde parei", "Índice do guia", "Pesquisar offline", "Favoritos", "Mapas",
        "Configurações",           "Voltar ao jogo"};
    size_t selected = 0;
    bool running = true;
    while (running && !SystemImpl::WantsToSleep() && !SystemImpl::Status()) {
        chrome(game.name, "Guia PT-BR / versão experimental");
        info("A / toque: selecionar\nB: voltar ao jogo\nD-Pad / Circle Pad: navegar\n\nContinuar "
             "abre a última página consultada. O plugin não lê o progresso interno do jogo.");
        for (size_t i = 0; i < menu.size(); ++i)
            row(menu[i], i, i == selected);
        if (!frame() || pressed(Key::B))
            break;
        if (pressed(Key::Up) && selected)
            --selected;
        if (pressed(Key::Down) && selected + 1 < menu.size())
            ++selected;
        bool open = pressed(Key::A);
        if (pressed(Key::X)) {
            selected = 2;
            open = true;
        }
        if (pressed(Key::Touchpad)) {
            auto pos = Touch::GetPosition();
            if (pos.y >= 34 && pos.y < 202) {
                selected = (pos.y - 34) / 24;
                open = true;
            }
        }
        if (!open)
            continue;
        std::vector<uint32_t> indices;
        if (selected == 0)
            pageView(progress.last, true);
        if (selected == 1) {
            for (uint32_t i = 0; i < guide.pages.size(); ++i)
                indices.push_back(i);
            pageList(indices, "Índice", true);
        }
        if (selected == 2)
            searchGuide();
        if (selected == 3) {
            for (uint32_t i = 0; i < guide.pages.size(); ++i)
                if (progress.get(false, i))
                    indices.push_back(i);
            pageList(indices, "Favoritos");
        }
        if (selected == 4) {
            for (uint32_t i = 0; i < guide.pages.size(); ++i)
                if (!guide.pages[i].map.empty())
                    indices.push_back(i);
            pageList(indices, "Mapas");
        }
        if (selected == 5)
            settings();
        if (selected == 6)
            running = false;
    }
    saveBeforeReturn(true);
}
} // namespace
void PatchProcess(FwkSettings &s) {
    // Settings only: no game-specific patches, input injection or memory edits.
    s.AllowActionReplay = false;
    s.AllowSearchEngine = false;
    s.TryLoadSDSounds = false;
    s.UseGameHidMemory = false;
}
int main() {
    UGGBootStage(16, "full main entered; before SD config/catalog reads");
    UGGBootHeap(getMemFree());
    std::string bytes;
    auto versionSize = sd.size(Root + "/VERSION");
    if (versionSize <= 128 && sd.read(Root + "/VERSION", 0, versionSize, bytes))
        testProfile = bytes.find("hardware-test") != std::string::npos;
    if (!sd.read(Root + "/config.bin", 0, 32, bytes) || !config.decode(bytes)) {
        if (sd.read(Root + "/config.bin.bak", 0, 32, bytes))
            config.decode(bytes);
    }
    UGGTouchEnabled = config.touch;
    debugLog.enable(config.logging);
    logContext();
    if (SystemImpl::RosalinaHotkey &&
        (config.hotkey & SystemImpl::RosalinaHotkey) == SystemImpl::RosalinaHotkey) {
        for (uint32_t candidate :
             {uint32_t(Key::L | Key::R | Key::Y), uint32_t(Key::L | Key::R | Key::X),
              uint32_t(Key::Start | Key::Select | Key::B)})
            if ((candidate & SystemImpl::RosalinaHotkey) != SystemImpl::RosalinaHotkey) {
                config.hotkey = candidate;
                break;
            }
    }
    UGGBootStage(17, "configuration loaded; entering hotkey loop");
    while (!SystemImpl::Status()) {
        if (SystemImpl::WantsToSleep()) {
            SystemImpl::ReadyToSleep();
            continue;
        }
        Controller::Update();
        if (Controller::IsKeysPressed(config.hotkey)) {
            overlay();
            SystemImpl::ReadyToSleep();
        }
        Sleep(Milliseconds(16));
    }
    return 0;
}
} // namespace CTRPluginFramework
