#pragma once
#include <3ds.h>

// Plain BSS, no heap or services needed to record the earliest checkpoints.
extern "C" void UGGBootStage(unsigned stage, const char *label);
extern "C" void UGGBootResult(const char *label, Result result);
extern "C" void UGGBootTitle(u64 title);
extern "C" void UGGBootFsReady(Result result);
extern "C" void UGGBootHeap(int bytes);
extern "C" void UGGBootValue(const char *label, u64 value);
extern "C" const char *UGGBootVariant();
extern "C" Result UGGBootLastWrite();
