# 00 Project Context

## Goal
Develop a **Forex Trading Agent** with a pipeline: 
`Strategy` → `Signal` → `Risk` → `Execution` → `Logging`.

## Constraints
- **Broker/API**: OANDA is problematic (no API access for German clients).
- **Status**: Broker and Market Data provider are currently OPEN/UNDECIDED.
- **Location**: User is in Germany/EU (Regulatory constraints apply).

## Working Mode
- **Dynamic & Adaptable**: Start small, iterate fast.
- **Self-Annealing**: The process should evolve based on feedback and results.
