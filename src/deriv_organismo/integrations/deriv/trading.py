from __future__ import annotations

from deriv_organismo.domain.accounts import AccountContext


class DerivTradingGateway:
    def build_proposal_request(
        self,
        *,
        account: AccountContext,
        symbol: str,
        amount: float,
        contract_type: str = "CALL",
        duration: int = 5,
        duration_unit: str = "m",
        currency: str = "USD",
        basis: str = "stake",
    ) -> dict:
        return {
            "proposal": 1,
            "symbol": symbol,
            "amount": amount,
            "basis": basis,
            "contract_type": contract_type,
            "currency": currency,
            "duration": duration,
            "duration_unit": duration_unit,
            "passthrough": {
                "account_id": account.account_id,
                "tenant_id": account.tenant_id,
                "account_slug": account.account_slug,
                "mode": account.mode,
            },
        }

    def build_buy_request(self, *, proposal_id: str, amount: float) -> dict:
        return {
            "buy": proposal_id,
            "price": amount,
        }

    def request_proposal(self, payload: dict) -> dict:
        proposal_id = payload.get("passthrough", {}).get("account_id", "acc") + "_proposal"
        return {"proposal": {"id": proposal_id, "request": payload}}

    def submit_buy(self, payload: dict) -> dict:
        return {
            "buy": {
                "contract_id": str(payload.get("buy", "contract")) + "_contract",
                "status": "open",
                "request": payload,
            }
        }
