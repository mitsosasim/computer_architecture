#include "cpu/pred/PAgPredictor.hh"

#include "base/intmath.hh"
#include "base/logging.hh"
#include "base/trace.hh"
#include "debug/Fetch.hh"
//csd4845 Dimitris Asimakopoulos
namespace gem5
{

namespace branch_prediction
{

PAgPred::PAgPred(const PAgPredParams &params)
    : BPredUnit(params),
    LHT(params.ltableHeight, 0), //initialize LHT to 0
    GPT(params.gtableHeight, SatCounter8(params.gpredSize)), //initialize GPT to 0
    ltableHeight(params.ltableHeight), //number of entries in LHT
    lhistoryWidth(params.lhistoryWidth), //bits of history stored in LHT entries
    gtableHeight(params.gtableHeight), //number of entries in GPT
    gpredSize(params.gpredSize), //counter size in GPT
    ltableMask((1 << params.ltableHeight) - 1), //mask for local history table indexing
    gtableMask((1 << params.gtableHeight) - 1) //mask for global pattern table indexing


{
    if (!isPowerOf2(ltableHeight)) fatal("Invalid local history table size: Must be a power of 2.\n");
    if (!isPowerOf2(gtableHeight)) fatal("Invalid global pattern table size: Must be a power of 2.\n");

    //debug with --debug-flags=Fetch
    DPRINTF(Fetch, "LHT entries: %u, history width: %u\n", ltableHeight, lhistoryWidth);
    DPRINTF(Fetch, "GPT entries: %u, predictor bits: %u\n", gtableHeight, gpredSize);
}

// unused
void
PAgPred::btbUpdate(ThreadID tid, Addr branch_addr, void * &bp_history)
{
// Place holder for a function that is called to update predictor history when
// a BTB entry is invalid or not found.
}

bool
PAgPred::lookup(ThreadID tid, Addr branch_addr, void * &bp_history)
{
    //index into the LHT using branch address
    unsigned local_index = branch_addr & ltableMask;
    uint32_t local_history = LHT[local_index];

    //index into the GPT using the local history
    unsigned global_index = local_history & gtableMask;
    uint8_t counter_value = GPT[global_index];

    //the most significant bit of the counter value is the prediction
    bool prediction = (counter_value >> (gpredSize - 1)) & 1;

    DPRINTF(Fetch, "Lookup: branch address %#x, local history %#x, global index %#x, prediction: %d\n", branch_addr, local_history, global_index, prediction);

    //bp_history = (void *)(uint32_t) local_history; //not needed i think

    return prediction;
}

void
PAgPred::update(ThreadID tid, Addr branch_addr, bool taken, void *bp_history,
                bool squashed, const StaticInstPtr & inst, Addr corrTarget)
{
    // No state to restore, and we do not update on the wrong path.
    if (squashed) {
        DPRINTF(Fetch, "Update skipped due to squash.\n");
        return;
    }

    //index into the LHT using branch address
    unsigned local_index = branch_addr & ltableMask;
    uint32_t local_history = LHT[local_index];

    //index into the GPT using the local history
    unsigned global_index = local_history & gtableMask;

    //update the GPT
    if (taken) {
        GPT[global_index]++; //increment counter if taken
        DPRINTF(Fetch, "Update: branch taken, incrementing counter at global index %#x\n", global_index);
    } else {
        GPT[global_index]--; //decrement counter if not taken
        DPRINTF(Fetch, "Update: branch not taken, decrementing counter at global index %#x\n", global_index);
    }

    //update the local history in the LHT by shifting to the left and adding the new branch outcome to the lsb
    LHT[local_index] = ((local_history << 1) | (taken ? 1 : 0)) & ((1 << lhistoryWidth) - 1);

    DPRINTF(Fetch, "Updated LHT: branch address %#x, new local history %#x\n", branch_addr, LHT[local_index]);
}

// unused
void
PAgPred::uncondBranch(ThreadID tid, Addr pc, void *&bp_history)
{
}

}

}
