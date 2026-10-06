#include "core.hpp"
#include <algorithm>
#include <cassert>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <random>
#include <sstream>
using namespace ugg;
struct Memory : Storage {
    std::map<std::string, std::string> files;
    uint32_t largest = 0;
    unsigned reads = 0;
    bool failWrites = false;
    uint64_t size(const std::string &p) override {
        return files.count(p) ? files[p].size() : UINT64_MAX;
    }
    bool read(const std::string &p, uint64_t o, uint32_t n, std::string &s) override {
        ++reads;
        largest = std::max(largest, n);
        s.clear();
        if (!files.count(p) || o > files[p].size() || n > files[p].size() - o)
            return false;
        s = files[p].substr(o, n);
        return true;
    }
    bool write(const std::string &p, const std::string &s) override {
        if (failWrites)
            return false;
        files[p] = s;
        return true;
    }
};
std::string readFile(const std::filesystem::path &p) {
    std::ifstream f(p, std::ios::binary);
    std::ostringstream s;
    s << f.rdbuf();
    return s.str();
}
// These sessions exercise the portable core, not CTRPF Keyboard or console SD.
void searchSessions(Memory &io, const std::string &pack) {
    const auto index = pack.substr(0, pack.size() - 4) + ".ugs";
    const auto pristine = io.files.at(index);
    std::vector<uint32_t> expected;
    Guide guide(io);
    assert(guide.open(pack));
    assert(guide.search("route", true, expected) && expected.size() > 1);
    for (unsigned session = 0; session < 32; ++session) {
        Guide reopened(io);
        assert(reopened.open(pack));
        std::vector<uint32_t> hits{MaxPages};
        assert(!reopened.search("", true, hits) && hits.empty());
        assert(reopened.search("route", true, hits) && hits == expected);
        assert(reopened.search("zzznothingzzz", true, hits) && hits.empty());
        assert(reopened.search("route", true, hits) && hits == expected);
    } // Destruction is the core equivalent of closing; UI Back is not simulated.
    std::vector<uint32_t> hits = expected;
    io.files.erase(index);
    assert(!guide.search("route", true, hits) && hits.empty());
    io.files[index] = pristine;
    const std::string firstTerm(pristine.data() + 12);
    for (unsigned damage = 0; damage < 5; ++damage) {
        auto malformed = pristine;
        if (damage == 0)
            malformed[0] = 'X';
        if (damage == 1)
            malformed.pop_back();
        if (damage == 2)
            malformed.replace(4, 4, std::string(4, '\xff'));
        if (damage == 3)
            malformed.replace(12, 64, std::string(64, 'a')); // Missing NUL.
        if (damage == 4) {
            std::string invalidPage;
            put32(invalidPage, MaxPages);
            malformed.replace(12 + 64, 4, invalidPage);
        }
        io.files[index] = malformed;
        hits = expected;
        assert(!guide.search(firstTerm, true, hits));
        io.files[index] = pristine;
        assert(guide.search("route", true, hits) && hits == expected);
    }
    std::cout << "Search core sessions: 32 reopen cycles, empty/multiple/no results, "
                 "missing index and five malformed-index cases passed.\n";
}
void configSessions() {
    Memory io;
    const std::string path = "config.bin";
    Config defaults;
    assert(defaults.hotkey == 13 && defaults.language == "pt-BR" && !defaults.spoilers &&
           defaults.touch && !defaults.logging && defaults.remember);
    std::string raw;
    assert(!io.read(path, 0, 32, raw));
    Config missing;
    assert(!missing.decode(raw) && missing.encode() == defaults.encode());
    for (unsigned session = 0; session < 32; ++session) {
        Config changed;
        changed.hotkey = 512 | 256 | 2048; // L + R + Y.
        changed.spoilers = session % 2;
        changed.touch = !(session % 2);
        changed.logging = session % 2;
        changed.remember = !(session % 2);
        assert(io.write(path, changed.encode()));
        assert(io.read(path, 0, 32, raw));
        Config reopened;
        assert(reopened.decode(raw) && reopened.encode() == changed.encode());
        const auto unchanged = reopened.encode();
        auto malformed = raw;
        malformed.back() ^= 1;
        assert(!reopened.decode(malformed) && reopened.encode() == unchanged);
        assert(!reopened.decode(raw.substr(0, 31)) && reopened.encode() == unchanged);
        io.failWrites = true;
        assert(!io.write(path, defaults.encode()) && io.files.at(path) == raw);
        io.failWrites = false;
    }
    std::cout << "Settings core sessions: defaults/missing config, 32 save/reopen cycles, "
                 "malformed config and failed writes passed (Memory storage only).\n";
}
int main(int argc, char **argv) {
    assert(argc == 2);
    std::filesystem::path root = argv[1];
    Memory io;
    for (auto &e : std::filesystem::recursive_directory_iterator(root))
        if (e.is_regular_file())
            io.files[e.path().string()] = readFile(e.path());
    auto path = [&](const std::string &p) { return (root / p).string(); };
    assert(crc32("123456789") == 0xCBF43926);
    assert(validUtf8("Pokémon / ação\n"));
    for (const std::string &bad :
         {std::string("\xc0\xaf"), std::string("\xed\xa0\x80"), std::string("\xf4\x90\x80\x80"),
          std::string("\0", 1), std::string("\xc3")})
        assert(!validUtf8(bad));
    assert(fold("AÇÃO Pokémon ÁÉÍÓÚ Ç") == "acao pokemon aeiou c");
    for (const auto &id : {"../game", "/root", "Upper", "", "game.json"})
        assert(!safeId(id));
    assert(safeId("super-mario-3d-land"));
    Game game;
    auto titles = path("titles.bin");
    assert(lookup(io, titles, 0, game) == Lookup::Unknown);
    for (uint64_t tid : {0x0004000000054000ULL, 0x0004000000053F00ULL, 0x0004000000054100ULL,
                         0x0004000000089D00ULL, 0x0004000000089E00ULL}) {
        assert(lookup(io, titles, tid, game) == Lookup::Found);
        assert(game.id == "super-mario-3d-land");
    }
    std::string original = io.files[titles];
    for (uint32_t i = 0; i < u32(original.data() + 4); ++i) {
        auto off = 8 + i * TitleRecordSize;
        assert(lookup(io, titles, u64(original.data() + off), game) == Lookup::Found);
        assert(game.id == std::string(original.data() + off + 8));
    }
    io.files[titles][0] = 'X';
    assert(lookup(io, titles, 0, game) == Lookup::Corrupt);
    io.files[titles] = original;
    io.files[titles].pop_back();
    assert(lookup(io, titles, 0, game) == Lookup::Corrupt);
    io.files[titles] = original;
    unsigned packs = 0, pages = 0;
    for (auto &e : std::filesystem::directory_iterator(root / "guides/pt-BR"))
        if (e.path().extension() == ".ugg") {
            Guide g(io);
            assert(g.open(e.path().string()));
            ++packs;
            for (uint32_t p = 0; p < g.pages.size(); ++p) {
                std::string text;
                assert(g.text(p, text));
                assert(text.size() <= MaxText);
                ++pages;
            }
            assert(!g.text(MaxPages, original));
        }
    Guide g(io);
    auto pokemon = path("guides/pt-BR/pokemon-x.ugg");
    assert(g.open(pokemon));
    searchSessions(io, pokemon);
    configSessions();
    assert(g.pages.size() > 732 && g.pages.size() <= MaxPages);
    std::string actual;
    assert(g.openLanguage(path("guides"), "pokemon-x", "en-US", actual) && actual == "pt-BR");
    const auto damagedLanguage = path("guides/en-US/pokemon-x.ugg");
    io.files[damagedLanguage] = "corrupt";
    assert(!g.openLanguage(path("guides"), "pokemon-x", "en-US", actual) && actual == "en-US" &&
           g.pages.empty());
    io.files.erase(damagedLanguage);
    assert(!g.openLanguage(path("guides"), "../bad", "pt-BR", actual) && g.pages.empty());
    assert(!g.openLanguage(path("guides"), "missing-game", "pt-BR", actual));
    assert(g.open(pokemon));
    assert(g.fingerprint() == u32(io.files[pokemon].data() + 8));
    std::vector<uint32_t> hits;
    io.reads = 0;
    assert(g.search("ChArIzArD", false, hits));
    assert(!hits.empty());
    assert(io.reads < 40);
    assert(std::any_of(hits.begin(), hits.end(),
                       [&](uint32_t p) { return g.pages[p].id == "dex-006"; }));
    assert(g.search("xerneas", false, hits));
    for (auto p : hits)
        assert(!g.pages[p].flags);
    assert(g.search("xerneas", true, hits));
    assert(std::any_of(hits.begin(), hits.end(),
                       [&](uint32_t p) { return g.pages[p].id == "dex-716"; }));
    assert(g.search("route 2", false, hits) && !hits.empty());
    assert(!g.search("x", false, hits));
    assert(!g.search("é", false, hits));
    assert(g.search("pokédex", false, hits) && !hits.empty());
    assert(g.search("zzznothingzzz", false, hits) && hits.empty());
    auto search = pokemon.substr(0, pokemon.size() - 4) + ".ugs";
    original = io.files[search];
    io.files[search][8] ^= 1;
    assert(!g.search("charizard", true, hits));
    io.files[search] = original;
    original = io.files[pokemon];
    io.files[pokemon].back() ^= 1;
    std::string text;
    assert(!g.text(g.pages.size() - 1, text) && text.empty());
    io.files[pokemon] = original;
    std::mt19937 random(20261004);
    for (unsigned i = 0; i < 100; ++i) {
        io.files[pokemon] = original;
        size_t pos = random() % (12 + g.pages.size() * PageRecordSize);
        io.files[pokemon][pos] ^= 1;
        Guide invalid(io);
        assert(!invalid.open(pokemon));
    }
    io.files[pokemon] = original;
    assert(g.open(pokemon));
    State state;
    state.last = 731;
    state.line = 12;
    state.toggle(false, 732);
    state.toggle(true, 1023);
    auto encoded = state.encode(123);
    assert(encoded.size() == StateSize);
    State decoded;
    assert(decoded.decode(encoded, 123));
    assert(decoded.get(false, 732) && decoded.get(true, 1023));
    assert(decoded.last == 731);
    assert(!decoded.decode(encoded, 124));
    encoded.back() ^= 1;
    assert(!decoded.decode(encoded, 123));
    state.toggle(false, MaxPages);
    assert(!state.get(false, MaxPages));
    Config cfg, copy;
    assert(copy.decode(cfg.encode()) && copy.hotkey == 13 && copy.language == "pt-BR");
    cfg.spoilers = true;
    cfg.language = "en-US";
    assert(copy.decode(cfg.encode()) && copy.spoilers);
    cfg.touch = false;
    cfg.logging = true;
    cfg.remember = false;
    assert(copy.decode(cfg.encode()) && !copy.touch && copy.logging && !copy.remember);
    Config legacy;
    auto oldConfig = legacy.encode();
    oldConfig[3] = '1';
    oldConfig.resize(28);
    put32(oldConfig, crc32(oldConfig));
    assert(copy.decode(oldConfig) && copy.touch && !copy.logging && copy.remember);
    cfg.hotkey = 1;
    assert(!copy.decode(cfg.encode()));
    cfg.hotkey = 512 | 128 | 4;
    assert(!copy.decode(cfg.encode()));
    cfg.hotkey = 1 << 31;
    assert(!copy.decode(cfg.encode()));
    cfg.hotkey = 1 | 16 | 32;
    assert(!copy.decode(cfg.encode()));
    cfg.hotkey = 1 | 64 | 128;
    assert(!copy.decode(cfg.encode()));
    cfg.hotkey = 1 | 16 | 64; // A plus a possible diagonal remains configurable.
    assert(copy.decode(cfg.encode()));
    auto image = path("maps/super-mario-3d-land/world-1-1-1-0-0.ugi");
    Tile tile;
    assert(loadTile(io, image, tile) && tile.width == 320 && tile.height == 192);
    original = io.files[image];
    io.files[image].back() ^= 1;
    assert(!loadTile(io, image, tile));
    io.files[image] = original;
    io.files[image][4] = 0;
    io.files[image][5] = 0;
    assert(!loadTile(io, image, tile));
    assert(io.largest <= 256 * 1024);
    BufferedLog logger;
    const auto before = io.files.size();
    logger.add("off");
    assert(logger.flush(io, "log") && io.files.size() == before);
    logger.enable(true);
    for (unsigned i = 0; i < 100; ++i)
        logger.add("ação event " + std::to_string(i) + std::string(400, 'x'));
    assert(logger.text().size() <= 4096 && validUtf8(logger.text()));
    assert(logger.flush(io, "log") && io.files["log"] == logger.text());
    const auto buffered = logger.text();
    io.failWrites = true;
    assert(!logger.flush(io, "log") && logger.text() == buffered);
    io.failWrites = false;
    logger.enable(false);
    assert(logger.text().empty());
    State oldProgress;
    oldProgress.last = 1;
    oldProgress.line = 3;
    oldProgress.toggle(false, 0);
    oldProgress.toggle(true, 1);
    std::string mapping;
    put32(mapping, 2);
    put32(mapping, 0);
    put32(mapping, UINT32_MAX);
    std::string migration = "UGR1";
    put32(migration, 11);
    put32(migration, 22);
    put32(migration, 3);
    put32(migration, crc32(mapping));
    io.files["migration"] = migration + mapping;
    State migrated;
    assert(migrateState(io, "migration", oldProgress.encode(11), 22, 4, migrated));
    assert(migrated.last == 0 && migrated.line == 3 && migrated.get(false, 2) &&
           migrated.get(true, 0));
    assert(!migrateState(io, "migration", oldProgress.encode(11), 23, 4, migrated));
    io.files["migration"].back() ^= 1;
    assert(!migrateState(io, "migration", oldProgress.encode(11), 22, 4, migrated));
    for (const auto invalidTarget : {2u, 4u}) {
        std::string badMap;
        put32(badMap, 2);
        put32(badMap, invalidTarget); // Duplicate or out of range, with a valid CRC.
        put32(badMap, UINT32_MAX);
        std::string header = migration.substr(0, 16);
        put32(header, crc32(badMap));
        io.files["migration"] = header + badMap;
        const auto unchanged = migrated.encode(22);
        assert(!migrateState(io, "migration", oldProgress.encode(11), 22, 4, migrated));
        assert(migrated.encode(22) == unchanged);
    }
    const auto realMigration = path("guides/pt-BR/pokemon-x.ugr");
    assert(io.files.count(realMigration));
    State originalProgress;
    originalProgress.last = 0;
    originalProgress.toggle(false, 0);
    originalProgress.toggle(true, 731);
    State upgraded;
    assert(migrateState(io, realMigration,
                        originalProgress.encode(u32(io.files[realMigration].data() + 4)),
                        g.fingerprint(), g.pages.size(), upgraded));
    assert(upgraded.get(false, 0) && upgraded.get(true, 731));
    assert(!loadTile(io, "missing", tile));
    std::cout << "Core: " << packs << " packs, " << pages
              << " pages, all Title IDs; lazy search, UTF-8, CRC, state and corrupt-file rejection "
                 "passed. Max single read "
              << io.largest << " bytes.\n";
}
