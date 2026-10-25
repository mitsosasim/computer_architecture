#include "cpu/pred/GAgPredictor.hh"

#include "base/intmath.hh"
#include "base/logging.hh"
#include "base/trace.hh"
#include "debug/Fetch.hh"

//csd4845 Dimitris Asimakopoulos

namespace gem5 {

namespace branch_prediction {

GAgPred::GAgPred(const GAgPredParams &params)
    : BPredUnit(params),
    GHR(0), //initialize GHR to 0
    PHT(1 << params.historySize, SatCounter8(params.predSize)), //PHT size is 2^historySize
    historySize(params.historySize), //bits of history
    predSize(params.predSize), //counter bits
    indexMask(( 1 << params.historySize) - 1) //ensure the mask is valid for the specified number of history bits by shifting 1 to the left by the number of history bits and subtracting 1 so GHR doesn’t exceed its allocated size (a circular history).
{
    //if (!isPowerOf2(params.historySize)) fatal("Invalid history size!\n"); //not needed i think
    if (params.predSize > 8 || params.predSize < 1) fatal("Invalid predictor size! Must be between 1 and 8.\n");

    //debugging prints
    DPRINTF(Fetch, "Index mask: %#x\n", indexMask);
    DPRINTF(Fetch, "History size: %i\n", historySize);
    DPRINTF(Fetch, "Predictor size: %i\n", predSize);
}

// unused
void GAgPred::btbUpdate(ThreadID tid, Addr branch_addr, void *&bp_history) {
  // Place holder for a function that is called to update predictor history when
  // a BTB entry is invalid or not found.
}

bool GAgPred::lookup(ThreadID tid, Addr branch_addr, void *&bp_history) {
  unsigned index = GHR & indexMask; //extract index from GHR
  uint8_t counter_value = PHT[index]; //get counter value from PHT
  DPRINTF(Fetch, "Looking up global pattern table with index %#x from global history register %#x, returned counter value: %d\n", index, GHR, counter_value); //debug with --debug-flags=Fetch

  bool prediction = counter_value >> (predSize - 1); //get the most significant bit of the counter value for the prediction
  DPRINTF(Fetch, "Prediction: %s\n", prediction ? "TAKEN" : "NOT TAKEN");
  return prediction;
}

void GAgPred::update(ThreadID tid, Addr branch_addr, bool taken,
                     void *bp_history, bool squashed, const StaticInstPtr &inst,
                     Addr corrTarget) {

    // No state to restore, and we do not update on the wrong path.
    if (squashed) {
        DPRINTF(Fetch, "Update skipped due to squash.\n");
        return;
    }
    unsigned index = GHR & indexMask; //extract index from GHR
    DPRINTF(Fetch, "Updating global pattern table with index %#x from global history register %#x\n", index, GHR);

    //update the PHT
    if (taken) {
        PHT[index]++; //increment counter if taken
        DPRINTF(Fetch, "Updated PHT[%#x] as TAKEN. New value: %d\n", index, (int)PHT[index]);
    } else {
        PHT[index]--; //decrement counter if not taken
        DPRINTF(Fetch, "Updated PHT[%#x] as TAKEN. New value: %d\n", index, (int)PHT[index]);
    }

    //update the GHR
    //drop the msb of GHR and add the new branch outcome to the lsb
    GHR = ((GHR << 1) | (taken ? 1 : 0)) & ((1 << historySize) - 1);

    DPRINTF(Fetch, "Updated GHR to %#x\n", GHR);
}



// unused
void GAgPred::uncondBranch(ThreadID tid, Addr pc, void *&bp_history) {}

} // namespace branch_prediction

} // namespace gem5
