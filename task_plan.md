# Task Plan: Forex Agent Optimization & Deployment
> Status: **PLANNING**
> Created on: 2026-01-24

This plan tracks the deep-dive refactoring, optimization, and **deployment** of the Forex Agent system.

## Phase 1: Foundation & Configuration
- [x] **Audit Dependencies**: Check `requirements.txt` and remove unused libs.
- [x] **Setup Pydantic Settings**: Refactor `config.py` to use `BaseSettings` from pydantic.
- [x] **Environment Variables**: Create `.env.template` and ensure all trading params are environment-configurable.
- [ ] **Linting**: Set up `ruff.toml` and run initial lint fix.

## Phase 2: Core Architecture (Refactoring)
- [x] **Interfaces**: `IBroker`, `IDataSource`, `IStrategy` sauber trennen.
- [x] **Broker Refactoring**: `IGBroker` code aufräumen.
- [ ] **Trading Engine**: Logik aus `main_loop.py` in eine saubere Klasse `TradingEngine` verschieben.
- [ ] **Refactor Data**: Ensure `TwelveData` and `IGData` implement `IDataSource`.
- [ ] **Create Trading Engine**: Implement `TradingEngine` class in `execution/engine.py`.
- [ ] **Scheduler**: Create `run_forever.py` to run the engine in a loop with safe error handling.

## Phase 3: Deployment (Passive Server)
- [x] **Dockerize Agent**: Create `Dockerfile.agent` for the trading bot.
- [x] **Orchestrate**: Create `docker-compose.yml` for Agent + Macro Server + DB.
- [x] **Deploy**: Push to GitHub/Railway and verify 24/7 operation.

## Phase 4: Stability & Error Proofing
- [x] **Typed Signals**: Replace string signals with Enums.
- [x] **Unified Logging**: Structured JSON logging.
- [x] **Database Integration**: Write trade results to DB.

## Phase 5: Testing
- [ ] **Unit Tests**: Risk & Strategy logic.
- [ ] **Integration Tests**: Engine loop with MockBroker.
