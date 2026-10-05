/* MIT: own homebrew fixture, not a commercial game or a compatibility claim. */
#include <3ds.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    gfxInitDefault();
    consoleInit(GFX_TOP, NULL);
    unsigned frames = 0;
    while (aptMainLoop()) {
        hidScanInput();
        printf("\x1b[0;0HUGG own homebrew fixture\nFrame: %u\n\n", frames++);
        printf("No commercial game or system files.\nNo save or NAND writes.\n");
        printf("Standard SDK entry: loader may skip it.\n");
        if (frames % 60 == 0) {
            const char *message = "UGG fixture: 60 frames reached\n";
            svcOutputDebugString(message, strlen(message));
        }
        gfxFlushBuffers();
        gfxSwapBuffers();
        gspWaitForVBlank();
    }
    gfxExit();
    return 0;
}
